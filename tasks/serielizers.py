from rest_framework import serializers
from .models import Task, SubTasks
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer para listar/obtener información de usuarios"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuarios con contraseña"""
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar usuarios"""
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']


# ==================== SUBTASK SERIALIZERS ====================

class SubTaskSerializer(serializers.ModelSerializer):
    """Serializer para listar/obtener subtareas"""
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = SubTasks
        fields = ['id', 'task', 'task_title', 'title', 'is_completed', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubTaskCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear subtareas"""
    class Meta:
        model = SubTasks
        fields = ['task', 'title', 'is_completed']
    
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("El título debe tener al menos 3 caracteres")
        return value


class SubTaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar subtareas"""
    class Meta:
        model = SubTasks
        fields = ['title', 'is_completed']
    
    def validate_title(self, value):
        if value and len(value.strip()) < 3:
            raise serializers.ValidationError("El título debe tener al menos 3 caracteres")
        return value


class SubTaskListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar subtareas dentro de Task"""
    class Meta:
        model = SubTasks
        fields = ['id', 'title', 'is_completed', 'created_at']
        read_only_fields = ['id', 'created_at']


# ==================== TASK SERIALIZERS ====================

class TaskSerializer(serializers.ModelSerializer):
    """Serializer completo para listar/obtener tareas con subtareas"""
    subtasks = SubTaskListSerializer(many=True, read_only=True)
    user_info = UserSerializer(source='user', read_only=True)
    subtasks_count = serializers.SerializerMethodField()
    completed_subtasks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'user', 'user_info', 'title', 'description', 
            'status', 'category', 'created_at', 'updated_at', 
            'subtasks', 'subtasks_count', 'completed_subtasks_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_subtasks_count(self, obj):
        return obj.subtasks.count()
    
    def get_completed_subtasks_count(self, obj):
        return obj.subtasks.filter(is_completed=True).count()


class TaskListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listar tareas (sin subtareas)"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    subtasks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'user', 'user_username', 'title', 'description',
            'status', 'category', 'created_at', 'updated_at', 'subtasks_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_subtasks_count(self, obj):
        return obj.subtasks.count()


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear tareas"""
    subtasks = SubTaskCreateSerializer(many=True, required=False)
    
    class Meta:
        model = Task
        fields = ['user', 'title', 'description', 'status', 'category', 'subtasks']
    
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("El título debe tener al menos 3 caracteres")
        return value
    
    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("La descripción debe tener al menos 10 caracteres")
        return value
    
    def create(self, validated_data):
        subtasks_data = validated_data.pop('subtasks', [])
        task = Task.objects.create(**validated_data)
        
        # Crear subtareas si se proporcionan
        for subtask_data in subtasks_data:
            SubTasks.objects.create(task=task, **subtask_data)
        
        return task


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar tareas"""
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'category']
    
    def validate_title(self, value):
        if value and len(value.strip()) < 3:
            raise serializers.ValidationError("El título debe tener al menos 3 caracteres")
        return value
    
    def validate_description(self, value):
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError("La descripción debe tener al menos 10 caracteres")
        return value


class TaskDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para obtener una tarea específica"""
    subtasks = SubTaskSerializer(many=True, read_only=True)
    user_info = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'user', 'user_info', 'title', 'description',
            'status', 'category', 'created_at', 'updated_at', 'subtasks'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']



class BulkDeleteSerializer(serializers.Serializer):
    """Serializer para eliminación múltiple"""
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )


class BulkStatusUpdateSerializer(serializers.Serializer):
    """Serializer para actualizar estado de múltiples tareas"""
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    status = serializers.ChoiceField(choices=['pending', 'is_completed'])


# ==================== STATISTICS SERIALIZERS ====================

class TaskStatisticsSerializer(serializers.Serializer):
    """Serializer para estadísticas de tareas"""
    total_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    tasks_by_category = serializers.DictField()
    total_subtasks = serializers.IntegerField()
    completed_subtasks = serializers.IntegerField()