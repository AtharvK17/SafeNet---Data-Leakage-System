# Description: URL Configuration for Accounts App
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'accounts'  # Add namespace

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('otp-verification/', views.otp_verification, name='otp_verification'),
    path('reset-password/', views.reset_password, name='reset_password'),

    path('account-settings/', views.account_settings, name='account_settings'),
    path('block-user/', views.blocked_users_view, name='block_user'),
    path('toggle-user-block/<int:user_id>/', views.toggle_user_block, name='toggle_user_block'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
