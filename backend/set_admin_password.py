from django.contrib.auth.models import User

# Set password for admin user
try:
    user = User.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print("Admin password set successfully!")
    print("Username: admin")
    print("Password: admin123")
except User.DoesNotExist:
    print("Admin user not found")
