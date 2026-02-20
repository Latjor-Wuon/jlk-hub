#!/usr/bin/env bash
# Railway deployment troubleshooting script

echo "🔧 Starting Railway Deployment..."
echo "================================"

# Check Python version
echo "✓ Python version:"
python --version

# Check current directory
echo ""
echo "✓ Current directory:"
pwd

# List files
echo ""
echo "✓ Files in current directory:"
ls -la

# Navigate to backend
cd backend || exit 1
echo ""
echo "✓ Backend directory contents:"
ls -la

# Check if manage.py exists
if [ -f "manage.py" ]; then
    echo "✓ manage.py found"
else
    echo "✗ manage.py NOT found - build will fail!"
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt || exit 1

# Collect static files (with error handling)
echo ""
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input --verbosity 2 || {
    echo "⚠️  Static collection failed, continuing..."
}

# Run migrations
echo ""
echo "🗄️  Running database migrations..."
python manage.py migrate --no-input --verbosity 2 || exit 1

# Test Django setup
echo ""
echo "🧪 Testing Django setup..."
python manage.py check || exit 1

echo ""
echo "✅ Build completed successfully!"
echo "================================"
