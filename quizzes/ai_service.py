"""
AI Service for Quiz Generation using Google Gemini
"""
import json
import os
import google.generativeai as genai
from django.conf import settings


class GeminiQuizGenerator:
    """Service class to generate quizzes using Google Gemini AI"""
    
    def __init__(self):
        # Configure Gemini API
        api_key = "AIzaSyBA9HE8-IWysfzqXFQiVrRL2kdCWK51xKw"
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def generate_quiz(self, subject: str, user_prompt: str) -> dict:
        """
        Generate a quiz with 10 multiple choice questions
        
        Args:
            subject: The subject/topic of the quiz
            user_prompt: User's detailed prompt for quiz generation
            
        Returns:
            dict: Quiz data with questions in JSON format
        """
        
        # Create a detailed prompt for Gemini
        prompt = f"""Generate a quiz with EXACTLY 10 multiple choice questions about: {subject}

User's specific requirements: {user_prompt}

IMPORTANT INSTRUCTIONS:
1. Generate EXACTLY 10 questions
2. Each question must have 4 options (A, B, C, D)
3. Only ONE option should be correct
4. Return the response ONLY as valid JSON with no additional text
5. Use this EXACT JSON structure:

{{
    "title": "Quiz title here",
    "subject": "{subject}",
    "questions": [
        {{
            "question_text": "Question text here?",
            "option_a": "First option",
            "option_b": "Second option",
            "option_c": "Third option",
            "option_d": "Fourth option",
            "correct_answer": "A"
        }}
    ]
}}

Requirements:
- Make questions clear and unambiguous
- Ensure options are distinct and plausible
- Vary the correct answer position (don't always make A correct)
- Questions should test understanding, not just memorization
- Difficulty should be appropriate for the topic

Return ONLY the JSON object, no markdown formatting, no explanation, no additional text."""

        try:
            # Generate content using Gemini
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON response
            quiz_data = json.loads(response_text)
            
            # Validate the structure
            if 'questions' not in quiz_data:
                raise ValueError("Invalid quiz format: missing 'questions' key")
            
            if len(quiz_data['questions']) != 10:
                raise ValueError(f"Expected 10 questions, got {len(quiz_data['questions'])}")
            
            # Validate each question
            for idx, question in enumerate(quiz_data['questions'], 1):
                required_fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
                for field in required_fields:
                    if field not in question:
                        raise ValueError(f"Question {idx} missing required field: {field}")
                
                # Validate correct_answer is A, B, C, or D
                if question['correct_answer'].upper() not in ['A', 'B', 'C', 'D']:
                    raise ValueError(f"Question {idx} has invalid correct_answer: {question['correct_answer']}")
                
                # Normalize correct_answer to uppercase
                question['correct_answer'] = question['correct_answer'].upper()
            
            return quiz_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}\nResponse: {response_text[:200]}")
        except Exception as e:
            raise ValueError(f"Error generating quiz: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test if Gemini API connection is working"""
        try:
            response = self.model.generate_content("Say 'OK' if you can read this.")
            return bool(response.text)
        except Exception:
            return False

