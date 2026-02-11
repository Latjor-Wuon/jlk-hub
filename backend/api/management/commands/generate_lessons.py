"""
Management command to generate lessons from textbook chapters.

Usage:
    python manage.py generate_lessons --all
    python manage.py generate_lessons --chapter-id 1
    python manage.py generate_lessons --subject "Mathematics" --grade "Primary 5"
    python manage.py generate_lessons --status uploaded --use-openai
"""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from api.models import TextbookChapter, GeneratedLesson, Subject, Grade
from api.services import LessonGeneratorService


class Command(BaseCommand):
    help = 'Generate interactive lessons from textbook chapters using AI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Process all uploaded chapters that haven\'t been processed yet'
        )
        
        parser.add_argument(
            '--chapter-id',
            type=int,
            help='Generate lesson for a specific chapter ID'
        )
        
        parser.add_argument(
            '--subject',
            type=str,
            help='Filter by subject name'
        )
        
        parser.add_argument(
            '--grade',
            type=str,
            help='Filter by grade name'
        )
        
        parser.add_argument(
            '--status',
            type=str,
            default='uploaded',
            choices=['uploaded', 'failed'],
            help='Process chapters with this status (default: uploaded)'
        )
        
        parser.add_argument(
            '--use-openai',
            action='store_true',
            help='Use OpenAI API for generation (requires API key in settings)'
        )
        
        parser.add_argument(
            '--validate-only',
            action='store_true',
            help='Only validate chapters without generating lessons'
        )
        
        parser.add_argument(
            '--max-chapters',
            type=int,
            default=None,
            help='Maximum number of chapters to process'
        )
        
        parser.add_argument(
            '--auto-publish',
            action='store_true',
            help='Automatically publish generated lessons to capsules'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting lesson generation...'))
        
        # Initialize generator
        use_openai = options['use_openai']
        generator = LessonGeneratorService(use_openai=use_openai)
        
        if use_openai:
            self.stdout.write(self.style.WARNING('Using OpenAI API for generation'))
        else:
            self.stdout.write('Using rule-based generation (offline mode)')
        
        # Get chapters to process
        chapters = self._get_chapters(options)
        
        if not chapters:
            self.stdout.write(self.style.WARNING('No chapters found matching criteria'))
            return
        
        total = len(chapters)
        self.stdout.write(f'Found {total} chapter(s) to process')
        
        # Process chapters
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        for i, chapter in enumerate(chapters, 1):
            self.stdout.write(f'\n[{i}/{total}] Processing: {chapter.title}')
            
            # Check if already processed
            if chapter.status in ['processing', 'generated', 'published']:
                self.stdout.write(self.style.WARNING(f'  Skipped: Already {chapter.status}'))
                skipped_count += 1
                continue
            
            try:
                # Generate lesson
                lesson = generator.generate_lesson_from_chapter(
                    chapter=chapter,
                    validate_only=options['validate_only']
                )
                
                if lesson:
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Generated: {lesson.title}'))
                    self.stdout.write(f'    - Sections: {lesson.sections.count()}')
                    self.stdout.write(f'    - Questions: {lesson.generated_questions.count()}')
                    self.stdout.write(f'    - Quality Score: {lesson.quality_score:.2f}')
                    
                    # Auto-publish if requested
                    if options['auto_publish']:
                        capsule = generator.publish_lesson_to_capsule(lesson)
                        if capsule:
                            self.stdout.write(self.style.SUCCESS(f'    ✓ Published to capsule #{capsule.id}'))
                        else:
                            self.stdout.write(self.style.WARNING('    ! Publishing failed'))
                else:
                    failed_count += 1
                    error_msg = chapter.processing_notes or 'Unknown error'
                    self.stdout.write(self.style.ERROR(f'  ✗ Failed: {error_msg}'))
                    
            except Exception as e:
                failed_count += 1
                self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('\nLesson Generation Summary:'))
        self.stdout.write(f'  Total Processed: {total}')
        self.stdout.write(self.style.SUCCESS(f'  ✓ Successful: {success_count}'))
        if failed_count:
            self.stdout.write(self.style.ERROR(f'  ✗ Failed: {failed_count}'))
        if skipped_count:
            self.stdout.write(self.style.WARNING(f'  - Skipped: {skipped_count}'))
        self.stdout.write('='*50 + '\n')
        
        # Show statistics
        self._show_statistics()
    
    def _get_chapters(self, options):
        """Get chapters based on command options"""
        queryset = TextbookChapter.objects.all()
        
        # Specific chapter ID
        if options['chapter_id']:
            try:
                return [TextbookChapter.objects.get(id=options['chapter_id'])]
            except TextbookChapter.DoesNotExist:
                raise CommandError(f'Chapter with ID {options["chapter_id"]} not found')
        
        # Filter by status
        if not options['all']:
            queryset = queryset.filter(status=options['status'])
        else:
            # Process all that haven't been successfully processed
            queryset = queryset.exclude(status__in=['generated', 'published'])
        
        # Filter by subject
        if options['subject']:
            try:
                subject = Subject.objects.get(name__iexact=options['subject'])
                queryset = queryset.filter(subject=subject)
            except Subject.DoesNotExist:
                raise CommandError(f'Subject "{options["subject"]}" not found')
        
        # Filter by grade
        if options['grade']:
            try:
                grade = Grade.objects.get(name__iexact=options['grade'])
                queryset = queryset.filter(grade=grade)
            except Grade.DoesNotExist:
                raise CommandError(f'Grade "{options["grade"]}" not found')
        
        # Limit results
        if options['max_chapters']:
            queryset = queryset[:options['max_chapters']]
        
        return list(queryset.order_by('created_at'))
    
    def _show_statistics(self):
        """Display overall statistics"""
        total_chapters = TextbookChapter.objects.count()
        total_lessons = GeneratedLesson.objects.count()
        published = GeneratedLesson.objects.filter(published_capsule__isnull=False).count()
        pending_review = GeneratedLesson.objects.filter(status='draft').count()
        
        self.stdout.write(self.style.SUCCESS('Overall Statistics:'))
        self.stdout.write(f'  Total Chapters: {total_chapters}')
        self.stdout.write(f'  Total Lessons Generated: {total_lessons}')
        self.stdout.write(f'  Published Lessons: {published}')
        self.stdout.write(f'  Pending Review: {pending_review}')
        
        # Status breakdown
        by_status = {}
        for chapter in TextbookChapter.objects.values('status').distinct():
            status = chapter['status']
            count = TextbookChapter.objects.filter(status=status).count()
            by_status[status] = count
        
        self.stdout.write('\n  Chapter Status Breakdown:')
        for status, count in sorted(by_status.items()):
            self.stdout.write(f'    {status}: {count}')
