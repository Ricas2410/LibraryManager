from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from library.models import Author, Category, Publisher, Book, LibrarySettings
from datetime import date
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create library settings
        settings, created = LibrarySettings.objects.get_or_create(
            pk=1,
            defaults={
                'library_name': 'School Library',
                'library_address': '123 Education Street, Learning City',
                'library_phone': '+1-555-0123',
                'library_email': 'library@school.edu',
                'default_loan_period': 14,
                'max_renewals': 3,
                'max_books_per_user': 5,
                'daily_fine_rate': 1.00,
                'max_fine_amount': 50.00,
                'reservation_expiry_days': 7,
                'max_reservations_per_user': 3,
            }
        )
        if created:
            self.stdout.write('✓ Library settings created')
        
        # Create sample users
        users_data = [
            {'username': 'librarian1', 'email': 'librarian@school.edu', 'first_name': 'Jane', 'last_name': 'Smith', 'role': 'librarian'},
            {'username': 'teacher1', 'email': 'teacher1@school.edu', 'first_name': 'John', 'last_name': 'Doe', 'role': 'teacher'},
            {'username': 'student1', 'email': 'student1@school.edu', 'first_name': 'Alice', 'last_name': 'Johnson', 'role': 'student', 'enrollment_number': 'STU001', 'class_grade': '10A'},
            {'username': 'student2', 'email': 'student2@school.edu', 'first_name': 'Bob', 'last_name': 'Wilson', 'role': 'student', 'enrollment_number': 'STU002', 'class_grade': '10B'},
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': user_data['role'],
                    'enrollment_number': user_data.get('enrollment_number'),
                    'class_grade': user_data.get('class_grade'),
                    'is_active_member': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'✓ User {user.username} created')
        
        # Create categories
        categories_data = [
            {'name': 'Fiction', 'description': 'Fictional literature and novels'},
            {'name': 'Science', 'description': 'Scientific books and textbooks'},
            {'name': 'History', 'description': 'Historical books and biographies'},
            {'name': 'Mathematics', 'description': 'Mathematics textbooks and references'},
            {'name': 'Literature', 'description': 'Classic and modern literature'},
            {'name': 'Technology', 'description': 'Computer science and technology books'},
            {'name': 'Biography', 'description': 'Biographies and autobiographies'},
            {'name': 'Reference', 'description': 'Reference books and encyclopedias'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'✓ Category {category.name} created')
        
        # Create authors
        authors_data = [
            {'first_name': 'William', 'last_name': 'Shakespeare', 'nationality': 'English'},
            {'first_name': 'Jane', 'last_name': 'Austen', 'nationality': 'English'},
            {'first_name': 'Mark', 'last_name': 'Twain', 'nationality': 'American'},
            {'first_name': 'Charles', 'last_name': 'Dickens', 'nationality': 'English'},
            {'first_name': 'George', 'last_name': 'Orwell', 'nationality': 'English'},
            {'first_name': 'Harper', 'last_name': 'Lee', 'nationality': 'American'},
            {'first_name': 'J.K.', 'last_name': 'Rowling', 'nationality': 'British'},
            {'first_name': 'Stephen', 'last_name': 'King', 'nationality': 'American'},
            {'first_name': 'Agatha', 'last_name': 'Christie', 'nationality': 'English'},
            {'first_name': 'Ernest', 'last_name': 'Hemingway', 'nationality': 'American'},
        ]
        
        for author_data in authors_data:
            author, created = Author.objects.get_or_create(
                first_name=author_data['first_name'],
                last_name=author_data['last_name'],
                defaults={'nationality': author_data['nationality']}
            )
            if created:
                self.stdout.write(f'✓ Author {author.get_full_name()} created')
        
        # Create publishers
        publishers_data = [
            {'name': 'Penguin Random House', 'website': 'https://www.penguinrandomhouse.com'},
            {'name': 'HarperCollins', 'website': 'https://www.harpercollins.com'},
            {'name': 'Simon & Schuster', 'website': 'https://www.simonandschuster.com'},
            {'name': 'Macmillan Publishers', 'website': 'https://www.macmillan.com'},
            {'name': 'Scholastic', 'website': 'https://www.scholastic.com'},
        ]
        
        for pub_data in publishers_data:
            publisher, created = Publisher.objects.get_or_create(
                name=pub_data['name'],
                defaults={'website': pub_data['website']}
            )
            if created:
                self.stdout.write(f'✓ Publisher {publisher.name} created')
        
        # Create sample books
        books_data = [
            {
                'title': 'To Kill a Mockingbird',
                'isbn': '978-0-06-112008-4',
                'publication_date': date(1960, 7, 11),
                'pages': 376,
                'section': 'Fiction',
                'shelf_location': 'A1',
                'summary': 'A gripping tale of racial injustice and childhood innocence in the American South.',
                'authors': ['Harper Lee'],
                'categories': ['Fiction', 'Literature'],
                'publisher': 'HarperCollins',
            },
            {
                'title': '1984',
                'isbn': '978-0-452-28423-4',
                'publication_date': date(1949, 6, 8),
                'pages': 328,
                'section': 'Fiction',
                'shelf_location': 'A2',
                'summary': 'A dystopian social science fiction novel about totalitarian control.',
                'authors': ['George Orwell'],
                'categories': ['Fiction', 'Literature'],
                'publisher': 'Penguin Random House',
            },
            {
                'title': 'Pride and Prejudice',
                'isbn': '978-0-14-143951-8',
                'publication_date': date(1813, 1, 28),
                'pages': 432,
                'section': 'Fiction',
                'shelf_location': 'A3',
                'summary': 'A romantic novel about manners, upbringing, morality, and marriage.',
                'authors': ['Jane Austen'],
                'categories': ['Fiction', 'Literature'],
                'publisher': 'Penguin Random House',
            },
            {
                'title': 'The Adventures of Tom Sawyer',
                'isbn': '978-0-486-40077-6',
                'publication_date': date(1876, 6, 1),
                'pages': 274,
                'section': 'Fiction',
                'shelf_location': 'A4',
                'summary': 'The adventures of a young boy growing up along the Mississippi River.',
                'authors': ['Mark Twain'],
                'categories': ['Fiction', 'Literature'],
                'publisher': 'Penguin Random House',
            },
            {
                'title': 'Harry Potter and the Philosopher\'s Stone',
                'isbn': '978-0-7475-3269-9',
                'publication_date': date(1997, 6, 26),
                'pages': 223,
                'section': 'Fiction',
                'shelf_location': 'B1',
                'summary': 'A young wizard\'s journey begins at Hogwarts School of Witchcraft and Wizardry.',
                'authors': ['J.K. Rowling'],
                'categories': ['Fiction'],
                'publisher': 'Scholastic',
            },
        ]
        
        admin_user = User.objects.filter(is_superuser=True).first()
        
        for book_data in books_data:
            book, created = Book.objects.get_or_create(
                isbn=book_data['isbn'],
                defaults={
                    'title': book_data['title'],
                    'publication_date': book_data['publication_date'],
                    'pages': book_data['pages'],
                    'section': book_data['section'],
                    'shelf_location': book_data['shelf_location'],
                    'summary': book_data['summary'],
                    'total_copies': random.randint(2, 5),
                    'created_by': admin_user,
                }
            )
            
            if created:
                book.available_copies = book.total_copies
                
                # Add publisher
                if book_data['publisher']:
                    publisher = Publisher.objects.get(name=book_data['publisher'])
                    book.publisher = publisher
                
                book.save()
                
                # Add authors
                for author_name in book_data['authors']:
                    first_name, last_name = author_name.split(' ', 1)
                    author = Author.objects.get(first_name=first_name, last_name=last_name)
                    book.authors.add(author)
                
                # Add categories
                for category_name in book_data['categories']:
                    category = Category.objects.get(name=category_name)
                    book.categories.add(category)
                
                self.stdout.write(f'✓ Book "{book.title}" created')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )
