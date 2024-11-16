# urls.py in the Task app
from django.urls import path
from .views import create_task, task_list, edit_task, delete_task

app_name = 'tasks'

urlpatterns = [
    path('tasks/', task_list, name='task_list'),
    path('tasks/create/', create_task, name='create_task'),
    path('tasks/edit/<int:task_id>/', edit_task, name='edit_task'),
    path('tasks/delete/<int:task_id>/', delete_task, name='delete_task'),  # Updated path
]
