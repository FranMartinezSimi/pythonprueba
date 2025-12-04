from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login, name='login'),                   # POST (login con email)

    # CRUD completo de tareas
    path('tasks/', views.task_list, name='task-list'),           # GET (listar), POST (crear)
    path('tasks/<int:task_id>/', views.task_detail, name='task-detail'),  # GET, PUT, PATCH, DELETE

    # CRUD de subtareas
    path('tasks/<int:task_id>/subtasks/', views.subtask_create, name='subtask-create'),  # POST (crear)
    path('subtasks/<int:subtask_id>/', views.subtask_detail, name='subtask-detail'),     # PATCH, DELETE
]

