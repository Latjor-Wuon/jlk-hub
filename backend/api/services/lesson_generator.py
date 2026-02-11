"""
AI-Assisted Interactive Lesson Generation Service

This service transforms raw textbook content into structured, interactive digital lessons
using pre-trained language models. Designed for offline use after initial content preparation.
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from api.models import (
    TextbookChapter, 
    GeneratedLesson, 
    LessonSection, 
    GeneratedQuestion
)

# Check if transformers is available (optional dependency)
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Check if OpenAI is available (optional, for content preparation)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class LessonGeneratorService:
    """
    Service for generating interactive lessons from textbook content.
    Uses AI models during content preparation phase, then stores results locally.
    """
    
    def __init__(self, use_openai: bool = False):
        """
        Initialize the lesson generator.
        
        Args:
            use_openai: If True and available, use OpenAI API. Otherwise use local models.
        """
        self.use_openai = use_openai and OPENAI_AVAILABLE
        self.model_name = None
        self.summarizer = None
        self.qa_generator = None
        
        if not self.use_openai and TRANSFORMERS_AVAILABLE:
            self._initialize_local_models()
    
    def _initialize_local_models(self):
        """Initialize local Hugging Face models for offline use"""
        try:
            # Using smaller models suitable for educational content
            self.model_name = "facebook/bart-large-cnn"
            # These models will be downloaded once and cached locally
            self.summarizer = pipeline(
                "summarization", 
                model="facebook/bart-large-cnn",
                device=-1  # Use CPU
            )
        except Exception as e:
            print(f"Warning: Could not initialize local models: {e}")
    
    def _call_openai(self, prompt: str, system_prompt: str = None, max_tokens: int = 2500) -> str:
        """Call OpenAI API for content generation with improved prompting"""
        if not self.use_openai:
            return ""
        
        try:
            client = openai.OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', None))
            
            default_system = """You are an expert educational content specialist with deep expertise in:
- Curriculum design and instructional pedagogy
- Converting raw textbook content into engaging, structured digital lessons
- Creating age-appropriate learning materials for students across different grade levels
- Identifying key concepts, learning objectives, and assessment points from educational text

Your task is to analyze and transform extracted PDF textbook content into well-structured, interactive digital lessons. 
Always maintain educational accuracy while making content engaging and accessible.
You must respond ONLY with valid JSON - no markdown, no code blocks, no explanations outside the JSON."""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt or default_system},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return ""
    
    def generate_lesson_from_chapter(
        self, 
        chapter: TextbookChapter,
        validate_only: bool = False
    ) -> Optional[GeneratedLesson]:
        """
        Main method to generate an interactive lesson from a textbook chapter.
        
        Args:
            chapter: TextbookChapter instance with raw content
            validate_only: If True, only validate content without generating
            
        Returns:
            GeneratedLesson instance or None if generation fails
        """
        if validate_only:
            return self._validate_chapter_content(chapter)
        
        try:
            # Update chapter status
            chapter.status = 'processing'
            chapter.save()
            
            # Extract structured information
            lesson_data = self._analyze_chapter_content(chapter)
            
            # Create the generated lesson
            lesson = GeneratedLesson.objects.create(
                source_chapter=chapter,
                title=lesson_data['title'],
                introduction=lesson_data['introduction'],
                learning_objectives=lesson_data['objectives'],
                key_concepts=lesson_data['key_concepts'],
                estimated_duration=lesson_data['estimated_duration'],
                difficulty_level=lesson_data['difficulty_level'],
                ai_model_used=self.model_name or 'rule-based',
                generation_params={'source': 'ai_assisted'},
                quality_score=lesson_data['quality_score']
            )
            
            # Generate sections
            self._generate_lesson_sections(lesson, lesson_data)
            
            # Generate questions
            self._generate_questions(lesson, lesson_data)
            
            # Update chapter status
            chapter.status = 'generated'
            chapter.save()
            
            return lesson
            
        except Exception as e:
            chapter.status = 'failed'
            chapter.processing_notes = f"Error: {str(e)}"
            chapter.save()
            print(f"Lesson generation failed: {e}")
            return None
    
    def _validate_chapter_content(self, chapter: TextbookChapter) -> Dict:
        """Validate if chapter content is suitable for lesson generation"""
        content = chapter.raw_content.strip()
        word_count = len(content.split())
        
        validation = {
            'is_valid': word_count >= 100,
            'word_count': word_count,
            'warnings': []
        }
        
        if word_count < 100:
            validation['warnings'].append("Content too short (minimum 100 words)")
        if word_count > 10000:
            validation['warnings'].append("Content very long, consider splitting")
            
        return validation
    
    def _analyze_chapter_content(self, chapter: TextbookChapter) -> Dict:
        """
        Analyze chapter content and extract structured information.
        This is the core AI processing step.
        """
        content = chapter.raw_content
        
        if self.use_openai:
            return self._analyze_with_openai(chapter, content)
        else:
            return self._analyze_with_rules(chapter, content)
    
    def _analyze_with_openai(self, chapter: TextbookChapter, content: str) -> Dict:
        """Use OpenAI to analyze and structure content with comprehensive prompting"""
        
        # Preprocess content for better AI understanding
        processed_content = self._preprocess_content_for_ai(content)
        
        # Truncate intelligently - keep beginning, middle, and end
        max_content_length = 8000
        if len(processed_content) > max_content_length:
            third = max_content_length // 3
            processed_content = (
                processed_content[:third] + 
                "\n\n[... middle content ...]\n\n" + 
                processed_content[len(processed_content)//2 - third//2 : len(processed_content)//2 + third//2] +
                "\n\n[... continued ...]\n\n" +
                processed_content[-third:]
            )
        
        prompt = f"""Analyze the following educational content extracted from a PDF textbook and transform it into a structured digital lesson.

