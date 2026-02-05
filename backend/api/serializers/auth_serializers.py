from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from api.models import LearnerProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    grade = serializers.IntegerField(write_only=True, required=False)
    school_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'first_name', 'last_name', 'grade', 'school_name']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': False}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        grade_id = validated_data.pop('grade', None)
        school_name = validated_data.pop('school_name', '')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        
        # Create learner profile
        from api.models import Grade
        grade = None
        if grade_id:
            try:
                grade = Grade.objects.get(id=grade_id)
            except Grade.DoesNotExist:
                pass
        
        LearnerProfile.objects.create(
            user=user,
            grade=grade,
            school_name=school_name
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    
    class Meta:
        model = LearnerProfile
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'grade', 'grade_name', 'school_name', 'date_of_birth', 'created_at']
