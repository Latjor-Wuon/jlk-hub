from django.core.management.base import BaseCommand
from api.models import Subject, Grade, LearningSimulation, CurriculumCapsule


class Command(BaseCommand):
    help = 'Populates the database with sample learning simulations'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample learning simulations...'))

        # Get or create subjects and grades
        try:
            math_subject = Subject.objects.get(name='Mathematics')
        except Subject.DoesNotExist:
            math_subject = Subject.objects.create(
                name='Mathematics',
                description='Learn numbers, algebra, geometry, and problem-solving skills',
                icon='🔢'
            )

        try:
            science_subject = Subject.objects.get(name='Science')
        except Subject.DoesNotExist:
            science_subject = Subject.objects.create(
                name='Science',
                description='Explore the natural world through physics, chemistry, and biology',
                icon='🔬'
            )

        try:
            grade_p3 = Grade.objects.get(level=3)
        except Grade.DoesNotExist:
            grade_p3 = Grade.objects.create(name='Primary 3', level=3, description='Primary level 3')

        try:
            grade_p4 = Grade.objects.get(level=4)
        except Grade.DoesNotExist:
            grade_p4 = Grade.objects.create(name='Primary 4', level=4, description='Primary level 4')

        try:
            grade_p5 = Grade.objects.get(level=5)
        except Grade.DoesNotExist:
            grade_p5 = Grade.objects.create(name='Primary 5', level=5, description='Primary level 5')

        # Create Simulations
        simulations_data = [
            {
                'title': 'Fraction Visualizer',
                'description': 'Learn how fractions work by adjusting the numerator and denominator. See fractions displayed as pie charts and bar models.',
                'simulation_type': 'math_visualization',
                'subject': math_subject,
                'grade': grade_p3,
                'config': {
                    'type': 'fraction',
                    'interactive': True,
                    'components': ['numerator_slider', 'denominator_slider', 'pie_chart', 'bar_model'],
                    'initial_values': {'numerator': 1, 'denominator': 2}
                },
                'instructions': 'Move the sliders to change the fraction. Watch how the pie chart and bar model change to show different fractions.',
                'hints': [
                    'The numerator (top number) tells you how many parts you have.',
                    'The denominator (bottom number) tells you how many equal parts the whole is divided into.',
                    'When the numerator equals the denominator, you have one whole.',
                    'Try making the numerator larger than the denominator to see an improper fraction.'
                ],
                'learning_objectives': [
                    'Understand the relationship between numerator and denominator',
                    'Visualize fractions as parts of a whole',
                    'Compare fractions using visual models'
                ],
                'difficulty_level': 'beginner',
                'estimated_time': 10,
                'is_published': True
            },
            {
                'title': 'Multiplication Arrays',
                'description': 'Explore multiplication using arrays of dots. See how rows and columns relate to multiplication equations.',
                'simulation_type': 'math_visualization',
                'subject': math_subject,
                'grade': grade_p3,
                'config': {
                    'type': 'array',
                    'interactive': True,
                    'max_rows': 10,
                    'max_columns': 10,
                    'show_equation': True,
                    'show_skip_counting': True
                },
                'instructions': 'Adjust the number of rows and columns using the sliders. Count the total dots to see the multiplication result.',
                'hints': [
                    'An array shows equal groups arranged in rows and columns.',
                    'Count the number of rows and columns to find the multiplication equation.',
                    'Try skip counting by the number in each row.',
                    'Notice that 3 × 4 gives the same answer as 4 × 3 (commutative property).'
                ],
                'learning_objectives': [
                    'Visualize multiplication as equal groups',
                    'Use arrays to understand multiplication facts',
                    'Discover the commutative property of multiplication'
                ],
                'difficulty_level': 'beginner',
                'estimated_time': 10,
                'is_published': True
            },
            {
                'title': 'Water Cycle Simulation',
                'description': 'Explore how water moves through the environment in a continuous cycle of evaporation, condensation, precipitation, and collection.',
                'simulation_type': 'science_experiment',
                'subject': science_subject,
                'grade': grade_p4,
                'config': {
                    'type': 'cycle_diagram',
                    'interactive': True,
                    'stages': ['evaporation', 'condensation', 'precipitation', 'collection'],
                    'animations': True,
                    'clickable_elements': True
                },
                'instructions': 'Click on each stage of the water cycle to learn more. Watch how water transforms as it moves through the cycle.',
                'hints': [
                    'Watch what happens when the sun heats the water.',
                    'Notice how water vapor rises and cools to form clouds.',
                    'Precipitation can be rain, snow, sleet, or hail.',
                    'The cycle repeats continuously in nature.'
                ],
                'learning_objectives': [
                    'Understand the four main stages of the water cycle',
                    'Explain how the sun drives the water cycle',
                    'Describe the process of evaporation and condensation'
                ],
                'difficulty_level': 'intermediate',
                'estimated_time': 15,
                'is_published': True
            },
            {
                'title': 'Plant Growth Experiment',
                'description': 'Conduct a virtual experiment to see how water and sunlight affect plant growth.',
                'simulation_type': 'science_experiment',
                'subject': science_subject,
                'grade': grade_p4,
                'config': {
                    'type': 'growth_simulation',
                    'variables': ['water', 'sunlight', 'soil_type'],
                    'time_lapse': True,
                    'measurement_tools': ['ruler', 'timer'],
                    'stages': ['seed', 'germination', 'seedling', 'mature_plant']
                },
                'instructions': 'Adjust the water and sunlight levels, then click "Grow Plant" to see how your plant develops. Find the optimal conditions for healthy growth.',
                'hints': [
                    'Plants need water, sunlight, and nutrients to grow.',
                    'Too much or too little water can harm the plant.',
                    'Watch how the plant grows toward the light source.',
                    'Different parts of the plant grow at different rates.'
                ],
                'learning_objectives': [
                    'Identify what plants need to grow',
                    'Observe the stages of plant growth',
                    'Understand how changing variables affects plant growth'
                ],
                'difficulty_level': 'beginner',
                'estimated_time': 12,
                'is_published': True
            },
            {
                'title': 'Electric Circuit Builder',
                'description': 'Build simple electric circuits using batteries, bulbs, switches, and wires. Learn how electricity flows in a complete circuit.',
                'simulation_type': 'interactive_diagram',
                'subject': science_subject,
                'grade': grade_p5,
                'config': {
                    'type': 'circuit_builder',
                    'components': ['battery', 'bulb', 'switch', 'wire'],
                    'max_components': 10,
                    'show_current_flow': True
                },
                'instructions': 'Select components from the palette and build a circuit. Connect components with wires to make the bulb light up.',
                'hints': [
                    'A complete circuit needs a power source, like a battery.',
                    'The circuit must form a complete loop for electricity to flow.',
                    'A switch can break or complete the circuit.',
                    'If your bulb doesn\'t light, check if the circuit is complete.'
                ],
                'learning_objectives': [
                    'Build a simple electric circuit',
                    'Understand that electricity flows in a complete loop',
                    'Learn the function of switches in circuits'
                ],
                'difficulty_level': 'intermediate',
                'estimated_time': 15,
                'is_published': True
            },
            {
                'title': 'Place Value Explorer',
                'description': 'Understand place value by working with ones, tens, and hundreds. See how digits change value based on their position.',
                'simulation_type': 'math_visualization',
                'subject': math_subject,
                'grade': grade_p3,
                'config': {
                    'type': 'place_value',
                    'max_value': 999,
                    'show_blocks': True,
                    'show_expanded_form': True
                },
                'instructions': 'Use the buttons to add or remove blocks in the ones, tens, and hundreds columns. Watch how the number changes.',
                'hints': [
                    'Each column represents a different place value.',
                    'Ten ones equal one ten. Ten tens equal one hundred.',
                    'The digit in each column tells you how many of that value you have.',
                    'Try making the number 234 using blocks.'
                ],
                'learning_objectives': [
                    'Understand place value of ones, tens, and hundreds',
                    'Represent numbers using place value blocks',
                    'Write numbers in expanded form'
                ],
                'difficulty_level': 'beginner',
                'estimated_time': 10,
                'is_published': True
            }
        ]

        for sim_data in simulations_data:
            sim, created = LearningSimulation.objects.update_or_create(
                title=sim_data['title'],
                defaults=sim_data
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status}: {sim.title}')

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created/updated {len(simulations_data)} simulations!'
        ))
