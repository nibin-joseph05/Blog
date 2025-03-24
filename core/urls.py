from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Public URLs
    path('', views.home, name='home'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('search/', views.search_posts, name='search_posts'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # User Interaction URLs
    path('toggle-theme/', views.toggle_theme, name='toggle_theme'),
    path('post/<slug:slug>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/add-comment/', views.add_comment, name='add_comment'),
    
    # Notification URLs
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/count/', views.get_notification_count, name='get_notification_count'),
    
    # Admin Dashboard URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/post/create/', views.create_post, name='create_post'),
    path('admin-dashboard/post/<slug:slug>/edit/', views.edit_post, name='edit_post'),
    path('admin-dashboard/post/<slug:slug>/delete/', views.delete_post, name='delete_post'),
    path('admin-dashboard/comment/<int:comment_id>/approve/', views.approve_comment, name='approve_comment'),
    path('admin-dashboard/comment/<int:comment_id>/reject/', views.reject_comment, name='reject_comment'),
    path('admin-dashboard/user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('profile/', views.profile, name='profile'),
] 