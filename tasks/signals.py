from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task, Subtask
from .services import SubtaskGenerator
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Task)
def create_subtasks(sender, instance, created, **kwargs):
    """Genera subtareas automáticamente al crear una tarea"""
    if not created:
        return
    
    generator = SubtaskGenerator()
    subtasks_data = generator.generate(
        task_title=instance.title,
        task_description=instance.description
    )
    
    # Crear subtareas
    for subtask_data in subtasks_data:
        Subtask.objects.create(task=instance, **subtask_data)
    
    logger.info(f"Created {len(subtasks_data)} subtasks for task {instance.id}")