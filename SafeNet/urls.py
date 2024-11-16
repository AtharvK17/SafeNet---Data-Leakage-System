from django.contrib import admin
from django.urls import path, include
from .views import landing_page
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_page, name='landing'),
    path('Accounts/', include('Accounts.urls')),
    path('Dashboard/', include('Dashboard.urls')),
    path('Tasks/', include(('Tasks.urls', 'tasks'), namespace='tasks')),  # Add namespace here
    path('Projects/', include('Projects.urls')),
    path('DataExplorer/', include(('DataExplorer.urls', 'data_explorer'))),  # Include with namespace
    path('Dataleakage/', include('Dataleakage.urls', namespace='dataleakage')),  # Correct namespace declaration
    path('Notifications/', include('Notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
