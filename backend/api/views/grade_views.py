from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from api.models import Grade
from api.serializers import GradeSerializer


class GradeViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for grades"""
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [AllowAny]
