# School Management System API Integration

This document explains how to integrate the Library Management System with your school's existing management system API for seamless student/staff authentication.

## Overview

The library system now supports multiple authentication methods:
1. **Local Library Accounts** - Traditional username/password authentication
2. **School API Authentication** - Students and staff can login using their school ID and PIN
3. **Email Authentication** - Users can login with their email address

## Configuration

### 1. Environment Variables

Add the following variables to your `.env` file:

```bash
# School Management System API Configuration
SCHOOL_API_URL=https://your-school-api.com/api/v1
SCHOOL_API_KEY=your-school-api-key-here
```

### 2. School API Requirements

Your school management system API should provide an authentication endpoint that:

- **Endpoint**: `POST {SCHOOL_API_URL}/auth/validate`
- **Authentication**: Bearer token using `SCHOOL_API_KEY`
- **Content-Type**: `application/json`

#### Request Format
```json
{
  "student_id": "STU001",
  "pin": "1234"
}
```

#### Response Format (Success)
```json
{
  "authenticated": true,
  "student_id": "STU001",
  "id": "STU001",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@school.edu",
  "phone": "+1234567890",
  "class": "Grade 10A",
  "type": "student"
}
```

#### Response Format (Failure)
```json
{
  "authenticated": false,
  "error": "Invalid credentials"
}
```

### 3. Supported User Types

The system automatically maps school user types to library roles:

| School Type | Library Role | School ID Format |
|-------------|--------------|------------------|
| `student`   | `student`    | STU001, STU002, etc. |
| `teacher`   | `teacher`    | TCH001, TCH002, etc. |
| `staff`     | `teacher`    | STF001, STF002, etc. |
| `admin`     | `librarian`  | ADM001, ADM002, etc. |

## How It Works

### 1. Authentication Flow

1. User enters their school ID (e.g., STU001) and PIN on the login page
2. System detects the school ID format and routes to school API authentication
3. API request is made to your school system
4. If authenticated, user data is retrieved and a local user account is created/updated
5. User is logged into the library system

### 2. User Account Management

- **First Login**: A new library user account is automatically created
- **Subsequent Logins**: Existing account is updated with latest school data
- **Data Sync**: User information is kept in sync with the school system

### 3. School ID Formats

The system recognizes these school ID patterns:
- **Students**: STU001, STU002, STUDENT001, etc.
- **Teachers**: TCH001, TCH002, TEACHER001, etc.
- **Staff**: STF001, STF002, STAFF001, etc.
- **Admins**: ADM001, ADM002, ADMIN001, etc.
- **Numeric IDs**: 12345, 67890, etc.

## Implementation Examples

### Example School API Endpoint

```python
# Example Flask endpoint for school system
@app.route('/api/v1/auth/validate', methods=['POST'])
def validate_user():
    data = request.get_json()
    student_id = data.get('student_id')
    pin = data.get('pin')
    
    # Validate against your school database
    user = validate_credentials(student_id, pin)
    
    if user:
        return jsonify({
            'authenticated': True,
            'student_id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': user.phone,
            'class': user.class_name,
            'type': user.user_type
        })
    else:
        return jsonify({
            'authenticated': False,
            'error': 'Invalid credentials'
        }), 401
```

### Example School Database Schema

```sql
-- Example user table in school system
CREATE TABLE school_users (
    id VARCHAR(20) PRIMARY KEY,  -- STU001, TCH001, etc.
    pin VARCHAR(10) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    class_name VARCHAR(50),
    user_type ENUM('student', 'teacher', 'staff', 'admin'),
    is_active BOOLEAN DEFAULT TRUE
);
```

## Testing

### 1. Test with Demo Data

You can test the integration with these demo credentials:
- **Student**: ID: `STU001`, PIN: `1234`
- **Teacher**: ID: `TCH001`, PIN: `5678`
- **Admin**: ID: `ADM001`, PIN: `9999`

### 2. API Testing

Test your school API endpoint:

```bash
curl -X POST https://your-school-api.com/api/v1/auth/validate \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"student_id": "STU001", "pin": "1234"}'
```

## Security Considerations

1. **API Key Security**: Store your school API key securely in environment variables
2. **HTTPS Only**: Ensure all API communications use HTTPS
3. **Rate Limiting**: Implement rate limiting on your school API
4. **PIN Security**: School PINs should be hashed in your school database
5. **Data Privacy**: Only share necessary user data with the library system

## Troubleshooting

### Common Issues

1. **Authentication Fails**
   - Check API URL and key configuration
   - Verify school API is accessible
   - Check API response format

2. **User Not Created**
   - Check user data format in API response
   - Verify required fields are present
   - Check Django logs for errors

3. **Role Mapping Issues**
   - Verify user type mapping in authentication backend
   - Check school ID format recognition

### Logging

Check the library system logs for authentication details:

```bash
tail -f library.log
```

## Support

For integration support:
1. Check the Django admin logs
2. Review the authentication backend code in `library/authentication.py`
3. Test API endpoints manually
4. Contact your system administrator

## Future Enhancements

Planned features:
- Real-time user data synchronization
- Bulk user import from school system
- Advanced role mapping configuration
- SSO (Single Sign-On) integration
- Multi-school support
