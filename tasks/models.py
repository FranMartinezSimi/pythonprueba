from django.db import models
from django.contrib.auth.models import User

status = [
    ('pending', 'Pending'),
    ('is_completed', 'Completed'),]

category = [
    ('work', 'Work'),
    ('personal', 'Personal'),
    ('urgent', 'Urgent'),
]

class Task(models.Model):
    """
    Task model
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=status, default='pending')
    category = models.CharField(max_length=20, choices=category, default='work')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        # indexes = [
        #     models.Index(fields=['user', 'status']),
        #     models.Index(fields=['user', 'category']),
        #     models.Index(fields=['user', '-created_at']),
        # ]
        db_table = 'tasks'

    def __str__(self):
        return f"{self.title} ({self.status})"

class SubTasks(models.Model):
    """
    SubTasks model
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'subtasks'

    def __str__(self):
        return f"{self.title} - {'Completed' if self.is_completed else 'Pending'}"