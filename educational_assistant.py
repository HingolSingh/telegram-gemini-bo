"""
Educational assistant for learning and teaching support.
"""
import logging
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class EducationalAssistant:
    """Comprehensive educational assistance system."""
    
    def __init__(self, ai_client):
        self.ai_client = ai_client
        self.learning_topics = {
            'mathematics': {
                'subtopics': ['algebra', 'geometry', 'calculus', 'statistics', 'trigonometry'],
                'difficulty_levels': ['beginner', 'intermediate', 'advanced']
            },
            'science': {
                'subtopics': ['physics', 'chemistry', 'biology', 'earth science', 'astronomy'],
                'difficulty_levels': ['elementary', 'high school', 'college', 'advanced']
            },
            'programming': {
                'subtopics': ['python', 'javascript', 'web development', 'data structures', 'algorithms'],
                'difficulty_levels': ['beginner', 'intermediate', 'advanced', 'expert']
            },
            'languages': {
                'subtopics': ['english', 'spanish', 'french', 'german', 'mandarin'],
                'difficulty_levels': ['basic', 'intermediate', 'advanced', 'fluent']
            },
            'history': {
                'subtopics': ['world history', 'american history', 'ancient civilizations', 'modern history'],
                'difficulty_levels': ['overview', 'detailed', 'scholarly']
            }
        }
    
    async def generate_lesson(self, topic: str, user_id: int, difficulty: str = "intermediate") -> str:
        """Generate a comprehensive lesson on a topic."""
        try:
            # Analyze topic and determine best approach
            main_topic, subtopic = self._parse_topic(topic)
            
            lesson_prompt = f"""
Create a comprehensive educational lesson on "{topic}" for {difficulty} level.

Structure the lesson with:
1. **Overview** - Brief introduction to the topic
2. **Key Concepts** - Main ideas and definitions
3. **Detailed Explanation** - Core content with examples
4. **Practice Questions** - 3-5 questions to test understanding
5. **Real-world Applications** - How this applies in practice
6. **Further Learning** - Suggested next topics or resources

Make it engaging, clear, and appropriate for the {difficulty} level.
Use markdown formatting for better readability.
Include specific examples and step-by-step explanations where helpful.
"""
            
            lesson_content = await self.ai_client.generate_response(
                lesson_prompt,
                model="gemini"  # Use free model for education
            )
            
            return lesson_content
            
        except Exception as e:
            logger.error(f"Error generating lesson: {e}")
            return "Sorry, I encountered an error while creating the lesson. Please try again."
    
    async def handle_question(self, question: str, user_id: int) -> str:
        """Handle educational questions with detailed explanations."""
        try:
            # Detect if this is an educational query
            educational_keywords = [
                'explain', 'what is', 'how does', 'why does', 'what are',
                'define', 'describe', 'teach me', 'help me understand',
                'how to', 'what happens when', 'difference between'
            ]
            
            is_educational = any(keyword in question.lower() for keyword in educational_keywords)
            
            if is_educational:
                educational_prompt = f"""
You are an educational assistant. Answer this question with a comprehensive explanation:

"{question}"

Provide:
1. **Direct Answer** - Clear, concise response
2. **Detailed Explanation** - Step-by-step breakdown
3. **Examples** - Concrete examples to illustrate
4. **Context** - Why this is important or relevant
5. **Related Concepts** - Connected topics to explore

Use simple language and provide visual examples when helpful.
Format your response in markdown for clarity.
"""
                
                response = await self.ai_client.generate_response(
                    educational_prompt,
                    model="gemini"
                )
                
                return f"🎓 **Educational Response:**\n\n{response}"
            else:
                # Regular conversation
                return await self.ai_client.generate_response(question, model="gemini")
                
        except Exception as e:
            logger.error(f"Error handling educational question: {e}")
            return "I'm having trouble processing your question. Please try rephrasing it."
    
    async def create_quiz(self, topic: str, difficulty: str = "intermediate", 
                         num_questions: int = 5) -> str:
        """Create a quiz on a specific topic."""
        try:
            quiz_prompt = f"""
Create a {difficulty} level quiz on "{topic}" with {num_questions} questions.

Format:
**Quiz: {topic}**
**Difficulty: {difficulty.title()}**

For each question:
**Question X:** [Question text]
A) [Option A]
B) [Option B] 
C) [Option C]
D) [Option D]

At the end, provide:
**Answer Key:**
1. [Correct answer with brief explanation]
2. [Correct answer with brief explanation]
etc.

Make questions challenging but fair for the {difficulty} level.
Include a mix of question types (multiple choice, conceptual, application).
"""
            
            quiz_content = await self.ai_client.generate_response(
                quiz_prompt,
                model="gemini"
            )
            
            return quiz_content
            
        except Exception as e:
            logger.error(f"Error creating quiz: {e}")
            return "Sorry, I couldn't create the quiz. Please try again."
    
    async def explain_concept(self, concept: str, level: str = "simple") -> str:
        """Explain a specific concept at different complexity levels."""
        try:
            if level == "simple":
                explanation_style = "Explain like I'm 12 years old, using simple words and analogies"
            elif level == "detailed":
                explanation_style = "Provide a comprehensive explanation with technical details"
            elif level == "advanced":
                explanation_style = "Give an in-depth, technical explanation suitable for experts"
            else:
                explanation_style = "Provide a balanced explanation suitable for general audience"
            
            concept_prompt = f"""
{explanation_style}.

Concept to explain: "{concept}"

Structure your explanation:
1. **Simple Definition** - What it is in basic terms
2. **Key Components** - Main parts or aspects
3. **How It Works** - Process or mechanism
4. **Examples** - Real-world examples
5. **Why It Matters** - Importance or applications

Use analogies and examples to make it clear and memorable.
"""
            
            explanation = await self.ai_client.generate_response(
                concept_prompt,
                model="gemini"
            )
            
            return f"📚 **Concept Explanation: {concept}**\n\n{explanation}"
            
        except Exception as e:
            logger.error(f"Error explaining concept: {e}")
            return "I'm having trouble explaining that concept. Please try again."
    
    async def create_study_plan(self, subject: str, timeframe: str = "1 month", 
                              level: str = "beginner") -> str:
        """Create a personalized study plan."""
        try:
            study_plan_prompt = f"""
Create a {timeframe} study plan for learning {subject} at {level} level.

Structure the plan:
**Study Plan: {subject}**
**Duration: {timeframe}**
**Level: {level.title()}**

**Week-by-Week Breakdown:**
Week 1: [Topics and goals]
Week 2: [Topics and goals]
etc.

**Daily Schedule:**
- Time recommendations
- Study techniques
- Practice exercises
- Review sessions

**Resources:**
- Recommended materials
- Online resources
- Practice platforms

**Milestones:**
- What you should achieve each week
- Assessment checkpoints

**Tips for Success:**
- Study strategies
- Common pitfalls to avoid
- Motivation techniques

Make it practical, achievable, and well-structured.
"""
            
            study_plan = await self.ai_client.generate_response(
                study_plan_prompt,
                model="gemini"
            )
            
            return study_plan
            
        except Exception as e:
            logger.error(f"Error creating study plan: {e}")
            return "Sorry, I couldn't create the study plan. Please try again."
    
    async def solve_problem_step_by_step(self, problem: str, subject: str = None) -> str:
        """Solve problems with detailed step-by-step solutions."""
        try:
            solution_prompt = f"""
Solve this problem step-by-step with detailed explanations:

Problem: "{problem}"
{f"Subject: {subject}" if subject else ""}

Provide:
**Problem Analysis:**
- What is being asked
- What information is given
- What approach to use

**Step-by-Step Solution:**
Step 1: [Detailed explanation of first step]
Step 2: [Detailed explanation of second step]
etc.

**Final Answer:** [Clear final result]

**Verification:** [Check if the answer makes sense]

**Alternative Methods:** [Other ways to solve this, if applicable]

Show all work clearly and explain the reasoning behind each step.
"""
            
            solution = await self.ai_client.generate_response(
                solution_prompt,
                model="gemini"
            )
            
            return f"🔧 **Problem Solution:**\n\n{solution}"
            
        except Exception as e:
            logger.error(f"Error solving problem: {e}")
            return "I'm having trouble solving that problem. Please try rephrasing it."
    
    def _parse_topic(self, topic: str) -> tuple:
        """Parse topic to identify main subject and subtopic."""
        topic_lower = topic.lower()
        
        main_topic = "general"
        subtopic = topic
        
        for main, data in self.learning_topics.items():
            if main in topic_lower:
                main_topic = main
                for sub in data['subtopics']:
                    if sub in topic_lower:
                        subtopic = sub
                        break
                break
        
        return main_topic, subtopic
    
    async def get_learning_path(self, subject: str, current_level: str = "beginner") -> str:
        """Suggest a learning path for a subject."""
        try:
            path_prompt = f"""
Create a comprehensive learning path for {subject} starting from {current_level} level.

**Learning Path: {subject}**
**Starting Level: {current_level.title()}**

**Phase 1: Foundation** (Beginner)
- Core concepts to master
- Essential skills
- Time estimate

**Phase 2: Building Skills** (Intermediate) 
- Advanced concepts
- Practical applications
- Projects to complete

**Phase 3: Mastery** (Advanced)
- Expert-level topics
- Specializations
- Real-world challenges

**Assessment Points:**
- How to know you're ready for the next phase
- Self-assessment questions
- Portfolio projects

**Career Applications:**
- How these skills apply professionally
- Related career paths

Make it progressive and practical with clear milestones.
"""
            
            learning_path = await self.ai_client.generate_response(
                path_prompt,
                model="gemini"
            )
            
            return learning_path
            
        except Exception as e:
            logger.error(f"Error creating learning path: {e}")
            return "Sorry, I couldn't create the learning path. Please try again."