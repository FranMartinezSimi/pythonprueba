from django.urls import path
from . import views

urlpatterns = [
    # CRUD completo de tareas
    path('tasks/', views.task_list, name='task-list'),           # GET (listar), POST (crear)
    path('tasks/<int:task_id>/', views.task_detail, name='task-detail'),  # GET, PUT, PATCH, DELETE
]

