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
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
import random
import string

def is_admin(user):
    return user.email == 'admin@gmail.com'

def ensure_user_profile(user):
    """Ensure that a UserProfile exists for the given user."""
    profile, created = UserProfile.objects.get_or_create(user=user)
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
            profile = ensure_user_profile(user)
            
            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
                profile.save()
            
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
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.theme_preference = theme
        profile.save()
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

@require_POST
def add_comment(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'Please login to comment',
            'redirect_url': reverse('core:login') + f'?next={request.path}'
        }, status=401)
        
    post = get_object_or_404(Post, id=post_id)
    content = request.POST.get('content')
    
    if content:
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content
        )
        
        # Create notification for post owner
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type='comment',
                message=f"{request.user.username} commented on your post '{post.title}'",
                link=post.slug
            )
        
        return JsonResponse({
            'status': 'success',
            'username': request.user.get_full_name() or request.user.username,
            'content': content
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Comment content is required'
    }, status=400)

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

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()

        # Get or create profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.bio = request.POST.get('bio')
        profile.theme_preference = request.POST.get('theme')
        
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('core:profile')
    
    return render(request, 'core/auth/edit_profile.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate OTP
            otp = ''.join(random.choices(string.digits, k=6))
            # Store OTP in session
            request.session['reset_otp'] = otp
            request.session['reset_email'] = email
            # Store expiry time as ISO format string
            request.session['otp_expiry'] = (timezone.now() + timezone.timedelta(minutes=10)).isoformat()
            
            # Send OTP via email
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is: {otp}. This OTP will expire in 10 minutes.',
                'nibinjoseph2003@gmail.com',
                [email],
                fail_silently=False,
            )
            messages.success(request, 'OTP has been sent to your email.')
            return redirect('core:verify_otp')
        except User.DoesNotExist:
            messages.error(request, 'No user found with this email address.')
    
    return render(request, 'core/auth/forgot_password.html')

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        stored_otp = request.session.get('reset_otp')
        expiry_str = request.session.get('otp_expiry')
        
        if not stored_otp or not expiry_str:
            messages.error(request, 'OTP session expired. Please request a new OTP.')
            return redirect('core:forgot_password')
        
        # Convert string back to datetime
        expiry = timezone.datetime.fromisoformat(expiry_str)
        if timezone.now() > expiry:
            messages.error(request, 'OTP has expired. Please request a new OTP.')
            return redirect('core:forgot_password')
        
        if otp == stored_otp:
            return redirect('core:reset_password')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    
    return render(request, 'core/auth/verify_otp.html')

def reset_password(request):
    if request.method == 'POST':
        email = request.session.get('reset_email')
        if not email:
            messages.error(request, 'Session expired. Please try again.')
            return redirect('core:forgot_password')
        
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'core/auth/reset_password.html')
        
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            # Clear session data
            del request.session['reset_otp']
            del request.session['reset_email']
            del request.session['otp_expiry']
            
            messages.success(request, 'Password has been reset successfully. Please login with your new password.')
            return redirect('core:login')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('core:forgot_password')
    
    return render(request, 'core/auth/reset_password.html')

@login_required
def profile(request):
    # Get or create profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get user's posts
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    
    # Get user's comments
    user_comments = Comment.objects.filter(author=request.user).order_by('-created_at')
    
    # Get user's liked posts
    liked_posts = Post.objects.filter(likes=request.user).order_by('-created_at')
    
    context = {
        'user_posts': user_posts,
        'user_comments': user_comments,
        'liked_posts': liked_posts,
    }
    return render(request, 'core/auth/profile.html', context)

@login_required
@require_POST
def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
        # Create notification for post owner
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type='like',
                message=f"{request.user.username} liked your post '{post.title}'",
                link=post.slug
            )
    
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes.count()
    })
