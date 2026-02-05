from rest_framework import serializers
from api.models import Grade

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'name', 'level', 'description']
