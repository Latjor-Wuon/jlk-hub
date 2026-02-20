#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🔍 Current directory: $(pwd)"
echo "📁 Directory contents:"
ls -la

# Check if we're already in backend or need to navigate to it
if [ -f "manage.py" ]; then
    echo "✅ Already in backend directory"
    BACKEND_DIR="."
elif [ -d "backend" ] && [ -f "backend/manage.py" ]; then
    echo "✅ Found backend directory, navigating..."
    cd backend
    BACKEND_DIR="."
else
    echo "❌ Error: Cannot find Django project (manage.py)"
    exit 1
fi

echo "📍 Working directory: $(pwd)"

# Install Python dependencies
echo "📦 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "❌ requirements.txt not found!"
    exit 1
fi

# Collect static files (skip if fails - production can still work)
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input || echo "⚠️ Static collection failed, continuing..."

# Run migrations
echo "🗄️ Running migrations..."
python manage.py migrate --no-input

echo "✅ Build completed successfully!"
