from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import Task, SubTasks
from .serielizers import TaskSerializer, SubTaskSerializer
from rest_framework.response import Response
from rest_framework import status


# ==================== TASK CRUD ====================

@api_view(['GET', 'POST'])
def task_list(request):
    """
    GET: List all tasks filtered by user_id
    POST: Create a new task
    Query params: ?user_id=1
    """
    if request.method == 'GET':
        # Obtener user_id del query parameter
        user_id = request.query_params.get('user_id', None)
        
        # Listar tareas
        if user_id:
            tasks = Task.objects.filter(user_id=user_id)
        else:
            tasks = Task.objects.all()
        
        # Si no hay tareas, devolver mensaje informativo
        if not tasks.exists():
            return Response({
                "message": "No hay tareas disponibles",
                "tasks": []
            }, status=status.HTTP_200_OK)
        
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Use TaskSerializer for creating (it handles the data properly)
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save()
            # Return the task with subtasks (signal will have generated them)
            response_serializer = TaskSerializer(task)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def task_detail(request, task_id):
    """
    GET: Retrieve a specific task
    PUT: Update a task completely
    PATCH: Update a task partially
    DELETE: Delete a task
    Query params: ?user_id=1 (opcional para verificar permisos)
    """
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Verificar permisos si se proporciona user_id
    user_id = request.query_params.get('user_id', None)
    if user_id and str(task.user_id) != user_id:
        return Response(
            {"error": "No tienes permiso para acceder a esta tarea"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        task.delete()
        return Response(
            {"message": "Tarea eliminada exitosamente"}, 
            status=status.HTTP_200_OK
        )