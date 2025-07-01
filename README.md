# LibraryPro - Professional Library Management System

A comprehensive, professional-grade library management system built with Django, featuring modern UI/UX, advanced search capabilities, reporting, and multi-user support.

## 🌟 Features

### Core Functionality
- **Book Management**: Add, edit, delete, and track books with detailed metadata
- **User Management**: Role-based access control (Admin, Librarian, Teacher, Student)
- **Loan Management**: Issue, return, renew books with automatic fine calculation
- **Reservation System**: Book reservation queue with priority management
- **Advanced Search**: Multi-criteria search across books, users, and loans

### Professional Features
- **Modern Sidebar Navigation**: Clean, responsive interface with professional styling
- **CSV User Import**: Bulk import users from CSV files with validation
- **School System API Integration**: Sync users from external school management systems
- **Comprehensive Reporting**: Analytics dashboard with charts and export capabilities
- **Email Notifications**: Automated reminders for due dates and overdue books
- **Library Settings**: Configurable policies, contact info, and logo upload

### User Roles & Permissions
- **Admin**: Full system access, user management, settings configuration
- **Librarian**: Book and loan management, user assistance
- **Teacher/Student**: Book browsing, reservations, profile management

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LMS
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open http://127.0.0.1:8000 in your browser
   - Login with your superuser credentials

## 📚 Usage Guide

### Initial Setup

1. **Configure Library Settings**
   - Navigate to Settings → Library Settings
   - Set library name, contact information, and policies
   - Upload library logo (optional)
   - Configure loan periods, fine rates, and limits

2. **Add Authors and Categories**
   - Go to Django Admin (/admin/)
   - Add authors and book categories
   - Add publishers (optional)

3. **Import Users**
   - Use User Management → CSV Import for bulk user creation
   - Or add users individually
   - Configure API integration for school systems

### Daily Operations

#### Book Management
- **Add Books**: Use the professional book form with all metadata fields
- **Search Books**: Advanced search with filters by category, status, location
- **Track Inventory**: Monitor available copies and book status

#### Loan Management
- **Issue Loans**: Quick loan creation with availability checking
- **Return Books**: Simple return process with fine calculation
- **Manage Overdue**: Automated overdue detection and notifications

#### User Management
- **Add Users**: Individual or bulk import via CSV
- **Manage Roles**: Assign appropriate permissions
- **Track Activity**: View user loan history and statistics

### Email Notifications

Set up automated email reminders:

```bash
# Send due date reminders (run daily)
python manage.py send_due_date_reminders

# Send overdue notifications (run daily)
python manage.py send_overdue_notifications

# Dry run to test
python manage.py send_due_date_reminders --dry-run
```

### CSV Import Format

For bulk user import, use this CSV format:

```csv
username,email,first_name,last_name,role,phone_number,date_of_birth,address,enrollment_number,class_grade
john.doe,john@school.edu,John,Doe,student,+1-555-0123,2005-01-15,"123 Main St",STU001,10A
jane.smith,jane@school.edu,Jane,Smith,teacher,+1-555-0124,1985-03-20,"456 Oak Ave",TCH001,
```

## 🔧 Configuration

### Email Settings

Configure email in `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'Library System <your-email@gmail.com>'
```

### Media Files

Configure media settings for file uploads:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## 📊 Reports & Analytics

The system provides comprehensive reporting:

- **Dashboard Overview**: Key metrics and recent activity
- **Book Statistics**: Most popular books, category distribution
- **User Analytics**: Active users, borrowing patterns
- **Loan Reports**: Current loans, overdue items, return rates
- **Export Options**: PDF and Excel export for all reports

## 🔐 Security Features

- **Role-based Access Control**: Granular permissions by user role
- **Audit Logging**: Track all system activities
- **Input Validation**: Comprehensive form validation and sanitization
- **CSRF Protection**: Built-in Django security features

## 🛠️ Development

### Project Structure
```
LMS/
├── library/                 # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View logic
│   ├── forms.py            # Form definitions
│   ├── urls.py             # URL routing
│   ├── templatetags/       # Custom template filters
│   └── management/         # Management commands
├── templates/              # HTML templates
│   ├── base.html          # Base template with sidebar
│   └── library/           # App-specific templates
├── static/                # Static files (CSS, JS, images)
├── media/                 # User uploads
└── requirements.txt       # Python dependencies
```

### Key Models
- **User**: Extended user model with roles and library-specific fields
- **Book**: Comprehensive book model with metadata and availability
- **Loan**: Loan tracking with dates, status, and fine calculation
- **Reservation**: Book reservation queue system
- **LibrarySettings**: Configurable library policies and settings

### Custom Management Commands
- `send_due_date_reminders`: Email reminders for upcoming due dates
- `send_overdue_notifications`: Email notifications for overdue books

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation
- Review the code comments
- Create an issue on GitHub

## 🔄 Updates & Maintenance

### Regular Tasks
- Run email notification commands daily
- Monitor system logs
- Update library settings as needed
- Backup database regularly

### Recommended Cron Jobs
```bash
# Daily at 9 AM - Send due date reminders
0 9 * * * /path/to/venv/bin/python /path/to/manage.py send_due_date_reminders

# Daily at 10 AM - Send overdue notifications  
0 10 * * * /path/to/venv/bin/python /path/to/manage.py send_overdue_notifications
```

---

**LibraryPro** - Making library management professional, efficient, and user-friendly.
