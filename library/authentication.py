"""
Custom authentication backends for the Library Management System
"""

import requests
import logging
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.conf import settings
from .models import User

logger = logging.getLogger(__name__)


class SchoolAPIAuthenticationBackend(BaseBackend):
    """
    Authentication backend that validates users against the school management system API
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user against school management system API
        """
        if not username or not password:
            return None
            
        # Check if this is an ID/PIN combination (school system authentication)
        if self.is_school_id_format(username):
            return self.authenticate_with_school_api(username, password)
        
        return None
    
    def is_school_id_format(self, username):
        """
        Check if the username follows school ID format
        Common formats: STU001, TCH001, ADM001, or numeric IDs
        """
        # Check for alphanumeric school ID patterns
        if len(username) >= 3 and (
            username.upper().startswith(('STU', 'TCH', 'ADM', 'STF')) or
            username.isdigit()
        ):
            return True
        return False
    
    def authenticate_with_school_api(self, school_id, pin):
        """
        Authenticate with school management system API
        """
        try:
            # Get API configuration from settings
            api_url = getattr(settings, 'SCHOOL_API_URL', None)
            api_key = getattr(settings, 'SCHOOL_API_KEY', None)
            
            if not api_url or not api_key:
                logger.warning("School API configuration missing")
                return None
            
            # Prepare API request
            auth_endpoint = f"{api_url.rstrip('/')}/auth/validate"
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'student_id': school_id,
                'pin': pin
            }
            
            # Make API request
            response = requests.post(
                auth_endpoint,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                
                if user_data.get('authenticated', False):
                    # Get or create user based on school data
                    return self.get_or_create_user_from_school_data(user_data)
            
            logger.info(f"School API authentication failed for ID: {school_id}")
            return None
            
        except requests.RequestException as e:
            logger.error(f"School API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"School API authentication error: {e}")
            return None
    
    def get_or_create_user_from_school_data(self, school_data):
        """
        Get or create a user based on school management system data
        """
        try:
            school_id = school_data.get('student_id') or school_data.get('id')
            email = school_data.get('email')
            
            if not school_id:
                return None
            
            # Try to find existing user by school ID or email
            user = None
            
            # First try by enrollment number (school ID)
            if school_id:
                try:
                    user = User.objects.get(enrollment_number=school_id)
                except User.DoesNotExist:
                    pass
            
            # Then try by email if provided
            if not user and email:
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    pass
            
            # Create new user if not found
            if not user:
                user = self.create_user_from_school_data(school_data)
            else:
                # Update existing user with latest school data
                user = self.update_user_from_school_data(user, school_data)
            
            return user
            
        except Exception as e:
            logger.error(f"Error processing school user data: {e}")
            return None
    
    def create_user_from_school_data(self, school_data):
        """
        Create a new user from school management system data
        """
        try:
            school_id = school_data.get('student_id') or school_data.get('id')
            
            # Determine role based on school data
            role = self.determine_user_role(school_data)
            
            # Generate username from school ID
            username = f"school_{school_id}"
            
            # Create user
            user = User.objects.create(
                username=username,
                email=school_data.get('email', f"{school_id}@school.edu"),
                first_name=school_data.get('first_name', ''),
                last_name=school_data.get('last_name', ''),
                role=role,
                enrollment_number=school_id,
                phone_number=school_data.get('phone', ''),
                class_grade=school_data.get('class', ''),
                is_active_member=True,
                # Set a random password since they authenticate via API
                password='!',  # Unusable password
            )
            
            logger.info(f"Created new user from school API: {username}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user from school data: {e}")
            return None
    
    def update_user_from_school_data(self, user, school_data):
        """
        Update existing user with latest school data
        """
        try:
            # Update user fields with latest data from school system
            user.first_name = school_data.get('first_name', user.first_name)
            user.last_name = school_data.get('last_name', user.last_name)
            user.email = school_data.get('email', user.email)
            user.phone_number = school_data.get('phone', user.phone_number)
            user.class_grade = school_data.get('class', user.class_grade)
            
            # Update role if changed
            new_role = self.determine_user_role(school_data)
            if new_role != user.role:
                user.role = new_role
            
            user.save()
            
            logger.info(f"Updated user from school API: {user.username}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user from school data: {e}")
            return user
    
    def determine_user_role(self, school_data):
        """
        Determine user role based on school data
        """
        user_type = school_data.get('type', '').lower()
        school_id = school_data.get('student_id') or school_data.get('id', '')
        
        # Role mapping based on school system data
        if user_type in ['teacher', 'staff', 'faculty'] or school_id.upper().startswith(('TCH', 'STF')):
            return 'teacher'
        elif user_type in ['admin', 'administrator'] or school_id.upper().startswith('ADM'):
            return 'librarian'  # School admins become librarians in library system
        else:
            return 'student'  # Default to student
    
    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class LocalAuthenticationBackend(BaseBackend):
    """
    Enhanced local authentication backend supporting email/ID + PIN login
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user against local database with flexible login formats
        Supports login with:
        - Username + password
        - Email (full or just username part) + password/PIN
        - Student ID (full like STU1001 or just number like 1001) + PIN
        """
        if not username or not password:
            return None

        user = None
        original_username = username.strip()

        # Normalize the username for flexible matching
        normalized_username = original_username.lower()

        # Try different authentication methods
        try:
            # Method 1: Direct username lookup
            user = User.objects.get(username=normalized_username)
        except User.DoesNotExist:
            try:
                # Method 2: Email lookup (full email)
                if '@' in original_username:
                    user = User.objects.get(email__iexact=original_username)
                else:
                    # Method 2b: Email lookup (just username part - add domain)
                    email_to_try = f"{normalized_username}@deigratiams.edu.gh"
                    user = User.objects.get(email__iexact=email_to_try)
            except User.DoesNotExist:
                try:
                    # Method 3: Student ID lookup (exact match)
                    user = User.objects.get(enrollment_number__iexact=original_username)
                except User.DoesNotExist:
                    try:
                        # Method 4: Flexible student ID lookup
                        # Handle cases like: 1001 -> STU1001, stu1001 -> STU1001, etc.
                        if original_username.isdigit():
                            # Just numbers - try with STU prefix
                            student_id_to_try = f"STU{original_username}"
                            user = User.objects.get(enrollment_number__iexact=student_id_to_try)
                        elif normalized_username.startswith('stu'):
                            # Starts with stu - normalize to STU
                            student_id_to_try = f"STU{original_username[3:]}"
                            user = User.objects.get(enrollment_number__iexact=student_id_to_try)
                        elif normalized_username.startswith('tch'):
                            # Teacher ID
                            student_id_to_try = f"TCH{original_username[3:]}"
                            user = User.objects.get(enrollment_number__iexact=student_id_to_try)
                        elif normalized_username.startswith('adm'):
                            # Admin ID
                            student_id_to_try = f"ADM{original_username[3:]}"
                            user = User.objects.get(enrollment_number__iexact=student_id_to_try)
                    except User.DoesNotExist:
                        pass

        # Verify password/PIN and active status
        if user and user.check_password(password) and user.is_active_member:
            return user

        return None

    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