CONTEXT:
- Subject: {chapter.subject.name}
- Grade Level: {chapter.grade.name} (Grade {chapter.grade.level})
- Chapter Title: {chapter.title}
- Source: {chapter.source_book or 'Textbook PDF'}

EXTRACTED CONTENT:
\"\"\"
{processed_content}
\"\"\"

YOUR TASK:
Carefully analyze the above content and create a comprehensive lesson structure. Pay attention to:
1. The main topic and subtopics
2. Key terminology and definitions
3. Examples and illustrations mentioned
4. Formulas, equations, or procedures
5. Any practice problems or exercises
6. Real-world applications

RESPOND WITH THIS EXACT JSON STRUCTURE:
{{
    "title": "Clear, engaging title for the lesson",
    "introduction": "A 2-3 sentence engaging introduction that hooks the student and explains what they'll learn",
    "learning_objectives": [
        "Students will be able to [specific, measurable outcome 1]",
        "Students will be able to [specific, measurable outcome 2]",
        "Students will be able to [specific, measurable outcome 3]"
    ],
    "key_concepts": [
        {{"term": "Concept Name", "definition": "Clear, student-friendly definition"}},
        {{"term": "Concept Name 2", "definition": "Clear, student-friendly definition"}}
    ],
    "sections": [
        {{
            "type": "introduction",
            "title": "Introduction",
            "content": "Opening content that introduces the topic",
            "order": 0
        }},
        {{
            "type": "explanation",
            "title": "Descriptive Section Title",
            "content": "Main explanatory content with clear explanations. Use simple language appropriate for the grade level. Include examples where relevant.",
            "order": 1
        }},
        {{
            "type": "example",
            "title": "Worked Example",
            "content": "Step-by-step example showing how to apply the concept",
            "order": 2
        }},
        {{
            "type": "practice",
            "title": "Practice Activity",
            "content": "Guided practice for students",
            "order": 3
        }},
        {{
            "type": "summary",
            "title": "Summary",
            "content": "Brief recap of key points learned",
            "order": 4
        }}
    ],
    "questions": [
        {{
            "type": "multiple_choice",
            "text": "Clear question text?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "explanation": "Why this answer is correct",
            "difficulty": "easy"
        }},
        {{
            "type": "multiple_choice",
            "text": "Another question testing different concept?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option B",
            "explanation": "Clear explanation",
            "difficulty": "medium"
        }},
        {{
            "type": "true_false",
            "text": "Statement to evaluate as true or false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "Why this is true/false",
            "difficulty": "easy"
        }}
    ],
    "real_world_applications": [
        "How this topic applies in everyday life or careers"
    ],
    "estimated_duration": 30,
    "difficulty_level": "intermediate"
}}

