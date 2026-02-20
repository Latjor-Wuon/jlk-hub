web: cd backend && gunicorn jln_hub.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 --log-level debug
release: cd backend && python manage.py migrate --no-input