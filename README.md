# Django Blog

A modern, feature-rich blog platform built with Django and Bootstrap. This blog includes a fully functional admin panel, rich text editing, image uploads, and a clean, responsive design.

## Features

- Responsive design using Bootstrap 5
- Rich text editing with CKEditor
- Image upload support
- Category-based post organization
- Comment system with moderation
- Search functionality
- Pagination
- SEO-friendly URLs
- Custom error pages
- Mobile-friendly layout

## Requirements

- Python 3.8+
- Django 5.0.3
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd blog
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py makemigrations
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

The blog will be available at http://127.0.0.1:8000/

## Admin Interface

Access the admin interface at http://127.0.0.1:8000/admin/
- Manage posts, categories, and comments
- Rich text editor for post content
- Image upload support
- Comment moderation

## Project Structure

```
blog/
├── core/                   # Main blog app
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── urls.py            # URL patterns
│   └── templates/         # HTML templates
├── static/                # Static files
├── media/                 # Uploaded media files
└── blog/                  # Project settings
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 