IMPORTANT GUIDELINES:
- Create at least 3-5 sections with meaningful content
- Generate at least 5 questions (mix of multiple_choice and true_false)
- Questions should directly test comprehension of the lesson content
- All content should be appropriate for Grade {chapter.grade.level} students
- Use clear, simple language
- If the content discusses specific facts, dates, formulas, or procedures, include them accurately
- difficulty_level should be "beginner" for grades 1-3, "intermediate" for grades 4-6, "advanced" for grades 7+
- estimated_duration should reflect actual lesson complexity (15-60 minutes)"""

        response = self._call_openai(prompt, max_tokens=3500)
        
        try:
            data = json.loads(response)
            return self._format_analysis_data(data, chapter)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            # Try to extract JSON from response if wrapped in markdown
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    return self._format_analysis_data(data, chapter)
                except:
                    pass
            # Fallback to rule-based if JSON parsing fails
            return self._analyze_with_rules(chapter, content)
    
    def _preprocess_content_for_ai(self, content: str) -> str:
        """
        Preprocess extracted PDF content to make it more understandable for AI.
        Cleans up common PDF extraction issues.
        """
        # Fix common PDF extraction issues
        processed = content
        
        # Fix hyphenated words split across lines
        processed = re.sub(r'(\w+)-\n(\w+)', r'\1\2', processed)
        
        # Remove excessive whitespace while preserving structure
        processed = re.sub(r' {3,}', '  ', processed)
        
        # Fix missing spaces after periods
        processed = re.sub(r'\.([A-Z])', r'. \1', processed)
        
        # Standardize bullet points
        processed = re.sub(r'^[\u2022\u2023\u25E6\u2043\u2219•●○◦▪▸►]\s*', '• ', processed, flags=re.MULTILINE)
        
        # Remove page numbers that appear alone
        processed = re.sub(r'^\d{1,3}\s*$', '', processed, flags=re.MULTILINE)
        
        # Clean up header/footer artifacts (common patterns)
        processed = re.sub(r'^(Chapter \d+|Page \d+|Copyright.*|All rights reserved.*)$', '', processed, flags=re.MULTILINE | re.IGNORECASE)
        
        # Consolidate multiple blank lines
        processed = re.sub(r'\n{3,}', '\n\n', processed)
        
        return processed.strip()
    
    def _analyze_with_rules(self, chapter: TextbookChapter, content: str) -> Dict:
        """
        Enhanced rule-based content analysis (fallback method).
        Works offline without AI models but produces better structured output.
        """
        # Preprocess content
        content = self._preprocess_content_for_ai(content)
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p.strip()) > 20]
        
        # Extract title
        title = chapter.title or self._extract_title(content)
        
        # Generate introduction
        introduction = self._generate_introduction(paragraphs, chapter)
        
        # Extract objectives with improved detection
        objectives = self._extract_objectives_enhanced(content, chapter)
        
        # Identify key concepts with definitions
        key_concepts = self._extract_key_concepts_enhanced(content, chapter)
        
        # Estimate duration based on content length and complexity
        word_count = len(content.split())
        estimated_duration = self._estimate_duration(word_count, chapter.grade.level)
        
        # Determine difficulty
        difficulty_level = self._determine_difficulty(chapter.grade.level)
        
        # Structure sections intelligently
        sections = self._structure_sections_enhanced(paragraphs, chapter, content)
        
        # Generate meaningful questions
        questions = self._generate_questions_enhanced(content, key_concepts, objectives, chapter)
        
        return {
            'title': title,
            'introduction': introduction,
            'objectives': objectives,
            'key_concepts': key_concepts,
            'estimated_duration': estimated_duration,
            'difficulty_level': difficulty_level,
            'sections': sections,
            'questions': questions,
            'quality_score': 0.75  # Improved rule-based quality score
        }
    
    def _extract_objectives_enhanced(self, content: str, chapter: TextbookChapter) -> List[str]:
        """Extract or generate meaningful learning objectives"""
        objectives = []
        
        # Look for objective markers
        patterns = [
            r'(?:objective|goal|aim|learn|understand)s?:?\s*(.+?)(?:\n|$)',
            r'(?:by the end|after completing|students will|you will).*?:?\s*(.+?)(?:\n|$)',
            r'(?:this (?:lesson|chapter|unit) (?:will|covers?|teaches?)).*?:?\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                obj = match.group(1).strip()
                if obj and 20 < len(obj) < 200:
                    objectives.append(obj.capitalize())
        
        # Remove duplicates
        objectives = list(dict.fromkeys(objectives))
        
        # If no objectives found, generate based on content
        if not objectives:
            # Generate from key sentences
            sentences = re.split(r'[.!?]+', content)
            important_sentences = [s.strip() for s in sentences if 30 < len(s.strip()) < 150][:3]
            
            objectives = [
                f"Understand the key concepts of {chapter.title}",
                f"Apply knowledge of {chapter.subject.name} to solve problems",
                f"Demonstrate comprehension through practice exercises"
            ]
            
            # Add content-specific objective if possible
            if important_sentences:
                objectives.insert(0, f"Explain {important_sentences[0][:80].lower()}")
        
        return objectives[:5]
    
    def _extract_key_concepts_enhanced(self, content: str, chapter: TextbookChapter) -> List[Dict]:
        """
        Identify key concepts with definitions from the content.
        Returns list of dicts with 'term' and 'definition'.
        """
        concepts = []
        
        # Look for definition patterns
        definition_patterns = [
            r'([A-Z][a-zA-Z\s]+)\s+(?:is|are|means?|refers?\s+to|can\s+be\s+defined\s+as)\s+([^.]+\.)',
            r'([A-Z][a-zA-Z\s]+):\s+([^.]+\.)',
            r'(?:A|The)\s+([a-zA-Z\s]+)\s+is\s+([^.]+\.)'
        ]
        
        for pattern in definition_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                term = match.group(1).strip()
                definition = match.group(2).strip()
                if 2 < len(term.split()) < 6 and len(definition) > 20:
                    concepts.append({
                        'term': term.title(),
                        'definition': definition[:200]
                    })
        
        # Also find frequently used terms (capitalized phrases)
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        word_freq = {}
        for word in words:
            if len(word) > 4 and word not in ['This', 'That', 'These', 'Those', 'Then', 'There']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Add frequent terms without definitions found
        frequent_terms = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        existing_terms = {c['term'].lower() for c in concepts}
        
        for term, freq in frequent_terms:
            if term.lower() not in existing_terms and freq >= 2:
                concepts.append({
                    'term': term,
                    'definition': f"A key concept in {chapter.subject.name} related to {chapter.title}"
                })
        
        return concepts[:8] if concepts else [
            {'term': 'Key Concept 1', 'definition': f'Important concept in {chapter.title}'},
            {'term': 'Key Concept 2', 'definition': f'Related concept in {chapter.subject.name}'}
        ]
    
    def _estimate_duration(self, word_count: int, grade_level: int) -> int:
        """Estimate lesson duration based on content and grade level"""
        # Younger students read slower
        words_per_minute = 100 if grade_level <= 3 else (150 if grade_level <= 6 else 200)
        reading_time = word_count // words_per_minute
        
        # Add time for activities and comprehension
        activity_time = max(10, reading_time // 2)
        
        total = reading_time + activity_time
        return min(60, max(15, total))  # Clamp between 15-60 minutes
    
    def _structure_sections_enhanced(self, paragraphs: List[str], chapter: TextbookChapter, full_content: str) -> List[Dict]:
        """Structure content into logical, well-organized sections"""
        sections = []
        
        # Check for existing headings in content
        headings = re.findall(r'^(?:##|###)\s+(.+)$', full_content, re.MULTILINE)
        
        # Create introduction from first substantial content
        intro_content = paragraphs[0] if paragraphs else f"Welcome to this lesson on {chapter.title}."
        sections.append({
            'type': 'introduction',
            'title': 'Introduction',
            'content': f"In this lesson, we will explore {chapter.title}. {intro_content[:400]}",
            'order': 0
        })
        
        # Process remaining paragraphs into sections
        current_section_content = []
        section_counter = 1
        
        for i, para in enumerate(paragraphs[1:], 1):
            if len(para) < 30:
                continue
                
            # Detect section type
            para_lower = para.lower()[:100]
            
            if any(word in para_lower for word in ['example', 'for instance', 'consider', 'let us', 'suppose']):
                # Flush current content and create example section
                if current_section_content:
                    sections.append({
                        'type': 'explanation',
                        'title': headings[section_counter-1] if section_counter <= len(headings) else f'Understanding {chapter.title}',
                        'content': '\n\n'.join(current_section_content),
                        'order': section_counter
                    })
                    section_counter += 1
                    current_section_content = []
                
                sections.append({
                    'type': 'example',
                    'title': 'Worked Example',
                    'content': para,
                    'order': section_counter
                })
                section_counter += 1
                
            elif any(word in para_lower for word in ['exercise', 'practice', 'try this', 'solve', 'calculate']):
                sections.append({
                    'type': 'practice',
                    'title': 'Practice Activity',
                    'content': para,
                    'order': section_counter
                })
                section_counter += 1
                
            else:
                current_section_content.append(para)
                
                # Create section every 3-4 paragraphs or when content gets long
                if len(current_section_content) >= 3 or sum(len(p) for p in current_section_content) > 1000:
                    sections.append({
                        'type': 'explanation',
                        'title': headings[section_counter-1] if section_counter <= len(headings) else f'Section {section_counter}: Key Concepts',
                        'content': '\n\n'.join(current_section_content),
                        'order': section_counter
                    })
                    section_counter += 1
                    current_section_content = []
        
        # Flush remaining content
        if current_section_content:
            sections.append({
                'type': 'explanation',
                'title': f'Additional Information',
                'content': '\n\n'.join(current_section_content),
                'order': section_counter
            })
            section_counter += 1
        
        # Add summary section
        summary_points = [s['title'] for s in sections if s['type'] == 'explanation'][:4]
        sections.append({
            'type': 'summary',
            'title': 'Summary',
            'content': f"In this lesson, you learned about {chapter.title}.\n\nKey topics covered:\n• " + '\n• '.join(summary_points) if summary_points else f"This lesson covered the essential concepts of {chapter.title}.",
            'order': section_counter
        })
        
        return sections
    
    def _generate_questions_enhanced(self, content: str, key_concepts: List[Dict], objectives: List[str], chapter: TextbookChapter) -> List[Dict]:
        """Generate meaningful practice questions based on content analysis"""
        questions = []
        
        # Extract facts and statements from content for questions
        sentences = re.split(r'[.!?]+', content)
        fact_sentences = [s.strip() for s in sentences if 30 < len(s.strip()) < 150 and not s.strip().startswith(('The', 'A ', 'An '))][:15]
        
        # Generate questions from key concepts
        for i, concept in enumerate(key_concepts[:3]):
            term = concept.get('term', '')
            definition = concept.get('definition', '')
            
            if term and definition:
                questions.append({
                    'type': 'multiple_choice',
                    'text': f"What is {term}?",
                    'options': [
                        definition[:100],
                        f"The opposite of {term.lower()}",
                        f"A type of unrelated concept",
                        f"None of the above"
                    ],
                    'correct_answer': definition[:100],
                    'explanation': f"{term} {definition}",
                    'difficulty': 'easy' if i == 0 else 'medium',
                    'order': i
                })
        
        # Generate questions from content sentences
        for i, sentence in enumerate(fact_sentences[:4]):
            # Create fill-in or comprehension question
            words = sentence.split()
            if len(words) > 5:
                questions.append({
                    'type': 'multiple_choice',
                    'text': f"According to the lesson, which statement is correct?",
                    'options': [
                        sentence[:100],
                        f"The opposite: {' '.join(words[:3])} is not {' '.join(words[-3:])}",
                        f"This topic is unrelated to {chapter.subject.name}",
                        f"The lesson did not discuss this"
                    ],
                    'correct_answer': sentence[:100],
                    'explanation': f"This is directly stated in the lesson content.",
                    'difficulty': 'medium',
                    'order': len(questions)
                })
        
        # Add true/false questions
        for i, obj in enumerate(objectives[:2]):
            questions.append({
                'type': 'true_false',
                'text': f"True or False: After this lesson, students should be able to {obj.lower()}",
                'options': ['True', 'False'],
                'correct_answer': 'True',
                'explanation': f"This is one of the learning objectives for this lesson.",
                'difficulty': 'easy',
                'order': len(questions)
            })
        
        # Ensure minimum questions
        while len(questions) < 5:
            questions.append({
                'type': 'multiple_choice',
                'text': f"What is the main topic of this lesson?",
                'options': [
                    chapter.title,
                    "An unrelated topic",
                    "Something not covered",
                    "None of the above"
                ],
                'correct_answer': chapter.title,
                'explanation': f"This lesson is about {chapter.title}.",
                'difficulty': 'easy',
                'order': len(questions)
            })
        
        return questions[:8]
    
    def _extract_title(self, content: str) -> str:
        """Extract or generate a title from content"""
        lines = content.split('\n')
        for line in lines[:5]:
            if line.strip() and len(line.strip()) < 100:
                return line.strip()
        return "New Lesson"
    
    def _generate_introduction(self, paragraphs: List[str], chapter: TextbookChapter) -> str:
        """Generate an engaging introduction"""
        if not paragraphs:
            return f"Welcome to this lesson on {chapter.subject.name}."
        
        first_para = paragraphs[0]
        if len(first_para) > 300:
            first_para = first_para[:300] + "..."
        
        intro = f"In this lesson, we'll explore {chapter.title}. {first_para}"
        return intro[:500]
    
    def _extract_objectives(self, content: str) -> List[str]:
        """Extract learning objectives from content"""
        objectives = []
        
        # Look for objective markers
        patterns = [
            r'(?:objective|goal|aim|learn|understand)s?:?\s*(.+?)(?:\n|$)',
            r'(?:by the end|after completing|students will).*?:?\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content.lower(), re.IGNORECASE)
            for match in matches:
                obj = match.group(1).strip()
                if obj and len(obj) < 200:
                    objectives.append(obj.capitalize())
        
        # If no objectives found, generate generic ones
        if not objectives:
            objectives = [
                "Understand the main concepts presented in this lesson",
                "Apply the learned principles to solve problems",
                "Demonstrate comprehension through practice exercises"
            ]
        
        return objectives[:5]
    
    def _extract_key_concepts(self, content: str, chapter: TextbookChapter) -> List[str]:
        """Identify key concepts from the content"""
        # Simple approach: find frequently used terms (excluding common words)
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        
        # Count frequency
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top concepts
        concepts = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        key_concepts = [concept[0] for concept in concepts[:8]]
        
        return key_concepts if key_concepts else ["Key Concept 1", "Key Concept 2"]
    
    def _determine_difficulty(self, grade_level: int) -> str:
        """Determine difficulty level based on grade"""
        if grade_level <= 3:
            return 'beginner'
        elif grade_level <= 6:
            return 'intermediate'
        else:
            return 'advanced'
    
    def _structure_sections(self, paragraphs: List[str], chapter: TextbookChapter) -> List[Dict]:
        """Structure content into logical sections"""
        sections = []
        
        # Always include introduction section
        sections.append({
            'type': 'introduction',
            'title': 'Introduction',
            'content': paragraphs[0] if paragraphs else '',
            'order': 0
        })
        
        # Main explanation sections
        for i, para in enumerate(paragraphs[1:], 1):
            if len(para) > 50:  # Only meaningful paragraphs
                section_type = 'explanation'
                if 'example' in para.lower()[:50]:
                    section_type = 'example'
                elif 'practice' in para.lower()[:50] or 'exercise' in para.lower()[:50]:
                    section_type = 'practice'
                
                sections.append({
                    'type': section_type,
                    'title': f'Section {i}',
                    'content': para,
                    'order': i
                })
        
        # Add summary section
        if len(paragraphs) > 1:
            sections.append({
                'type': 'summary',
                'title': 'Summary',
                'content': self._generate_summary(paragraphs),
                'order': len(sections)
            })
        
        return sections
    
    def _generate_summary(self, paragraphs: List[str]) -> str:
        """Generate a summary of the lesson"""
        # Simple summary: take key sentences
        summary = "In this lesson, we covered the following key points:\n\n"
        summary += "• " + "\n• ".join([p[:100] + "..." for p in paragraphs[:3]])
        return summary
    
    def _generate_questions_rule_based(self, content: str, objectives: List[str]) -> List[Dict]:
        """Generate practice questions based on content"""
        questions = []
        
        # Extract potential question topics from content
        sentences = re.split(r'[.!?]+', content)
        important_sentences = [s.strip() for s in sentences if len(s.strip()) > 30][:10]
        
        # Generate different types of questions
        for i, sentence in enumerate(important_sentences[:5]):
            # Multiple choice question
            questions.append({
                'type': 'multiple_choice',
                'text': f"What does the following statement describe: '{sentence[:80]}...'?",
                'options': [
                    'Option A - Related concept',
                    'Option B - Another aspect',
                    'Option C - Different topic',
                    'Option D - Alternative explanation'
                ],
                'correct_answer': 'Option A - Related concept',
                'explanation': 'This relates to the main concept discussed.',
                'difficulty': 'medium',
                'order': i
            })
        
        # Add true/false questions
        if objectives:
            questions.append({
                'type': 'true_false',
                'text': f"True or False: {objectives[0]}",
                'options': ['True', 'False'],
                'correct_answer': 'True',
                'explanation': 'This is one of the learning objectives.',
                'difficulty': 'easy',
                'order': len(questions)
            })
        
        return questions
    
    def _generate_lesson_sections(self, lesson: GeneratedLesson, lesson_data: Dict):
        """Create LessonSection objects from analyzed data"""
        sections = lesson_data.get('sections', [])
        
        for section_data in sections:
            LessonSection.objects.create(
                lesson=lesson,
                section_type=section_data.get('type', 'explanation'),
                title=section_data.get('title', 'Section'),
                content=section_data.get('content', ''),
                order=section_data.get('order', 0),
                has_interactive_elements=False,
                interactive_data={},
                embedded_questions=[]
            )
    
    def _generate_questions(self, lesson: GeneratedLesson, lesson_data: Dict):
        """Create GeneratedQuestion objects"""
        questions = lesson_data.get('questions', [])
        
        for q_data in questions:
            GeneratedQuestion.objects.create(
                lesson=lesson,
                question_text=q_data.get('text', ''),
                question_type=q_data.get('type', 'multiple_choice'),
                difficulty_level=q_data.get('difficulty', 'medium'),
                options=q_data.get('options', []),
                correct_answer=q_data.get('correct_answer', ''),
                explanation=q_data.get('explanation', ''),
                order=q_data.get('order', 0)
            )
    
    def _format_analysis_data(self, data: Dict, chapter: TextbookChapter) -> Dict:
        """Format AI response data into standard structure with validation"""
        
        # Handle key_concepts which can be list of strings or list of dicts
        raw_concepts = data.get('key_concepts', [])
        if raw_concepts and isinstance(raw_concepts[0], dict):
            # Already in dict format
            key_concepts = [c.get('term', str(c)) for c in raw_concepts]
        else:
            # List of strings
            key_concepts = raw_concepts
        
        # Extract sections with validation
        sections = []
        raw_sections = data.get('sections', [])
        for i, section in enumerate(raw_sections):
            sections.append({
                'type': section.get('type', 'explanation'),
                'title': section.get('title', f'Section {i+1}'),
                'content': section.get('content', ''),
                'order': section.get('order', i)
            })
        
        # Extract questions with validation  
        questions = []
        raw_questions = data.get('questions', [])
        for i, q in enumerate(raw_questions):
            questions.append({
                'type': q.get('type', 'multiple_choice'),
                'text': q.get('text', ''),
                'options': q.get('options', []),
                'correct_answer': q.get('correct_answer', ''),
                'explanation': q.get('explanation', ''),
                'difficulty': q.get('difficulty', 'medium'),
                'order': q.get('order', i)
            })
        
        # Validate and normalize difficulty level
        difficulty = data.get('difficulty_level', 'intermediate').lower()
        if difficulty not in ['beginner', 'intermediate', 'advanced']:
            difficulty = 'intermediate'
        
        # Validate duration
        duration = data.get('estimated_duration', 30)
        try:
            duration = int(duration)
            duration = min(60, max(15, duration))
        except (ValueError, TypeError):
            duration = 30
        
        return {
            'title': data.get('title', chapter.title) or chapter.title,
            'introduction': data.get('introduction', '') or f"Welcome to this lesson on {chapter.title}.",
            'objectives': data.get('learning_objectives', []) or ['Understand the key concepts presented'],
            'key_concepts': key_concepts or ['Key Concept 1'],
            'estimated_duration': duration,
            'difficulty_level': difficulty,
            'sections': sections,
            'questions': questions,
            'real_world_applications': data.get('real_world_applications', []),
            'quality_score': 0.9  # Higher score for AI-generated content
        }
    
    def publish_lesson_to_capsule(self, lesson: GeneratedLesson) -> Optional['CurriculumCapsule']:
        """
        Convert a GeneratedLesson to a published CurriculumCapsule.
        This makes the lesson available to students.
        """
        from api.models import CurriculumCapsule, Quiz, Question
        
        try:
            # Create or update capsule
            if lesson.published_capsule:
                capsule = lesson.published_capsule
            else:
                capsule = CurriculumCapsule.objects.create(
                    title=lesson.title,
                    subject=lesson.source_chapter.subject,
                    grade=lesson.source_chapter.grade,
                    description=lesson.introduction,
                    content=self._compile_lesson_content(lesson),
                    objectives=lesson.learning_objectives,
                    estimated_duration=lesson.estimated_duration,
                    is_published=True
                )
                lesson.published_capsule = capsule
                lesson.status = 'published'
                lesson.save()
            
            # Create quiz from generated questions
            if lesson.generated_questions.exists():
                quiz = Quiz.objects.create(
                    capsule=capsule,
                    title=f"{lesson.title} - Practice Quiz",
                    instructions="Answer the following questions to test your understanding.",
                    passing_score=70
                )
                
                for gen_q in lesson.generated_questions.all():
                    Question.objects.create(
                        quiz=quiz,
                        question_text=gen_q.question_text,
                        question_type=gen_q.question_type,
                        options=gen_q.options,
                        correct_answer=gen_q.correct_answer,
                        explanation=gen_q.explanation,
                        points=gen_q.points,
                        order=gen_q.order
                    )
            
            # Update source chapter
            lesson.source_chapter.status = 'published'
            lesson.source_chapter.save()
            
            return capsule
            
        except Exception as e:
            print(f"Publishing failed: {e}")
            return None
    
    def _compile_lesson_content(self, lesson: GeneratedLesson) -> str:
        """Compile all sections into formatted lesson content"""
        content_parts = [
            f"# {lesson.title}\n\n",
            f"## Introduction\n{lesson.introduction}\n\n",
            f"## Learning Objectives\n"
        ]
        
        for obj in lesson.learning_objectives:
            content_parts.append(f"• {obj}\n")
        
        content_parts.append("\n")
        
        # Add all sections
        for section in lesson.sections.all():
            content_parts.append(f"## {section.title}\n")
            content_parts.append(f"{section.content}\n\n")
        
        # Add key concepts
        if lesson.key_concepts:
            content_parts.append("## Key Concepts\n")
            for concept in lesson.key_concepts:
                content_parts.append(f"• {concept}\n")
        
        return "".join(content_parts)
