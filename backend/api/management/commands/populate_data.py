from django.core.management.base import BaseCommand
from api.models import Subject, Grade, CurriculumCapsule, Quiz, Question


class Command(BaseCommand):
    help = 'Populates the database with sample curriculum data for JLN Hub'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate database...'))

        # Create Subjects
        self.stdout.write('Creating subjects...')
        math_subject, _ = Subject.objects.get_or_create(
            name='Mathematics',
            defaults={
                'description': 'Learn numbers, algebra, geometry, and problem-solving skills',
                'icon': '🔢'
            }
        )
        
        english_subject, _ = Subject.objects.get_or_create(
            name='English',
            defaults={
                'description': 'Develop reading, writing, and communication skills',
                'icon': '📖'
            }
        )
        
        science_subject, _ = Subject.objects.get_or_create(
            name='Science',
            defaults={
                'description': 'Explore the natural world through physics, chemistry, and biology',
                'icon': '🔬'
            }
        )
        
        social_studies, _ = Subject.objects.get_or_create(
            name='Social Studies',
            defaults={
                'description': 'Learn about history, geography, and society',
                'icon': '🌍'
            }
        )

        # Create Grades
        self.stdout.write('Creating grades...')
        grades = []
        for i in range(1, 9):
            grade, _ = Grade.objects.get_or_create(
                level=i,
                defaults={
                    'name': f'Primary {i}',
                    'description': f'Primary level {i} curriculum'
                }
            )
            grades.append(grade)

        for i in range(1, 5):
            grade, _ = Grade.objects.get_or_create(
                level=i + 8,
                defaults={
                    'name': f'Secondary {i}',
                    'description': f'Secondary level {i} curriculum'
                }
            )
            grades.append(grade)

        # Create Sample Mathematics Lessons
        self.stdout.write('Creating Mathematics lessons...')
        
        math_capsule_1 = CurriculumCapsule.objects.create(
            title='Introduction to Addition',
            subject=math_subject,
            grade=grades[0],  # Primary 1
            description='Learn the basics of adding numbers together',
            content='''# Introduction to Addition

Addition is one of the basic operations in mathematics. When we add, we are combining numbers to find out how many we have in total.

## What is Addition?

Addition means putting things together. The symbol we use for addition is the plus sign (+).

## Basic Examples

Let's look at some simple examples:
- 1 + 1 = 2 (One plus one equals two)
- 2 + 3 = 5 (Two plus three equals five)
- 4 + 2 = 6 (Four plus two equals six)

## Real-Life Addition

Addition is used everywhere in daily life:
- If you have 2 mangoes and your friend gives you 3 more mangoes, you now have 5 mangoes (2 + 3 = 5)
- If there are 4 birds on a tree and 3 more birds come, there are now 7 birds (4 + 3 = 7)

## Practice

Try adding these numbers:
1. 3 + 2 = ?
2. 5 + 1 = ?
3. 2 + 2 = ?

Remember: Addition makes numbers bigger!''',
            objectives=['Understand the concept of addition', 'Add single-digit numbers', 'Solve simple word problems with addition'],
            order=1,
            estimated_duration=30,
            is_published=True
        )

        # Create quiz for Addition
        addition_quiz = Quiz.objects.create(
            capsule=math_capsule_1,
            title='Addition Practice Quiz',
            instructions='Answer the following questions about addition',
            passing_score=70
        )

        Question.objects.create(
            quiz=addition_quiz,
            question_text='What is 2 + 3?',
            question_type='multiple_choice',
            options=['4', '5', '6', '7'],
            correct_answer='5',
            explanation='When you add 2 and 3 together, you get 5.',
            points=1,
            order=1
        )

        Question.objects.create(
            quiz=addition_quiz,
            question_text='What is 4 + 1?',
            question_type='multiple_choice',
            options=['3', '4', '5', '6'],
            correct_answer='5',
            explanation='4 plus 1 equals 5.',
            points=1,
            order=2
        )

        Question.objects.create(
            quiz=addition_quiz,
            question_text='If you have 3 apples and get 2 more, how many apples do you have?',
            question_type='multiple_choice',
            options=['4', '5', '6', '7'],
            correct_answer='5',
            explanation='3 + 2 = 5. You have 5 apples in total.',
            points=1,
            order=3
        )

        # Create more Math lessons
        math_capsule_2 = CurriculumCapsule.objects.create(
            title='Introduction to Subtraction',
            subject=math_subject,
            grade=grades[0],
            description='Learn how to subtract numbers',
            content='''# Introduction to Subtraction

Subtraction is the opposite of addition. When we subtract, we are taking away or removing things.

## What is Subtraction?

Subtraction means taking away. The symbol we use for subtraction is the minus sign (-).

## Basic Examples

Let's look at some simple examples:
- 5 - 2 = 3 (Five minus two equals three)
- 4 - 1 = 3 (Four minus one equals three)
- 6 - 3 = 3 (Six minus three equals three)

## Real-Life Subtraction

Subtraction is used in daily life:
- If you have 5 oranges and eat 2, you have 3 oranges left (5 - 2 = 3)
- If there are 7 birds and 3 fly away, 4 birds remain (7 - 3 = 4)

Remember: Subtraction makes numbers smaller!''',
            objectives=['Understand subtraction concept', 'Subtract single-digit numbers', 'Solve simple subtraction problems'],
            order=2,
            estimated_duration=30,
            is_published=True
        )

        # Create English Lessons
        self.stdout.write('Creating English lessons...')
        
        english_capsule_1 = CurriculumCapsule.objects.create(
            title='The Alphabet - Letters A to Z',
            subject=english_subject,
            grade=grades[0],
            description='Learn all the letters of the English alphabet',
            content='''# The English Alphabet

The English alphabet has 26 letters. Each letter has two forms: uppercase (big letter) and lowercase (small letter).

## The Letters

A a - Apple
B b - Ball
C c - Cat
D d - Dog
E e - Elephant
F f - Fish
G g - Goat
H h - House
I i - Ice cream
J j - Jump
K k - Kite
L l - Lion
M m - Mango
N n - Nest
O o - Orange
P p - Pen
Q q - Queen
R r - Rabbit
S s - Sun
T t - Tree
U u - Umbrella
V v - Van
W w - Water
X x - X-ray
Y y - Yellow
Z z - Zebra

## Practice

Can you say the alphabet from A to Z?
Can you write both uppercase and lowercase letters?''',
            objectives=['Recognize all alphabet letters', 'Write uppercase and lowercase letters', 'Associate letters with common words'],
            order=1,
            estimated_duration=45,
            is_published=True
        )

        # Create Science Lessons
        self.stdout.write('Creating Science lessons...')
        
        science_capsule_1 = CurriculumCapsule.objects.create(
            title='Living and Non-Living Things',
            subject=science_subject,
            grade=grades[1],  # Primary 2
            description='Learn to identify living and non-living things',
            content='''# Living and Non-Living Things

Everything around us can be grouped into two categories: living things and non-living things.

## What are Living Things?

Living things are things that are alive. They have special characteristics:
- They grow
- They need food and water
- They breathe
- They can move
- They can reproduce (make babies)

Examples of Living Things:
- Plants (trees, flowers, grass)
- Animals (dogs, cats, birds, fish)
- People (you and me!)
- Insects (bees, ants, butterflies)

## What are Non-Living Things?

Non-living things are not alive. They do not grow, eat, breathe, or reproduce.

Examples of Non-Living Things:
- Rocks
- Water
- Books
- Cars
- Houses
- Chairs

## How to Tell the Difference

Ask yourself these questions:
1. Does it grow?
2. Does it need food?
3. Does it breathe?
4. Can it move by itself?

If the answer to most questions is yes, it's a living thing!
If the answer to most questions is no, it's a non-living thing!''',
            objectives=['Identify living things', 'Identify non-living things', 'List characteristics of living things'],
            order=1,
            estimated_duration=40,
            is_published=True
        )

        # Create quiz for Science
        science_quiz = Quiz.objects.create(
            capsule=science_capsule_1,
            title='Living vs Non-Living Quiz',
            instructions='Identify whether each item is living or non-living',
            passing_score=70
        )

        Question.objects.create(
            quiz=science_quiz,
            question_text='Is a tree a living thing?',
            question_type='multiple_choice',
            options=['Yes', 'No'],
            correct_answer='Yes',
            explanation='Trees are living things because they grow, need water, and can make seeds.',
            points=1,
            order=1
        )

        Question.objects.create(
            quiz=science_quiz,
            question_text='Is a rock a living thing?',
            question_type='multiple_choice',
            options=['Yes', 'No'],
            correct_answer='No',
            explanation='Rocks are non-living things. They do not grow, eat, or breathe.',
            points=1,
            order=2
        )

        # Create quiz for Subtraction
        self.stdout.write('Creating Subtraction quiz...')
        subtraction_quiz = Quiz.objects.create(
            capsule=math_capsule_2,
            title='Subtraction Practice Quiz',
            instructions='Answer these subtraction questions. Take away!',
            passing_score=70
        )

        Question.objects.create(
            quiz=subtraction_quiz,
            question_text='What is 5 - 2?',
            question_type='multiple_choice',
            options=['2', '3', '4', '5'],
            correct_answer='3',
            explanation='When you take 2 away from 5, you get 3.',
            points=1,
            order=1
        )

        Question.objects.create(
            quiz=subtraction_quiz,
            question_text='What is 7 - 3?',
            question_type='multiple_choice',
            options=['3', '4', '5', '6'],
            correct_answer='4',
            explanation='7 minus 3 equals 4.',
            points=1,
            order=2
        )

        Question.objects.create(
            quiz=subtraction_quiz,
            question_text='If you have 6 cookies and eat 2, how many are left?',
            question_type='multiple_choice',
            options=['2', '3', '4', '5'],
            correct_answer='4',
            explanation='6 - 2 = 4. You have 4 cookies left.',
            points=1,
            order=3
        )

        # Create quiz for English Alphabet
        self.stdout.write('Creating Alphabet quiz...')
        alphabet_quiz = Quiz.objects.create(
            capsule=english_capsule_1,
            title='Alphabet Recognition Quiz',
            instructions='Test your knowledge of the English alphabet!',
            passing_score=60
        )

        Question.objects.create(
            quiz=alphabet_quiz,
            question_text='What letter comes after B?',
            question_type='multiple_choice',
            options=['A', 'C', 'D', 'E'],
            correct_answer='C',
            explanation='The alphabet goes A, B, C. So C comes after B.',
            points=1,
            order=1
        )

        Question.objects.create(
            quiz=alphabet_quiz,
            question_text='What letter starts the word "Apple"?',
            question_type='multiple_choice',
            options=['A', 'B', 'P', 'E'],
            correct_answer='A',
            explanation='Apple starts with the letter A.',
            points=1,
            order=2
        )

        Question.objects.create(
            quiz=alphabet_quiz,
            question_text='How many letters are in the English alphabet?',
            question_type='multiple_choice',
            options=['24', '25', '26', '27'],
            correct_answer='26',
            explanation='The English alphabet has 26 letters from A to Z.',
            points=1,
            order=3
        )

        Question.objects.create(
            quiz=alphabet_quiz,
            question_text='What is the last letter of the alphabet?',
            question_type='multiple_choice',
            options=['X', 'Y', 'Z', 'W'],
            correct_answer='Z',
            explanation='Z is the 26th and last letter of the alphabet.',
            points=1,
            order=4
        )

        # Create quiz for Social Studies
        self.stdout.write('Creating Social Studies quiz...')
        social_quiz = Quiz.objects.create(
            capsule=social_capsule_1,
            title='Family and Community Quiz',
            instructions='Answer questions about families and communities',
            passing_score=70
        )

        Question.objects.create(
            quiz=social_quiz,
            question_text='Who helps us learn at school?',
            question_type='multiple_choice',
            options=['Doctors', 'Teachers', 'Shopkeepers', 'Farmers'],
            correct_answer='Teachers',
            explanation='Teachers are community helpers who help us learn at school.',
            points=1,
            order=1
        )

        Question.objects.create(
            quiz=social_quiz,
            question_text='Who grows food for us to eat?',
            question_type='multiple_choice',
            options=['Police officers', 'Nurses', 'Farmers', 'Teachers'],
            correct_answer='Farmers',
            explanation='Farmers grow crops and raise animals to provide us with food.',
            points=1,
            order=2
        )

        Question.objects.create(
            quiz=social_quiz,
            question_text='Who keeps us safe in the community?',
            question_type='multiple_choice',
            options=['Police officers', 'Shopkeepers', 'Farmers', 'Teachers'],
            correct_answer='Police officers',
            explanation='Police officers are community helpers who keep us safe.',
            points=1,
            order=3
        )

        # Create Social Studies Lesson
        self.stdout.write('Creating Social Studies lessons...')
        
        social_capsule_1 = CurriculumCapsule.objects.create(
            title='My Family and Community',
            subject=social_studies,
            grade=grades[0],
            description='Learn about families and communities',
            content='''# My Family and Community

We all belong to a family and live in a community. Let's learn about them!

## What is a Family?

A family is a group of people who love and care for each other. Families can be different sizes and types.

Family members can include:
- Parents (mother and father)
- Children (brothers and sisters)
- Grandparents
- Aunts and uncles
- Cousins

## What is a Community?

A community is a group of people living in the same area. Your community includes:
- Your neighbors
- Your school
- Local shops and markets
- Churches or mosques
- Health centers

## People Who Help Us

Many people in our community help us every day:
- Teachers help us learn
- Doctors and nurses help us stay healthy
- Police officers keep us safe
- Shopkeepers sell us things we need
- Farmers grow our food

## Being a Good Community Member

We can help our community by:
- Being kind to others
- Keeping our environment clean
- Helping neighbors when they need it
- Following rules
- Going to school to learn''',
            objectives=['Identify family members', 'Understand community roles', 'Recognize community helpers'],
            order=1,
            estimated_duration=35,
            is_published=True
        )

        self.stdout.write(self.style.SUCCESS('✓ Successfully populated database with sample data!'))
        self.stdout.write(self.style.SUCCESS(f'Created:'))
        self.stdout.write(f'  - 4 Subjects')
        self.stdout.write(f'  - 12 Grades')
        self.stdout.write(f'  - 6 Curriculum Capsules (Lessons)')
        self.stdout.write(f'  - 5 Quizzes with Questions')
        self.stdout.write(self.style.SUCCESS('\nYou can now:'))
        self.stdout.write('  1. Visit http://127.0.0.1:8000/ to see the lessons')
        self.stdout.write('  2. Visit http://127.0.0.1:8000/admin/ to add more content')
