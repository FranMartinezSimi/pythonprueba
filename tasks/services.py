from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SubtaskGenerator:
    def __init__(self):
        self.llm = OllamaLLM(model="llama2", base_url=settings.OLLAMA_API_URL)
    def generate(self, task_title: str, task_description: str) -> List[dict]:
        """Genera subtareas usando LangChain"""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """Eres un asistente experto en dividir tareas en subtareas manejables.

Reglas:
- Genera entre 3-6 subtareas
- Ordénalas lógicamente (lo primero que se debe hacer tiene order=1)
- Sé específico y accionable
- Estima tiempos realistas en minutos

{format_instructions}"""),
                ("user", """Tarea: {title}

Descripción: {description}

Genera las subtareas necesarias para completar esta tarea.""")
            ])
            
            chain = prompt | self.llm | self.parser
            
            result = chain.invoke({
                "title": task_title,
                "description": task_description,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            subtasks = [subtask.dict() for subtask in result.subtasks]
            logger.info(f"Generated {len(subtasks)} subtasks for: {task_title}")
            return subtasks
            
        except Exception as e:
            logger.error(f"Error generating subtasks: {str(e)}")
            # Retornar subtarea por defecto si falla
            return [{
                'title': 'Revisar y planificar tarea',
                'description': 'Analizar los requisitos y crear un plan de acción',
                'estimated_time': 30,
                'order': 1
            }]