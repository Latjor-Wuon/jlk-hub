from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from api.models import Subject
from api.serializers import SubjectSerializer


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for subjects"""
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]
