from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from library.models import User, Book, Publisher, Category, Author, Section, ShelfLocation, Floor, LibrarySettings


class Command(BaseCommand):
    help = 'Set up initial data for the library system'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')

        # Create admin user if not exists
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create(
                username='admin',
                email='admin@library.com',
                first_name='Library',
                last_name='Admin',
                role='admin',
                is_staff=True,
                is_superuser=True,
                password=make_password('admin123'),
                is_active_member=True
            )
            self.stdout.write(f'Created admin user: {admin_user.username}')

        # Create sample floors
        floors_data = [
            {'name': 'Ground Floor', 'description': 'Main entrance and reception'},
            {'name': 'First Floor', 'description': 'General collection and study areas'},
            {'name': 'Second Floor', 'description': 'Reference and research materials'},
            {'name': 'Basement', 'description': 'Archives and storage'},
        ]

        for floor_data in floors_data:
            floor, created = Floor.objects.get_or_create(
                name=floor_data['name'],
                defaults={'description': floor_data['description']}
            )
            if created:
                self.stdout.write(f'Created floor: {floor.name}')

        # Create sample sections
        sections_data = [
            {'name': 'Fiction', 'description': 'Novels and fictional works', 'floor': 'First Floor'},
            {'name': 'Non-Fiction', 'description': 'Educational and informational books', 'floor': 'First Floor'},
            {'name': 'Science', 'description': 'Scientific and technical books', 'floor': 'Second Floor'},
            {'name': 'History', 'description': 'Historical books and documents', 'floor': 'Second Floor'},
            {'name': 'Children', 'description': 'Books for children and young adults', 'floor': 'Ground Floor'},
            {'name': 'Reference', 'description': 'Dictionaries, encyclopedias, and reference materials', 'floor': 'Second Floor'},
        ]

        for section_data in sections_data:
            floor = Floor.objects.get(name=section_data['floor'])
            section, created = Section.objects.get_or_create(
                name=section_data['name'],
                defaults={
                    'description': section_data['description'],
                    'floor': floor.name
                }
            )
            if created:
                self.stdout.write(f'Created section: {section.name}')

        # Create sample shelf locations
        shelf_locations_data = [
            {'code': 'A1', 'section': 'Fiction', 'description': 'Fiction A-D', 'capacity': 50},
            {'code': 'A2', 'section': 'Fiction', 'description': 'Fiction E-H', 'capacity': 50},
            {'code': 'A3', 'section': 'Fiction', 'description': 'Fiction I-M', 'capacity': 50},
            {'code': 'B1', 'section': 'Non-Fiction', 'description': 'General Non-Fiction', 'capacity': 60},
            {'code': 'B2', 'section': 'Non-Fiction', 'description': 'Biography and Autobiography', 'capacity': 40},
            {'code': 'C1', 'section': 'Science', 'description': 'Physics and Chemistry', 'capacity': 45},
            {'code': 'C2', 'section': 'Science', 'description': 'Biology and Medicine', 'capacity': 45},
            {'code': 'D1', 'section': 'History', 'description': 'World History', 'capacity': 55},
            {'code': 'E1', 'section': 'Children', 'description': 'Picture Books', 'capacity': 30},
            {'code': 'E2', 'section': 'Children', 'description': 'Young Adult', 'capacity': 35},
            {'code': 'R1', 'section': 'Reference', 'description': 'Dictionaries and Encyclopedias', 'capacity': 25},
        ]

        for shelf_data in shelf_locations_data:
            section = Section.objects.get(name=shelf_data['section'])
            shelf, created = ShelfLocation.objects.get_or_create(
                code=shelf_data['code'],
                defaults={
                    'section': section,
                    'description': shelf_data['description'],
                    'capacity': shelf_data['capacity']
                }
            )
            if created:
                self.stdout.write(f'Created shelf location: {shelf.code}')

        # Create sample publishers
        publishers_data = [
            {'name': 'Penguin Random House', 'address': 'New York, NY', 'email': 'info@penguinrandomhouse.com'},
            {'name': 'HarperCollins', 'address': 'New York, NY', 'email': 'info@harpercollins.com'},
            {'name': 'Simon & Schuster', 'address': 'New York, NY', 'email': 'info@simonandschuster.com'},
            {'name': 'Macmillan Publishers', 'address': 'London, UK', 'email': 'info@macmillan.com'},
            {'name': 'Scholastic', 'address': 'New York, NY', 'email': 'info@scholastic.com'},
            {'name': 'Oxford University Press', 'address': 'Oxford, UK', 'email': 'info@oup.com'},
            {'name': 'Cambridge University Press', 'address': 'Cambridge, UK', 'email': 'info@cambridge.org'},
        ]

        for pub_data in publishers_data:
            publisher, created = Publisher.objects.get_or_create(
                name=pub_data['name'],
                defaults={
                    'address': pub_data['address'],
                    'email': pub_data['email']
                }
            )
            if created:
                self.stdout.write(f'Created publisher: {publisher.name}')

        # Create sample categories
        categories_data = [
            {'name': 'Fiction', 'description': 'Fictional literature including novels and short stories'},
            {'name': 'Mystery', 'description': 'Mystery and detective fiction'},
            {'name': 'Romance', 'description': 'Romantic fiction'},
            {'name': 'Science Fiction', 'description': 'Science fiction and fantasy'},
            {'name': 'Biography', 'description': 'Biographical works'},
            {'name': 'History', 'description': 'Historical books and documents'},
            {'name': 'Science', 'description': 'Scientific and technical books'},
            {'name': 'Mathematics', 'description': 'Mathematics and statistics'},
            {'name': 'Computer Science', 'description': 'Programming and computer science'},
            {'name': 'Children', 'description': 'Books for children'},
            {'name': 'Young Adult', 'description': 'Books for teenagers and young adults'},
            {'name': 'Reference', 'description': 'Reference materials'},
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create sample authors
        authors_data = [
            {'first_name': 'J.K.', 'last_name': 'Rowling', 'nationality': 'British'},
            {'first_name': 'Stephen', 'last_name': 'King', 'nationality': 'American'},
            {'first_name': 'Agatha', 'last_name': 'Christie', 'nationality': 'British'},
            {'first_name': 'George', 'last_name': 'Orwell', 'nationality': 'British'},
            {'first_name': 'Jane', 'last_name': 'Austen', 'nationality': 'British'},
            {'first_name': 'Mark', 'last_name': 'Twain', 'nationality': 'American'},
            {'first_name': 'Charles', 'last_name': 'Dickens', 'nationality': 'British'},
            {'first_name': 'William', 'last_name': 'Shakespeare', 'nationality': 'British'},
        ]

        for author_data in authors_data:
            author, created = Author.objects.get_or_create(
                first_name=author_data['first_name'],
                last_name=author_data['last_name'],
                defaults={'nationality': author_data['nationality']}
            )
            if created:
                self.stdout.write(f'Created author: {author.get_full_name()}')

        # Create sample books
        self._create_sample_books()

        self.stdout.write(self.style.SUCCESS('Initial data setup completed successfully!'))
        self.stdout.write('Admin credentials: username=admin, password=admin123')

    def _create_sample_books(self):
        """Create sample books with proper relationships"""
        from datetime import date

        # Get some publishers, authors, categories, sections, and shelf locations
        penguin = Publisher.objects.get(name='Penguin Random House')
        harper = Publisher.objects.get(name='HarperCollins')
        oxford = Publisher.objects.get(name='Oxford University Press')

        jk_rowling = Author.objects.get(first_name='J.K.', last_name='Rowling')
        stephen_king = Author.objects.get(first_name='Stephen', last_name='King')
        agatha_christie = Author.objects.get(first_name='Agatha', last_name='Christie')
        george_orwell = Author.objects.get(first_name='George', last_name='Orwell')

        fiction_cat = Category.objects.get(name='Fiction')
        mystery_cat = Category.objects.get(name='Mystery')
        scifi_cat = Category.objects.get(name='Science Fiction')

        fiction_section = Section.objects.get(name='Fiction')
        children_section = Section.objects.get(name='Children')

        shelf_a1 = ShelfLocation.objects.get(code='A1')
        shelf_a2 = ShelfLocation.objects.get(code='A2')
        shelf_e1 = ShelfLocation.objects.get(code='E1')

        ground_floor = Floor.objects.get(name='Ground Floor')
        first_floor = Floor.objects.get(name='First Floor')

        books_data = [
            {
                'title': "Harry Potter and the Philosopher's Stone",
                'isbn': '978-0-7475-3269-9',
                'publisher': penguin,
                'authors': [jk_rowling],
                'categories': [fiction_cat, scifi_cat],
                'publication_date': date(1997, 6, 26),
                'pages': 223,
                'section': children_section,
                'shelf_location': shelf_e1,
                'floor': ground_floor,
                'total_copies': 5,
                'summary': 'The first book in the Harry Potter series, following young Harry as he discovers he is a wizard.',
                'price': 12.99
            },
            {
                'title': 'The Shining',
                'isbn': '978-0-385-12167-5',
                'publisher': harper,
                'authors': [stephen_king],
                'categories': [fiction_cat],
                'publication_date': date(1977, 1, 28),
                'pages': 447,
                'section': fiction_section,
                'shelf_location': shelf_a1,
                'floor': first_floor,
                'total_copies': 3,
                'summary': 'A psychological horror novel about a family isolated in a haunted hotel.',
                'price': 15.99
            },
            {
                'title': 'Murder on the Orient Express',
                'isbn': '978-0-00-711926-0',
                'publisher': harper,
                'authors': [agatha_christie],
                'categories': [fiction_cat, mystery_cat],
                'publication_date': date(1934, 1, 1),
                'pages': 256,
                'section': fiction_section,
                'shelf_location': shelf_a2,
                'floor': first_floor,
                'total_copies': 4,
                'summary': 'Hercule Poirot investigates a murder aboard the famous Orient Express.',
                'price': 13.99
            },
            {
                'title': '1984',
                'isbn': '978-0-452-28423-4',
                'publisher': oxford,
                'authors': [george_orwell],
                'categories': [fiction_cat, scifi_cat],
                'publication_date': date(1949, 6, 8),
                'pages': 328,
                'section': fiction_section,
                'shelf_location': shelf_a1,
                'floor': first_floor,
                'total_copies': 6,
                'summary': 'A dystopian social science fiction novel about totalitarian control.',
                'price': 14.99
            },
            {
                'title': 'Animal Farm',
                'isbn': '978-0-452-28424-1',
                'publisher': oxford,
                'authors': [george_orwell],
                'categories': [fiction_cat],
                'publication_date': date(1945, 8, 17),
                'pages': 112,
                'section': fiction_section,
                'shelf_location': shelf_a1,
                'floor': first_floor,
                'total_copies': 4,
                'summary': 'An allegorical novella about farm animals who rebel against their human farmer.',
                'price': 10.99
            }
        ]

        for book_data in books_data:
            authors = book_data.pop('authors')
            categories = book_data.pop('categories')

            book, created = Book.objects.get_or_create(
                isbn=book_data['isbn'],
                defaults={**book_data, 'available_copies': book_data['total_copies']}
            )

            if created:
                book.authors.set(authors)
                book.categories.set(categories)
                self.stdout.write(f'Created book: {book.title}')
