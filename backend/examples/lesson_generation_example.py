"""
Example: Using the AI-Assisted Lesson Generation Feature

This script demonstrates how to programmatically use the lesson generation
feature to transform textbook content into interactive lessons.
"""

from django.contrib.auth.models import User
from api.models import Subject, Grade, TextbookChapter, GeneratedLesson
from api.services import LessonGeneratorService


def example_1_create_and_generate_lesson():
    """
    Example 1: Upload a textbook chapter and generate a lesson
    """
    print("\n=== Example 1: Create and Generate Lesson ===\n")
    
    # Get or create subject and grade
    subject, _ = Subject.objects.get_or_create(
        name="Mathematics",
        defaults={'description': 'Mathematics curriculum'}
    )
    grade, _ = Grade.objects.get_or_create(
        name="Primary 5",
        defaults={'level': 5}
    )
    
    # Get admin user (or create one for testing)
    user = User.objects.filter(is_staff=True).first()
    if not user:
        user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )
    
    # Create a textbook chapter
    chapter = TextbookChapter.objects.create(
        title="Introduction to Fractions",
        subject=subject,
        grade=grade,
        chapter_number="Chapter 3",
        raw_content="""
        Fractions
        
        A fraction represents a part of a whole. When we divide something into equal
        parts, each part is called a fraction of the whole.
        
        Understanding Fractions
        
        The top number of a fraction is called the numerator. It tells us how many
        parts we have. The bottom number is called the denominator. It tells us how
        many equal parts the whole is divided into.
        
        For example, in the fraction 3/4:
        - 3 is the numerator (we have 3 parts)
        - 4 is the denominator (the whole is divided into 4 equal parts)
        
        Real-World Examples
        
        Fractions are everywhere in our daily lives:
        - Cutting a pizza into 8 slices means each slice is 1/8 of the whole pizza
        - If you drink half a glass of water, you've consumed 1/2 of the water
        - Sharing 3 oranges equally among 4 friends means each gets 3/4 of an orange
        
        Types of Fractions
        
        There are several types of fractions:
        1. Proper fractions: numerator is less than denominator (e.g., 2/5)
        2. Improper fractions: numerator is greater than denominator (e.g., 7/4)
        3. Mixed numbers: whole number and a fraction (e.g., 1 3/4)
        
        Practice Activities
        
        Try identifying fractions in your environment. Look for:
        - Divided shapes (circles, rectangles)
        - Measurements in recipes
        - Time on a clock (quarter past, half past)
        
        Remember: Fractions help us describe parts of things precisely!
        """,
        source_book="Mathematics for Primary 5",
        page_numbers="45-52",
        uploaded_by=user
    )
    
    print(f"✓ Created chapter: {chapter.title}")
    print(f"  Subject: {chapter.subject.name}")
    print(f"  Grade: {chapter.grade.name}")
    print(f"  Word count: {len(chapter.raw_content.split())}")
    
    # Initialize the lesson generator (offline mode)
    generator = LessonGeneratorService(use_openai=False)
    
    print("\n⚙ Generating lesson (offline mode)...")
    
    # Generate the lesson
    lesson = generator.generate_lesson_from_chapter(chapter)
    
    if lesson:
        print(f"\n✓ Lesson generated successfully!")
        print(f"  Title: {lesson.title}")
        print(f"  Status: {lesson.status}")
        print(f"  Sections: {lesson.sections.count()}")
        print(f"  Questions: {lesson.generated_questions.count()}")
        print(f"  Quality Score: {lesson.quality_score:.2f}")
        print(f"  Estimated Duration: {lesson.estimated_duration} minutes")
        
        # Display sections
        print("\n  Sections:")
        for section in lesson.sections.all():
            print(f"    - {section.section_type}: {section.title}")
        
        # Display questions
        print("\n  Questions:")
        for question in lesson.generated_questions.all()[:3]:
            print(f"    {question.order + 1}. [{question.question_type}] {question.question_text[:60]}...")
        
        return lesson
    else:
        print(f"\n✗ Lesson generation failed")
        print(f"  Error: {chapter.processing_notes}")
        return None


