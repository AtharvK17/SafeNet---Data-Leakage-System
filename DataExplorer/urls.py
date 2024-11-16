# DataExplorer/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'data_explorer'
urlpatterns = [
    path('', views.data_explorer_home, name='data_explorer_home'),  # Home view showing all files
    path('upload/', views.upload_file, name='upload_file'),        # Upload file view
    path('delete_file/<int:file_id>/', views.delete_file, name='delete_file'),
    path('view/<int:file_id>/', views.view_data, name='view_data'),  # View specific file data
    path('update-row/<int:file_id>/<int:row_id>/', views.update_row, name='update_row'),
    path('delete-row/<int:file_id>/', views.delete_row, name='delete_row'),
    path('visualization/<int:file_id>/', views.create_visualization, name='create_visualization'),  # Create visualization for specific file
    path('create-visualization/<int:file_id>/', views.create_visualization, name='create_visualization'),
    path('get-columns/<int:file_id>/', views.get_columns, name='get_columns'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
