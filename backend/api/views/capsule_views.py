from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from api.models import CurriculumCapsule
from api.serializers import CurriculumCapsuleSerializer, CurriculumCapsuleListSerializer


class CurriculumCapsuleViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for curriculum capsules"""
    queryset = CurriculumCapsule.objects.filter(is_published=True)
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CurriculumCapsuleListSerializer
        return CurriculumCapsuleSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        subject_id = self.request.query_params.get('subject')
        grade_id = self.request.query_params.get('grade')
        
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if grade_id:
            queryset = queryset.filter(grade_id=grade_id)
        
        return queryset.order_by('order')
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured lessons"""
        featured = self.get_queryset()[:6]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)