def example_2_review_and_publish(lesson):
    """
    Example 2: Review and publish a generated lesson
    """
    print("\n=== Example 2: Review and Publish Lesson ===\n")
    
    if not lesson:
        print("No lesson to review")
        return
    
    # Review and approve
    user = User.objects.filter(is_staff=True).first()
    
    lesson.status = 'approved'
    lesson.reviewed_by = user
    lesson.review_notes = "Content is accurate and well-structured. Approved for publication."
    from django.utils import timezone
    lesson.reviewed_at = timezone.now()
    lesson.save()
    
    print(f"✓ Lesson reviewed and approved")
    print(f"  Reviewer: {lesson.reviewed_by.username}")
    print(f"  Notes: {lesson.review_notes}")
    
    # Publish to curriculum capsule
    generator = LessonGeneratorService()
    
    print("\n⚙ Publishing to curriculum capsule...")
    capsule = generator.publish_lesson_to_capsule(lesson)
    
    if capsule:
        print(f"\n✓ Lesson published successfully!")
        print(f"  Capsule ID: {capsule.id}")
        print(f"  Title: {capsule.title}")
        print(f"  Published: {capsule.is_published}")
        print(f"  Quiz attached: {capsule.quizzes.count() > 0}")
        
        # Check quiz
        if capsule.quizzes.exists():
            quiz = capsule.quizzes.first()
            print(f"\n  Quiz Details:")
            print(f"    Title: {quiz.title}")
            print(f"    Questions: {quiz.questions.count()}")
            print(f"    Passing Score: {quiz.passing_score}%")
        
        return capsule
    else:
        print("\n✗ Publishing failed")
        return None


def example_3_batch_generation():
    """
    Example 3: Batch generate lessons for multiple chapters
    """
    print("\n=== Example 3: Batch Generation ===\n")
    
    # Get all uploaded chapters
    chapters = TextbookChapter.objects.filter(status='uploaded')[:3]
    
    if not chapters:
        print("No uploaded chapters available for batch processing")
        return
    
    print(f"Found {chapters.count()} chapters to process\n")
    
    generator = LessonGeneratorService(use_openai=False)
    results = {'success': [], 'failed': []}
    
    for i, chapter in enumerate(chapters, 1):
        print(f"[{i}/{chapters.count()}] Processing: {chapter.title}")
        
        lesson = generator.generate_lesson_from_chapter(chapter)
        
        if lesson:
            results['success'].append(lesson)
            print(f"  ✓ Success - {lesson.sections.count()} sections, {lesson.generated_questions.count()} questions")
        else:
            results['failed'].append(chapter)
            print(f"  ✗ Failed - {chapter.processing_notes}")
    
    print(f"\n=== Batch Results ===")
    print(f"✓ Successful: {len(results['success'])}")
    print(f"✗ Failed: {len(results['failed'])}")


def example_4_query_lessons():
    """
    Example 4: Query and filter generated lessons
    """
    print("\n=== Example 4: Query Generated Lessons ===\n")
    
    # Get all lessons
    total = GeneratedLesson.objects.count()
    print(f"Total lessons: {total}")
    
    # Filter by status
    pending = GeneratedLesson.objects.filter(status='draft').count()
    published = GeneratedLesson.objects.filter(published_capsule__isnull=False).count()
    
    print(f"Pending review: {pending}")
    print(f"Published: {published}")
    
    # Get high-quality lessons
    high_quality = GeneratedLesson.objects.filter(quality_score__gte=0.8)
    
    print(f"\nHigh-quality lessons (score >= 0.8): {high_quality.count()}")
    
    for lesson in high_quality[:3]:
        print(f"  - {lesson.title} (Score: {lesson.quality_score:.2f})")
    
    # Get lessons by subject
    from django.db.models import Count
    by_subject = GeneratedLesson.objects.values(
        'source_chapter__subject__name'
    ).annotate(count=Count('id'))
    
    print("\nLessons by subject:")
    for item in by_subject:
        print(f"  - {item['source_chapter__subject__name']}: {item['count']}")


def run_all_examples():
    """
    Run all examples in sequence
    """
    print("\n" + "="*60)
    print("AI-Assisted Lesson Generation - Examples")
    print("="*60)
    
    # Example 1: Create and generate
    lesson = example_1_create_and_generate_lesson()
    
    if lesson:
        # Example 2: Review and publish
        example_2_review_and_publish(lesson)
    
    # Example 3: Batch generation (if more chapters exist)
    example_3_batch_generation()
    
    # Example 4: Query lessons
    example_4_query_lessons()
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Note: This should be run in Django shell or as a management command
    # python manage.py shell < examples/lesson_generation_example.py
    
    import os
    import django
    
    # Setup Django environment (if running standalone)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jln_hub.settings')
    django.setup()
    
    run_all_examples()
