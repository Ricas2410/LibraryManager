from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import (User, Book, Author, Category, Publisher, Loan, Reservation,
                     LibrarySettings, Section, ShelfLocation, Floor)


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), 
        required=False
    )
    enrollment_number = forms.CharField(max_length=20, required=False)
    class_grade = forms.CharField(max_length=10, required=False)

    # Additional notification email (optional)
    notification_email = forms.EmailField(
        required=False,
        help_text="Optional additional email for notifications (parent, guardian, or secondary contact)"
    )

    role = forms.ChoiceField(choices=User.ROLE_CHOICES, initial='student')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2',
                 'phone_number', 'address', 'date_of_birth', 'enrollment_number',
                 'class_grade', 'notification_email', 'role')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only admins can create admin/librarian accounts
        if user and not user.can_manage_users():
            self.fields['role'].choices = [
                ('teacher', 'Teacher'),
                ('student', 'Student'),
            ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data.get('phone_number')
        user.address = self.cleaned_data.get('address')
        user.date_of_birth = self.cleaned_data.get('date_of_birth')
        user.enrollment_number = self.cleaned_data.get('enrollment_number')
        user.class_grade = self.cleaned_data.get('class_grade')
        user.notification_email = self.cleaned_data.get('notification_email')
        user.role = self.cleaned_data['role']
        
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with enhanced styling and school ID support"""
    username = forms.CharField(
        label='Username / School ID',
        widget=forms.TextInput(attrs={
            'class': 'form-input field-input',
            'placeholder': 'Username, Email, or School ID (e.g., STU001)'
        }),
        help_text='Enter your library username, email, or school ID'
    )
    password = forms.CharField(
        label='Password / PIN',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input field-input',
            'placeholder': 'Password or PIN'
        }),
        help_text='Enter your password or school PIN'
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Try to authenticate with username first
            self.user_cache = authenticate(
                self.request, 
                username=username, 
                password=password
            )
            
            # If that fails, try with email
            if self.user_cache is None:
                try:
                    user = User.objects.get(email=username)
                    self.user_cache = authenticate(
                        self.request,
                        username=user.username,
                        password=password
                    )
                except User.DoesNotExist:
                    pass

            if self.user_cache is None:
                raise forms.ValidationError(
                    "Please enter a correct username/email and password."
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address',
                 'date_of_birth', 'enrollment_number', 'class_grade', 'profile_picture',
                 'notification_email']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class BookForm(forms.ModelForm):
    """Form for adding/editing books"""
    authors = forms.ModelMultipleChoiceField(
        queryset=Author.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    # Autocomplete fields
    publisher_name = forms.CharField(max_length=200, required=False)
    section_name = forms.CharField(max_length=100, required=False)
    shelf_location_code = forms.CharField(max_length=20, required=False)
    floor_name = forms.CharField(max_length=50, required=False)

    class Meta:
        model = Book
        fields = ['title', 'subtitle', 'authors', 'isbn', 'publisher', 'publication_date',
                 'edition', 'pages', 'language', 'categories', 'cover_image',
                 'physical_description', 'shelf_location', 'section', 'floor',
                 'total_copies', 'summary', 'notes', 'price']
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'physical_description': forms.Textarea(attrs={'rows': 3}),
            'summary': forms.Textarea(attrs={'rows': 4}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['authors', 'categories']:
                field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()

        # Validate that at least one author is selected
        authors = cleaned_data.get('authors')
        if not authors:
            raise forms.ValidationError("At least one author must be selected.")

        # Validate that at least one category is selected
        categories = cleaned_data.get('categories')
        if not categories:
            raise forms.ValidationError("At least one category must be selected.")

        # ISBN is now optional and flexible - no validation needed

        # Validate total copies
        total_copies = cleaned_data.get('total_copies')
        if total_copies and total_copies < 1:
            raise forms.ValidationError("Total copies must be at least 1.")

        # Validate pages (optional)
        pages = cleaned_data.get('pages')
        if pages is not None and pages < 1:
            raise forms.ValidationError("Number of pages must be at least 1.")

        # Validate price
        price = cleaned_data.get('price')
        if price and price < 0:
            raise forms.ValidationError("Price cannot be negative.")

        return cleaned_data

    def save(self, commit=True):
        book = super().save(commit=False)

        # Handle autocomplete fields
        self._handle_publisher()
        self._handle_section()
        self._handle_shelf_location()
        self._handle_floor()

        if not book.available_copies:
            book.available_copies = book.total_copies
        if commit:
            book.save()
            self.save_m2m()
        return book

    def _handle_publisher(self):
        """Handle publisher autocomplete field"""
        publisher_id = self.data.get('publisher')
        publisher_name = self.data.get('publisher_name', '').strip()

        if publisher_id:
            try:
                self.instance.publisher = Publisher.objects.get(id=publisher_id)
            except Publisher.DoesNotExist:
                pass
        elif publisher_name:
            # Create new publisher
            publisher, created = Publisher.objects.get_or_create(
                name=publisher_name,
                defaults={'name': publisher_name}
            )
            self.instance.publisher = publisher

    def _handle_section(self):
        """Handle section autocomplete field"""
        section_id = self.data.get('section')
        section_name = self.data.get('section_name', '').strip()

        if section_id:
            try:
                self.instance.section = Section.objects.get(id=section_id)
            except Section.DoesNotExist:
                pass
        elif section_name:
            # Create new section
            section, created = Section.objects.get_or_create(
                name=section_name,
                defaults={'name': section_name, 'floor': 'Ground Floor'}
            )
            self.instance.section = section

    def _handle_shelf_location(self):
        """Handle shelf location autocomplete field"""
        shelf_id = self.data.get('shelf_location')
        shelf_code = self.data.get('shelf_location_code', '').strip()

        if shelf_id:
            try:
                self.instance.shelf_location = ShelfLocation.objects.get(id=shelf_id)
            except ShelfLocation.DoesNotExist:
                pass
        elif shelf_code and self.instance.section:
            # Create new shelf location
            shelf, created = ShelfLocation.objects.get_or_create(
                code=shelf_code,
                defaults={'code': shelf_code, 'section': self.instance.section, 'capacity': 50}
            )
            self.instance.shelf_location = shelf

    def _handle_floor(self):
        """Handle floor autocomplete field"""
        floor_id = self.data.get('floor')
        floor_name = self.data.get('floor_name', '').strip()

        if floor_id:
            try:
                self.instance.floor = Floor.objects.get(id=floor_id)
            except Floor.DoesNotExist:
                pass
        elif floor_name:
            # Create new floor
            floor, created = Floor.objects.get_or_create(
                name=floor_name,
                defaults={'name': floor_name}
            )
            self.instance.floor = floor


class BookSearchForm(forms.Form):
    """Form for searching books"""
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title, author, ISBN...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Book.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    section = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Section'
        })
    )


class LoanForm(forms.ModelForm):
    """Form for issuing loans"""
    class Meta:
        model = Loan
        fields = ['book', 'borrower', 'due_date', 'notes']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available books
        self.fields['book'].queryset = Book.objects.filter(
            status='available', 
            available_copies__gt=0
        )
        # Only show users who can borrow books
        self.fields['borrower'].queryset = User.objects.filter(
            role__in=['student', 'teacher'],
            is_active_member=True
        )
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ReservationForm(forms.ModelForm):
    """Form for making reservations"""
    class Meta:
        model = Reservation
        fields = ['book', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show books that are not available
        self.fields['book'].queryset = Book.objects.filter(available_copies=0)
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_book(self):
        book = self.cleaned_data['book']
        user = self.instance.user if hasattr(self.instance, 'user') else None
        
        if user and Reservation.objects.filter(
            book=book, 
            user=user, 
            status='active'
        ).exists():
            raise forms.ValidationError("You already have an active reservation for this book.")
        
        return book


class LibrarySettingsForm(forms.ModelForm):
    """Form for library settings"""
    logo = forms.ImageField(required=False, help_text="Upload library logo")

    class Meta:
        model = LibrarySettings
        fields = [
            'library_name', 'library_address', 'library_phone', 'library_email',
            'default_loan_period', 'max_renewals', 'max_books_per_user',
            'daily_fine_rate', 'max_fine_amount',
            'reservation_expiry_days', 'max_reservations_per_user',
            'is_active'
        ]
        widgets = {
            'library_name': forms.TextInput(attrs={
                'class': 'block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'placeholder': 'Library Name'
            }),
            'library_address': forms.Textarea(attrs={
                'class': 'block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'rows': 3,
                'placeholder': 'Library Address'
            }),
            'library_phone': forms.TextInput(attrs={
                'class': 'block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'placeholder': '+1 (555) 123-4567'
            }),
            'library_email': forms.EmailInput(attrs={
                'class': 'block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'placeholder': 'library@school.edu'
            }),
            'default_loan_period': forms.NumberInput(attrs={
                'class': 'block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'min': 1
            }),
            'max_renewals': forms.NumberInput(attrs={
                'class': 'block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'min': 0
            }),
            'max_books_per_user': forms.NumberInput(attrs={
                'class': 'block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'min': 1
            }),
            'daily_fine_rate': forms.NumberInput(attrs={
                'class': 'block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'step': '0.01',
                'min': 0
            }),
            'max_fine_amount': forms.NumberInput(attrs={
                'class': 'block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'step': '0.01',
                'min': 0
            }),
            'reservation_expiry_days': forms.NumberInput(attrs={
                'class': 'block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'min': 1
            }),
            'max_reservations_per_user': forms.NumberInput(attrs={
                'class': 'block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm',
                'min': 1
            }),
        }
