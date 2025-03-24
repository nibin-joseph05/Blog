from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    theme_preference = models.CharField(max_length=10, choices=[('light', 'Light'), ('dark', 'Dark')], default='light')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['-created_at']

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def like_count(self):
        return self.likes.count()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Create notification for post author
        if self.post.author != self.author:
            Notification.objects.create(
                recipient=self.post.author,
                sender=self.author,
                notification_type='comment',
                message=f'{self.author.get_full_name() or self.author.username} commented on your post "{self.post.title}"',
                link=self.post.slug
            )

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('comment', 'New Comment'),
        ('like', 'New Like'),
        ('reply', 'New Reply'),
        ('post', 'New Post'),
        ('comment_approved', 'Comment Approved'),
        ('comment_rejected', 'Comment Rejected'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=50)
    message = models.TextField()
    link = models.CharField(max_length=255, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} - {self.recipient.username}"

    def get_url(self):
        """Convert the stored link to a proper URL."""
        if not self.link:
            return '#'
        
        try:
            # Split the link into namespace:name:slug
            parts = self.link.split(':')
            if len(parts) == 3:
                namespace, name, slug = parts
                return reverse(f'{namespace}:{name}', kwargs={'slug': slug})
        except:
            pass
        
        return '#'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created and instance.author != instance.post.author:
        Notification.objects.create(
            recipient=instance.post.author,
            sender=instance.author,
            notification_type='comment',
            message=f"{instance.author.get_full_name() or instance.author.username} commented on your post '{instance.post.title}'",
            link=instance.post.slug
        )

@receiver(post_save, sender=Post)
def create_post_notification(sender, instance, created, **kwargs):
    if created:
        # Notify all users about new post
        for user in User.objects.exclude(id=instance.author.id):
            Notification.objects.create(
                recipient=user,
                sender=instance.author,
                notification_type='post',
                message=f"New post published: '{instance.title}'",
                link=instance.slug
            )

@receiver(post_save, sender=Post)
def create_like_notification(sender, instance, **kwargs):
    if instance.likes.exists():
        for user in instance.likes.all():
            if user != instance.author:
                Notification.objects.create(
                    recipient=instance.author,
                    sender=user,
                    notification_type='like',
                    message=f"{user.get_full_name() or user.username} liked your post '{instance.title}'",
                    link=instance.slug
                )
