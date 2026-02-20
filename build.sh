#!/usr/bin/env bash
# exit on error
set -o errexit

# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Collect static files (skip if fails - production can still work)
python manage.py collectstatic --no-input || echo "Static collection failed, continuing..."

# Run migrations
python manage.py migrate --no-input

echo "Build completed successfully!"
