"""
Test script to verify AI integration setup for JLN Hub
Run this to check if all AI components are properly configured
"""

import os
import sys

def test_ai_setup():
    print("=" * 60)
    print("JLN Hub AI Integration Setup Test")
    print("=" * 60)
    print()
    
    # Test 1: Check Python packages
    print("1. Testing AI Package Installation...")
    packages = {
        'transformers': 'Transformers (Hugging Face)',
        'torch': 'PyTorch',
        'openai': 'OpenAI API',
        'nltk': 'NLTK',
        'beautifulsoup4': 'BeautifulSoup',
        'dotenv': 'Python-dotenv'
    }
    
    all_installed = True
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"   ✅ {name} - Installed")
        except ImportError:
            print(f"   ❌ {name} - NOT installed")
            all_installed = False
    
    print()
    
    # Test 2: Check Django settings
    print("2. Testing Django Configuration...")
    try:
        # Add backend to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jln_hub.settings')
        
        import django
        django.setup()
        
        from django.conf import settings
        print("   ✅ Django settings loaded")
        
        # Check API keys
        openrouter_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        openai_key = getattr(settings, 'OPENAI_API_KEY', None)
        
        if openrouter_key:
            print(f"   ✅ OpenRouter API Key configured (starts with: {openrouter_key[:10]}...)")
        elif openai_key and openai_key != 'your-openai-api-key-here':
            print(f"   ✅ OpenAI API Key configured (starts with: {openai_key[:10]}...)")
        else:
            print("   ⚠️  No AI API Key configured (will use local models)")
        
    except Exception as e:
        print(f"   ❌ Error loading Django: {e}")
    
    print()
    
    # Test 3: Test AI API Connection
    print("3. Testing AI API Connection...")
    if openrouter_key:
        try:
            import openai
            client = openai.OpenAI(
                api_key=openrouter_key,
                base_url="https://openrouter.ai/api/v1"
            )
            
            # Simple test call with affordable model
            response = client.chat.completions.create(
                model="meta-llama/llama-3-8b-instruct",
                messages=[{"role": "user", "content": "Say 'AI is working!' if you can read this."}],
                max_tokens=20
            )
            
            result = response.choices[0].message.content
            print(f"   ✅ OpenRouter API working! Response: {result}")
            
        except Exception as e:
            print(f"   ❌ OpenRouter API error: {e}")
    elif openai_key and openai_key != 'your-openai-api-key-here':
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            
            # Simple test call
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say 'AI is working!' if you can read this."}],
                max_tokens=20
            )
            
            result = response.choices[0].message.content
            print(f"   ✅ OpenAI API working! Response: {result}")
            
        except Exception as e:
            print(f"   ❌ OpenAI API error: {e}")
    else:
        print("   ⚠️  Skipped (no API key configured)")
    
    print()
    
    # Test 4: Test Lesson Generator Service
    print("4. Testing Lesson Generator Service...")
    try:
        from api.services.lesson_generator import LessonGeneratorService
        
        generator = LessonGeneratorService()
        print(f"   ✅ LessonGeneratorService initialized")
        print(f"   📝 Using OpenAI: {generator.use_openai}")
        print(f"   📝 Transformers available: {generator.model_name is not None or 'TRANSFORMERS_AVAILABLE'}")
        
    except Exception as e:
        print(f"   ❌ Error initializing service: {e}")
    
    print()
    
    # Summary
    print("=" * 60)
    print("Summary:")
    print("=" * 60)
    
    if all_installed:
        print("✅ All required packages are installed")
    else:
        print("❌ Some packages are missing - run: pip install -r requirements.txt")
    
    if openai_key and openai_key != 'your-openai-api-key-here':
        print("✅ OpenAI API is configured")
        print("\n💡 To use AI lesson generation:")
        print("   1. Start server: python manage.py runserver")
        print("   2. Login as admin at http://localhost:8000/")
        print("   3. Click '✨ AI Lessons' in the menu")
        print("   4. Upload a textbook chapter and click 'Generate Lesson'")
    else:
        print("⚠️  OpenAI API key not set")
        print("\n💡 To enable AI:")
        print("   1. Get API key from: https://platform.openai.com/api-keys")
        print("   2. Edit backend/.env file")
        print("   3. Set: OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx")
        print("   4. Restart the server")
    
    print()

if __name__ == '__main__':
    test_ai_setup()
