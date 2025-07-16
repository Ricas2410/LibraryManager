FROM python:3.11-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBUG=False
ENV DJANGO_SETTINGS_MODULE=library_management.production_settings

# Set work directory
WORKDIR /app

# Install system dependencies including cryptographic libraries and OpenSSL runtime
RUN apt-get update && apt-get install -y \
    gcc \
    libc6-dev \
    libssl-dev \
    libffi-dev \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn==22.0.0 whitenoise==6.6.0 psycopg2-binary==2.9.9 django-redis==5.4.0

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD gunicorn library_management.wsgi:application --bind 0.0.0.0:8080