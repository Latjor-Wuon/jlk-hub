"""
API Views for AI-Assisted Lesson Generation
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.db.models import Count, Q
from api.models import (
    TextbookChapter,
    GeneratedLesson,
    LessonSection,
    GeneratedQuestion,
    Subject,
    Grade
)
from api.serializers import (
    TextbookChapterSerializer,
    TextbookChapterListSerializer,
    GeneratedLessonSerializer,
    GeneratedLessonListSerializer,
    LessonSectionSerializer,
    GeneratedQuestionSerializer,
    LessonGenerationRequestSerializer,
    LessonPublishSerializer,
    LessonReviewSerializer,
    BatchGenerationSerializer
)
from api.services import LessonGeneratorService, PDFExtractorService
from rest_framework.parsers import MultiPartParser, FormParser


class TextbookChapterViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing textbook chapters.
    Allows uploading raw textbook content for AI processing.
    """
    queryset = TextbookChapter.objects.all()
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TextbookChapterListSerializer
        return TextbookChapterSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by subject
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        # Filter by grade
        grade_id = self.request.query_params.get('grade')
        if grade_id:
            queryset = queryset.filter(grade_id=grade_id)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Save chapter with current user as uploader and optionally auto-generate lesson"""
        chapter = serializer.save(uploaded_by=self.request.user)
        
        # Auto-generate lesson if requested
        auto_generate = self.request.data.get('auto_generate', 'false')
        if auto_generate in [True, 'true', '1', 'yes']:
            generator = LessonGeneratorService()  # Auto-detect AI
            lesson = generator.generate_lesson_from_chapter(chapter)
            # Store lesson data in the request context for response
            self.request._generated_lesson = lesson
    
    def create(self, request, *args, **kwargs):
        """Override create to include generated lesson in response"""
        response = super().create(request, *args, **kwargs)
        
        # Add generated lesson to response if available
        if hasattr(request, '_generated_lesson') and request._generated_lesson:
            from api.serializers import GeneratedLessonSerializer
            response.data['lesson'] = GeneratedLessonSerializer(request._generated_lesson).data
            response.data['message'] = 'Chapter uploaded and lesson generated successfully.'
        
        return response

    @action(detail=False, methods=['post'])
    def upload_pdf(self, request):
        """
        Upload a PDF file and extract text content automatically.
        
        POST /api/chapters/upload_pdf/
        Content-Type: multipart/form-data
        Body: {
            "pdf_file": <file>,
            "title": "Chapter Title",
            "subject": 1,
            "grade": 1,
            "chapter_number": "1.1" (optional),
            "source_book": "Book Name" (optional),
            "start_page": 1 (optional),
            "end_page": 10 (optional),
            "auto_generate": false (optional - auto generate lesson after upload)
        }
        """
        # Check if PDF extraction is available
        if not PDFExtractorService.is_available():
            return Response({
                'status': 'error',
                'message': 'PDF extraction not available. Install: pip install pdfplumber PyPDF2'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Validate required fields
        pdf_file = request.FILES.get('pdf_file')
        if not pdf_file:
            return Response({
                'status': 'error',
                'message': 'No PDF file provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not pdf_file.name.lower().endswith('.pdf'):
            return Response({
                'status': 'error',
                'message': 'File must be a PDF'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        title = request.data.get('title')
        subject_id = request.data.get('subject')
        grade_id = request.data.get('grade')
        
        if not all([title, subject_id, grade_id]):
            return Response({
                'status': 'error',
                'message': 'Title, subject, and grade are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Extract text from PDF
            start_page = request.data.get('start_page')
            end_page = request.data.get('end_page')
            
            extracted_text, metadata = PDFExtractorService.extract_from_django_file(pdf_file)
            
            if metadata['word_count'] < 50:
                return Response({
                    'status': 'error',
                    'message': f'Extracted text is too short ({metadata["word_count"]} words). The PDF may be image-based or empty.',
                    'metadata': metadata
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create chapter with extracted content
            chapter = TextbookChapter.objects.create(
                title=title,
                subject_id=subject_id,
                grade_id=grade_id,
                chapter_number=request.data.get('chapter_number', ''),
                source_book=request.data.get('source_book', pdf_file.name),
                page_numbers=f"{start_page or 1}-{end_page or metadata['total_pages']}",
                raw_content=extracted_text,
                pdf_file=pdf_file,
                uploaded_by=request.user,
                processing_notes=f"Extracted from PDF: {metadata['extracted_pages']}/{metadata['total_pages']} pages, {metadata['word_count']} words"
            )
            
            response_data = {
                'status': 'success',
                'message': f'PDF uploaded and text extracted successfully ({metadata["word_count"]} words from {metadata["extracted_pages"]} pages)',
                'chapter': TextbookChapterSerializer(chapter).data,
                'extraction_metadata': metadata
            }
            
            # Auto-generate lesson if requested
            auto_generate = request.data.get('auto_generate', 'false')
            if auto_generate in [True, 'true', '1', 'yes']:
                generator = LessonGeneratorService()  # Auto-detect AI
                lesson = generator.generate_lesson_from_chapter(chapter)
                if lesson:
                    response_data['lesson'] = GeneratedLessonSerializer(lesson).data
                    response_data['message'] += ' Lesson generated automatically.'
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Failed to process PDF: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def generate_lesson(self, request, pk=None):
        """
        Trigger AI lesson generation for a specific chapter.
        
        POST /api/chapters/{id}/generate_lesson/
        Body: {
            "use_openai": false,  # Optional, default false
            "validate_only": false  # Optional, default false
        }
        """
        chapter = self.get_object()
        
        # Validate request
        serializer = LessonGenerationRequestSerializer(data={
            'chapter_id': chapter.id,
            'use_openai': request.data.get('use_openai', True),  # Default to True
            'validate_only': request.data.get('validate_only', False)
        })
        serializer.is_valid(raise_exception=True)
        
        # Initialize generator service
        generator = LessonGeneratorService(
            use_openai=serializer.validated_data['use_openai']
        )
        
        # Generate lesson
        lesson = generator.generate_lesson_from_chapter(
            chapter=chapter,
            validate_only=serializer.validated_data['validate_only']
        )
        
        if lesson:
            return Response({
                'status': 'success',
                'message': 'Lesson generated successfully',
                'lesson': GeneratedLessonSerializer(lesson).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'status': 'error',
                'message': 'Lesson generation failed. Check chapter processing notes.',
                'chapter_id': chapter.id
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def batch_generate(self, request):
        """
        Generate lessons for multiple chapters at once.
        
        POST /api/chapters/batch_generate/
        Body: {
            "chapter_ids": [1, 2, 3],
            "use_openai": false
        }
        """
        serializer = BatchGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        chapter_ids = serializer.validated_data['chapter_ids']
        use_openai = serializer.validated_data['use_openai']
        
        # Initialize generator
        generator = LessonGeneratorService(use_openai=use_openai)
        
        results = {
            'success': [],
            'failed': [],
            'skipped': []
        }
        
        chapters = TextbookChapter.objects.filter(id__in=chapter_ids)
        
        for chapter in chapters:
            # Skip already processed chapters
            if chapter.status in ['processing', 'generated', 'published']:
                results['skipped'].append({
                    'chapter_id': chapter.id,
                    'title': chapter.title,
                    'reason': f'Already {chapter.status}'
                })
                continue
            
            # Generate lesson
            lesson = generator.generate_lesson_from_chapter(chapter)
            
            if lesson:
                results['success'].append({
                    'chapter_id': chapter.id,
                    'lesson_id': lesson.id,
                    'title': lesson.title
                })
            else:
                results['failed'].append({
                    'chapter_id': chapter.id,
                    'title': chapter.title,
                    'reason': chapter.processing_notes or 'Unknown error'
                })
        
        return Response({
            'status': 'completed',
            'message': f"Generated {len(results['success'])} lessons",
            'results': results
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get statistics about chapter processing.
        
        GET /api/chapters/statistics/
        """
        stats = {
            'total_chapters': TextbookChapter.objects.count(),
            'by_status': {},
            'by_subject': {},
            'recent_uploads': []
        }
        
        # Count by status
        status_counts = TextbookChapter.objects.values('status').annotate(
            count=Count('id')
        )
        for item in status_counts:
            stats['by_status'][item['status']] = item['count']
        
        # Count by subject
        subject_counts = TextbookChapter.objects.values(
            'subject__name'
        ).annotate(count=Count('id'))
        for item in subject_counts:
            stats['by_subject'][item['subject__name']] = item['count']
        
        # Recent uploads
        recent = TextbookChapter.objects.order_by('-created_at')[:5]
        stats['recent_uploads'] = TextbookChapterListSerializer(
            recent, many=True
        ).data
        
        return Response(stats)


class GeneratedLessonViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing AI-generated lessons.
    Allows reviewing, editing, and publishing lessons.
    """
    queryset = GeneratedLesson.objects.all()
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return GeneratedLessonListSerializer
        return GeneratedLessonSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'source_chapter',
            'source_chapter__subject',
            'source_chapter__grade'
        ).prefetch_related('sections', 'generated_questions')
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by subject
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(source_chapter__subject_id=subject_id)
        
        # Filter by grade
        grade_id = self.request.query_params.get('grade')
        if grade_id:
            queryset = queryset.filter(source_chapter__grade_id=grade_id)
        
        # Filter unpublished
        unpublished_only = self.request.query_params.get('unpublished')
        if unpublished_only:
            queryset = queryset.filter(published_capsule__isnull=True)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """
        Review and approve/reject a generated lesson.
        
        POST /api/generated-lessons/{id}/review/
        Body: {
            "status": "approved",  # or "rejected"
            "review_notes": "Looks good!"
        }
        """
        lesson = self.get_object()
        
        serializer = LessonReviewSerializer(data={
            'lesson_id': lesson.id,
            'status': request.data.get('status'),
            'review_notes': request.data.get('review_notes', '')
        })
        serializer.is_valid(raise_exception=True)
        
        # Update lesson status
        lesson.status = serializer.validated_data['status']
        lesson.review_notes = serializer.validated_data.get('review_notes', '')
        lesson.reviewed_by = request.user
        lesson.reviewed_at = timezone.now()
        lesson.save()
        
        return Response({
            'status': 'success',
            'message': f"Lesson {serializer.validated_data['status']}",
            'lesson': GeneratedLessonSerializer(lesson).data
        })
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Publish a generated lesson as a curriculum capsule.
        
        POST /api/generated-lessons/{id}/publish/
        """
        lesson = self.get_object()
        
        # Check if already published
        if lesson.published_capsule:
            return Response({
                'status': 'warning',
                'message': 'Lesson already published',
                'capsule_id': lesson.published_capsule.id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Initialize generator service
        generator = LessonGeneratorService()
        
        # Publish to capsule
        capsule = generator.publish_lesson_to_capsule(lesson)
        
        if capsule:
            return Response({
                'status': 'success',
                'message': 'Lesson published successfully',
                'capsule_id': capsule.id,
                'lesson': GeneratedLessonSerializer(lesson).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'status': 'error',
                'message': 'Publishing failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def regenerate_questions(self, request, pk=None):
        """
        Regenerate questions for a lesson.
        
        POST /api/generated-lessons/{id}/regenerate_questions/
        """
        lesson = self.get_object()
        
        # Delete existing questions
        lesson.generated_questions.all().delete()
        
        # Initialize generator and regenerate
        generator = LessonGeneratorService()
        
        # Get chapter data
        lesson_data = generator._analyze_chapter_content(lesson.source_chapter)
        generator._generate_questions(lesson, lesson_data)
        
        # Refresh lesson
        lesson.refresh_from_db()
        
        return Response({
            'status': 'success',
            'message': 'Questions regenerated',
            'questions_count': lesson.generated_questions.count(),
            'lesson': GeneratedLessonSerializer(lesson).data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get statistics about generated lessons.
        
        GET /api/generated-lessons/statistics/
        """
        stats = {
            'total_lessons': GeneratedLesson.objects.count(),
            'by_status': {},
            'published_count': GeneratedLesson.objects.filter(
                published_capsule__isnull=False
            ).count(),
            'average_quality_score': 0,
            'total_sections': LessonSection.objects.count(),
            'total_questions': GeneratedQuestion.objects.count(),
        }
        
        # Count by status
        status_counts = GeneratedLesson.objects.values('status').annotate(
            count=Count('id')
        )
        for item in status_counts:
            stats['by_status'][item['status']] = item['count']
        
        # Average quality score
        avg_score = GeneratedLesson.objects.aggregate(
            avg=Count('quality_score')
        )
        stats['average_quality_score'] = avg_score.get('avg', 0)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def pending_review(self, request):
        """
        Get lessons pending review.
        
        GET /api/generated-lessons/pending_review/
        """
        lessons = self.get_queryset().filter(
            status__in=['draft', 'review']
        ).order_by('-quality_score', '-created_at')
        
        serializer = self.get_serializer(lessons, many=True)
        return Response(serializer.data)


class LessonSectionViewSet(viewsets.ModelViewSet):
    """API endpoint for managing lesson sections"""
    queryset = LessonSection.objects.all()
    serializer_class = LessonSectionSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by lesson
        lesson_id = self.request.query_params.get('lesson')
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)
        
        # Filter by section type
        section_type = self.request.query_params.get('type')
        if section_type:
            queryset = queryset.filter(section_type=section_type)
        
        return queryset.order_by('lesson', 'order')


class GeneratedQuestionViewSet(viewsets.ModelViewSet):
    """API endpoint for managing generated questions"""
    queryset = GeneratedQuestion.objects.all()
    serializer_class = GeneratedQuestionSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by lesson
        lesson_id = self.request.query_params.get('lesson')
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # Filter by question type
        question_type = self.request.query_params.get('type')
        if question_type:
            queryset = queryset.filter(question_type=question_type)
        
        return queryset.order_by('lesson', 'order')
