# Django Blog Project

A modern, feature-rich blog platform built with Django that supports user authentication, post management, comments, likes, and notifications.

## Features

### User Management
- User registration and authentication
- Email-based login system
- User profiles with theme preferences
- Admin dashboard for site management

### Blog Posts
- Create, edit, and delete blog posts
- Categorize posts
- View post details with related posts
- Track post views
- Search functionality

### Comments and Interactions
- Comment on blog posts
- Like/unlike posts
- Real-time comment updates using AJAX
- Comment moderation system

### Notifications
- Real-time notifications for:
  - New comments on posts
  - Comment approvals/rejections
  - Post likes
- Mark notifications as read
- Unread notification counter

### Admin Features
- Dashboard with statistics
- Post management
- Comment moderation
- User management
- Category management

## Technical Stack

- **Backend**: Django 4.2
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (default)
- **Authentication**: Django's built-in authentication system
- **AJAX**: For real-time interactions

## Project Structure

```
blog/
├── core/                    # Main application
│   ├── migrations/         # Database migrations
│   ├── static/            # Static files (CSS, JS, images)
│   ├── templates/         # HTML templates
│   ├── admin.py           # Admin configuration
│   ├── apps.py            # App configuration
│   ├── models.py          # Database models
│   ├── urls.py            # URL routing
│   └── views.py           # View functions
├── blog/                   # Project settings
│   ├── settings.py        # Project settings
│   ├── urls.py            # Main URL routing
│   └── wsgi.py            # WSGI configuration
├── manage.py              # Django management script
└── requirements.txt       # Project dependencies
```

## Models

### Post
- Title and content
- Author (User)
- Category
- Creation date
- Views counter
- Likes (Many-to-Many with User)

### Comment
- Content
- Author (User)
- Post (ForeignKey)
- Creation date

### Category
- Name and slug
- Description

### Notification
- Recipient and sender (User)
- Message
- Link to related content
- Read status
- Creation date

### UserProfile
- User (One-to-One)
- Theme preference

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd blog
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Usage

### Admin Access
- Login with admin credentials at `/admin/`
- Access the admin dashboard at `/admin-dashboard/`
- Manage posts, comments, users, and categories

### User Features
- Register at `/register/`
- Login at `/login/`
- View notifications at `/notifications/`
- Like posts and comment on them
- Toggle between light and dark themes

### Blog Features
- View posts on the home page
- Search posts using the search bar
- Filter posts by category
- View post details and related posts

## API Endpoints

### Authentication
- `POST /register/` - User registration
- `POST /login/` - User login
- `POST /logout/` - User logout

### Posts
- `GET /` - Home page with posts
- `GET /post/<slug>/` - Post detail
- `POST /post/<slug>/delete/` - Delete post (admin only)
- `POST /post/<id>/like/` - Toggle post like

### Comments
- `POST /post/<id>/comment/` - Add comment
- `POST /comment/<id>/approve/` - Approve comment (admin only)
- `POST /comment/<id>/reject/` - Reject comment (admin only)

### Notifications
- `GET /notifications/` - View notifications
- `POST /notification/<id>/read/` - Mark notification as read
- `GET /notification-count/` - Get unread notification count

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 