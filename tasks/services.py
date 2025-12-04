from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from django.conf import settings
import logging
import json

logger = logging.getLogger(__name__)

class SubtaskGenerator:
    def __init__(self):
        """Initialize the Ollama LLM for subtask generation"""
        ollama_url = getattr(settings, 'OLLAMA_API_URL', 'http://ollama:11434')
        ollama_model = getattr(settings, 'OLLAMA_MODEL', 'llama3.2')
        self.llm = OllamaLLM(model=ollama_model, base_url=ollama_url)

    def generate(self, task_title: str, task_description: str, max_subtasks: int = 5):
        """Generate subtasks using LangChain and Ollama

        Args:
            task_title: The title of the main task
            task_description: The description of the main task
            max_subtasks: Maximum number of subtasks to generate (default: 5)

        Returns:
            List of dictionaries with subtask data
        """
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert assistant that breaks down tasks into manageable subtasks.

Rules:
- Generate between 3 and {max_subtasks} subtasks maximum
- Order them logically (first subtask should be done first)
- Be specific and actionable
- Each subtask should be clear and concise

You MUST respond with a valid JSON array of subtasks. Each subtask must have only a "title" field.
Example format:
[
  {{"title": "Research and gather requirements"}},
  {{"title": "Create initial design mockup"}},
  {{"title": "Implement core functionality"}}
]

Do not include any other text, only the JSON array."""),
                ("user", """Task: {title}

Description: {description}

Generate the necessary subtasks to complete this task. Remember to return ONLY a JSON array.""")
            ])

            # Create the chain
            chain = prompt | self.llm

            # Invoke the chain
            response = chain.invoke({
                "title": task_title,
                "description": task_description,
                "max_subtasks": max_subtasks
            })

            # Parse the JSON response
            try:
                # Clean up the response - remove markdown code blocks if present
                cleaned_response = response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response.replace("```json", "").replace("```", "").strip()
                elif cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response.replace("```", "").strip()

                subtasks_data = json.loads(cleaned_response)

                # Ensure it's a list and limit to max_subtasks
                if isinstance(subtasks_data, list):
                    subtasks_data = subtasks_data[:max_subtasks]
                    logger.info(f"Generated {len(subtasks_data)} subtasks for: {task_title}")
                    return subtasks_data
                else:
                    raise ValueError("Response is not a list")

            except (json.JSONDecodeError, ValueError) as parse_error:
                logger.error(f"Failed to parse LLM response: {parse_error}")
                logger.error(f"Raw response: {response}")
                raise

        except Exception as e:
            logger.error(f"Error generating subtasks: {str(e)}")
            # Return default subtask if generation fails
            return [
                {'title': 'Review and plan the task'},
                {'title': 'Break down into smaller steps'},
                {'title': 'Execute and complete the task'}
            ]