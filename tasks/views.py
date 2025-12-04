from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import Task, SubTasks
from .serielizers import TaskSerializer, SubTaskSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User


# ==================== AUTH ====================

@api_view(['POST'])
def login(request):
    """
    POST: Login with email only
    Body: {"email": "user@example.com"}
    """
    email = request.data.get('email', None)

    if not email:
        return Response(
            {"error": "Email es requerido"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
        return Response({
            "id": user.id,
            "email": user.email,
            "username": user.username
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(
            {"error": "Usuario no encontrado con ese email"},
            status=status.HTTP_404_NOT_FOUND
        )


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
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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


# ==================== SUBTASK CRUD ====================

@api_view(['POST'])
def subtask_create(request, task_id):
    """
    POST: Create a new subtask for a task
    Body: {"title": "My subtask", "is_completed": false}
    """
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    # Validar que el usuario sea dueño de la tarea
    user_id = request.data.get('user_id', None)
    if user_id and str(task.user_id) != str(user_id):
        return Response(
            {"error": "No tienes permiso para agregar subtareas a esta tarea"},
            status=status.HTTP_403_FORBIDDEN
        )

    title = request.data.get('title', '')
    is_completed = request.data.get('is_completed', False)

    if not title:
        return Response(
            {"error": "El título es requerido"},
            status=status.HTTP_400_BAD_REQUEST
        )

    subtask = SubTasks.objects.create(
        task=task,
        title=title,
        is_completed=is_completed
    )

    serializer = SubTaskSerializer(subtask)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PATCH', 'DELETE'])
def subtask_detail(request, subtask_id):
    """
    PATCH: Update subtask (toggle is_completed or change title)
    DELETE: Delete subtask
    """
    try:
        subtask = SubTasks.objects.get(id=subtask_id)
    except SubTasks.DoesNotExist:
        return Response({"error": "Subtask not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        # Actualizar campos proporcionados
        if 'title' in request.data:
            subtask.title = request.data['title']
        if 'is_completed' in request.data:
            subtask.is_completed = request.data['is_completed']

        subtask.save()
        serializer = SubTaskSerializer(subtask)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        subtask.delete()
        return Response(
            {"message": "Subtarea eliminada exitosamente"},
            status=status.HTTP_200_OK
        )