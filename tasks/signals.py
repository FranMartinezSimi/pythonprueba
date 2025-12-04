from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task, SubTasks
from .services import SubtaskGenerator
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Task)
def create_subtasks(sender, instance, created, **kwargs):
    """Generate subtasks automatically when a task is created"""
    if not created:
        return

    try:
        generator = SubtaskGenerator()
        subtasks_data = generator.generate(
            task_title=instance.title,
            task_description=instance.description,
            max_subtasks=5
        )

        # Create subtasks
        for subtask_data in subtasks_data:
            SubTasks.objects.create(task=instance, **subtask_data)

        logger.info(f"Created {len(subtasks_data)} subtasks for task {instance.id}")
    except Exception as e:
        logger.error(f"Failed to create subtasks for task {instance.id}: {str(e)}")