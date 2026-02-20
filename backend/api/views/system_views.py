"""
System status views for checking AI integration and dependencies
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone


@api_view(['GET'])
@permission_classes([IsAdminUser])
def ai_integration_status(request):
    """
    Check AI integration status and installed dependencies.
    Only accessible to admin users.
    """
    status = {
        'integrated': True,
        'models_available': False,
        'dependencies': {},
        'features': {
            'textbook_upload': True,
            'lesson_generation': True,
            'batch_processing': True,
            'review_workflow': True,
            'publishing': True
        },
        'generation_modes': {},
        'statistics': {}
    }
    
    # Check for transformers (Hugging Face)
    try:
        import transformers
        status['dependencies']['transformers'] = {
            'installed': True,
            'version': transformers.__version__,
            'description': 'Hugging Face models for text processing'
        }
        status['generation_modes']['offline'] = True
    except ImportError:
        status['dependencies']['transformers'] = {
            'installed': False,
            'description': 'Required for offline AI generation',
            'install_command': 'pip install transformers torch'
        }
        status['generation_modes']['offline'] = False
    
    # Check for PyTorch
    try:
        import torch
        status['dependencies']['torch'] = {
            'installed': True,
            'version': torch.__version__,
            'description': 'Deep learning framework'
        }
    except ImportError:
        status['dependencies']['torch'] = {
            'installed': False,
            'description': 'Required for AI model inference',
            'install_command': 'pip install torch'
        }
    
    # Check for OpenAI/OpenRouter
    try:
        import openai
        status['dependencies']['openai'] = {
            'installed': True,
            'version': openai.__version__,
            'description': 'OpenAI/OpenRouter API client'
        }
        
        # Check for OpenRouter API key (preferred)
        openrouter_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        openai_key = getattr(settings, 'OPENAI_API_KEY', None)
        
        if openrouter_key:
            status['generation_modes']['openrouter'] = True
            status['generation_modes']['api'] = 'openrouter'
            status['dependencies']['openai']['api_key_configured'] = True
            status['dependencies']['openai']['provider'] = 'OpenRouter'
        elif openai_key:
            status['generation_modes']['openai'] = True
            status['generation_modes']['api'] = 'openai'
            status['dependencies']['openai']['api_key_configured'] = True
            status['dependencies']['openai']['provider'] = 'OpenAI'
        else:
            status['generation_modes']['openai'] = False
            status['generation_modes']['openrouter'] = False
            status['dependencies']['openai']['api_key_configured'] = False
            
    except ImportError:
        status['dependencies']['openai'] = {
            'installed': False,
            'description': 'Optional: For API-based AI generation (OpenRouter/OpenAI)',
            'install_command': 'pip install openai'
        }
        status['generation_modes']['openai'] = False
        status['generation_modes']['openrouter'] = False
    
    # Check if models are available
    status['models_available'] = status['dependencies'].get('transformers', {}).get('installed', False)
    
    # Get statistics from database
    from api.models import TextbookChapter, GeneratedLesson
    
    status['statistics'] = {
        'total_chapters': TextbookChapter.objects.count(),
        'chapters_uploaded': TextbookChapter.objects.filter(status='uploaded').count(),
        'chapters_processing': TextbookChapter.objects.filter(status='processing').count(),
        'chapters_generated': TextbookChapter.objects.filter(status='generated').count(),
        'chapters_published': TextbookChapter.objects.filter(status='published').count(),
        'total_lessons': GeneratedLesson.objects.count(),
        'lessons_draft': GeneratedLesson.objects.filter(status='draft').count(),
        'lessons_approved': GeneratedLesson.objects.filter(status='approved').count(),
        'lessons_published': GeneratedLesson.objects.filter(published_capsule__isnull=False).count()
    }
    
    # Determine overall status
    all_installed = all(
        dep.get('installed', False) 
        for dep in status['dependencies'].values()
    )
    
    if all_installed:
        status['status_message'] = 'All AI dependencies installed and ready!'
        status['status_level'] = 'success'
    elif status['models_available']:
        status['status_message'] = 'Offline AI generation available. Install OpenAI for higher quality.'
        status['status_level'] = 'warning'
    else:
        status['status_message'] = 'AI dependencies not installed. Run: pip install -r requirements.txt'
        status['status_level'] = 'error'
    
    # Add installation instructions
    status['installation'] = {
        'quick_install': 'pip install -r requirements.txt',
        'individual_packages': [
            'pip install transformers torch',
            'pip install openai tiktoken',
            'pip install nltk beautifulsoup4'
        ],
        'note': 'PyTorch installation may take several minutes on first install.'
    }
    
    return Response(status)


@api_view(['GET'])
def system_health(request):
    """
    Basic system health check (public endpoint)
    Resilient to database issues - returns basic health even if DB fails
    Used by Railway for deployment health checks from healthcheck.railway.app
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Log the health check request
    logger.info(f"Health check request from: {request.META.get('HTTP_HOST', 'unknown')}")
    
    health = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'host': request.META.get('HTTP_HOST', 'unknown'),
    }
    
    # Try to check database, but don't fail if it's not available
    try:
        from api.models import Subject, Grade, CurriculumCapsule
        from django.db import connection
        
        # Test database connection
        connection.ensure_connection()
        
        health['database'] = 'connected'
        health['stats'] = {
            'subjects': Subject.objects.count(),
            'grades': Grade.objects.count(),
            'lessons': CurriculumCapsule.objects.count()
        }
        logger.info("Health check: Database connected successfully")
    except Exception as e:
        # Database not available yet, but app is still healthy
        health['database'] = 'not_ready'
        health['database_error'] = str(e)
        logger.warning(f"Health check: Database not ready - {str(e)}")
        # Still return 200 OK so Railway doesn't think app is unhealthy
    
    return Response(health, status=200)
