from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Post, Category, Comment, UserProfile, Notification
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.utils import timezone

def is_admin(user):
    return user.email == 'admin@gmail.com'

def ensure_user_profile(user):
    """Ensure that a UserProfile exists for the given user."""
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    return profile

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('core:register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('core:register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('core:register')

        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)
            ensure_user_profile(user)
            
        messages.success(request, 'Registration successful! Please login.')
        return redirect('core:login')

    return render(request, 'core/auth/register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password!')
            return redirect('core:login')
        
        user = authenticate(username=user.username, password=password)
        
        if user is not None:
            # Ensure UserProfile exists before login
            ensure_user_profile(user)
            login(request, user)
            messages.success(request, 'Login successful!')
            
            if user.email == 'admin@gmail.com':
                return redirect('core:admin_dashboard')
            return redirect('core:home')
        else:
            messages.error(request, 'Invalid email or password!')
    
    return render(request, 'core/auth/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('core:home')

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('core:home')
    
    # Get statistics
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()
    total_users = User.objects.count()
    
    # Get recent posts
    recent_posts = Post.objects.all().order_by('-created_at')[:5]
    
    # Get recent comments
    recent_comments = Comment.objects.all().order_by('-created_at')[:5]
    
    context = {
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_users': total_users,
        'recent_posts': recent_posts,
        'recent_comments': recent_comments,
    }
    return render(request, 'core/auth/admin_dashboard.html', context)

def home(request):
    posts = Post.objects.all()
    featured_posts = posts.order_by('-created_at')[:3]
    paginator = Paginator(posts, 6)  # Show 6 posts per page
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    categories = Category.objects.all()
    
    context = {
        'posts': posts,
        'featured_posts': featured_posts,
        'categories': categories,
    }
    return render(request, 'core/home.html', context)

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.views += 1
    post.save()
    
    # Get all comments for the post
    comments = post.comments.all().order_by('-created_at')
    
    # Get related posts
    related_posts = Post.objects.filter(category=post.category).exclude(id=post.id)[:3]
    
    # Get all categories for sidebar
    categories = Category.objects.all()
    
    context = {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
        'categories': categories,
    }
    return render(request, 'core/post_detail.html', context)

def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category)
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'core/category_posts.html', context)

def search_posts(request):
    query = request.GET.get('q')
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )
    else:
        posts = Post.objects.all()
    
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {
        'posts': posts,
        'query': query,
    }
    return render(request, 'core/search_results.html', context)

@login_required
@require_POST
def toggle_theme(request):
    theme = request.POST.get('theme')
    if theme in ['light', 'dark']:
        request.user.userprofile.theme_preference = theme
        request.user.userprofile.save()
        return JsonResponse({'status': 'success', 'theme': theme})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'status': 'success',
        'liked': liked,
        'like_count': post.like_count()
    })

@login_required
@user_passes_test(is_admin)
@require_POST
def approve_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.is_approved = True
    comment.save()
    
    # Create notification for the comment author
    Notification.objects.create(
        recipient=comment.author,
        sender=request.user,
        notification_type='comment_approved',
        message=f'Your comment on "{comment.post.title}" has been approved.',
        link=comment.post.slug
    )
    
    return JsonResponse({'status': 'success'})

@login_required
@user_passes_test(is_admin)
@require_POST
def reject_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_slug = comment.post.slug  # Store the slug before deleting
    comment.delete()
    
    # Create notification for the comment author
    Notification.objects.create(
        recipient=comment.author,
        sender=request.user,
        notification_type='comment_rejected',
        message=f'Your comment on "{comment.post.title}" has been rejected.',
        link=post_slug
    )
    
    return JsonResponse({'status': 'success'})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            comment = Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            
            # Return the new comment HTML for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('core/includes/comment.html', {
                    'comment': comment
                }, request=request)
                return JsonResponse({
                    'status': 'success',
                    'html': html
                })
            
            messages.success(request, 'Your comment has been added.')
        else:
            messages.error(request, 'Please provide a comment.')
    
    return redirect('core:post_detail', slug=post.slug)

@login_required
def notifications(request):
    notifications = request.user.notifications.all()
    unread_count = notifications.filter(is_read=False).count()
    
    if request.method == 'POST' and request.POST.get('action') == 'mark_all_read':
        notifications.filter(is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('core:notifications')
    
    # Clean up old notification links and prepare context
    processed_notifications = []
    for notification in notifications:
        if notification.link:
            try:
                # Handle old format (core:post_detail:slug)
                if ':' in notification.link:
                    parts = notification.link.split(':')
                    if len(parts) >= 3 and parts[1] == 'post_detail':
                        slug = parts[2]
                        # Verify the slug exists in Post model
                        if Post.objects.filter(slug=slug).exists():
                            notification.link = slug
                            notification.save()
                            processed_notifications.append(notification)
                    else:
                        notification.link = None
                        notification.save()
                else:
                    # Handle new format (just the slug)
                    if Post.objects.filter(slug=notification.link).exists():
                        processed_notifications.append(notification)
                    else:
                        notification.link = None
                        notification.save()
            except Exception:
                notification.link = None
                notification.save()
    
    context = {
        'notifications': processed_notifications,
        'unread_notifications_count': unread_count,
    }
    return render(request, 'core/notifications.html', context)

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

@login_required
def get_notification_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})

@login_required
@user_passes_test(is_admin)
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        
        if title and content and category_id:
            category = get_object_or_404(Category, id=category_id)
            post = Post.objects.create(
                title=title,
                content=content,
                category=category,
                author=request.user
            )
            messages.success(request, 'Post created successfully!')
            return redirect('core:post_detail', slug=post.slug)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'core/auth/create_post.html', context)

@login_required
@user_passes_test(is_admin)
def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        
        if title and content and category_id:
            category = get_object_or_404(Category, id=category_id)
            post.title = title
            post.content = content
            post.category = category
            post.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('core:post_detail', slug=post.slug)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    categories = Category.objects.all()
    context = {
        'post': post,
        'categories': categories,
    }
    return render(request, 'core/auth/edit_post.html', context)

@login_required
@user_passes_test(is_admin)
@require_POST
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.delete()
    return JsonResponse({'status': 'success'})

@login_required
@user_passes_test(is_admin)
@require_POST
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.email != 'admin@gmail.com':  # Prevent deleting admin
        user.delete()
    return JsonResponse({'status': 'success'})
