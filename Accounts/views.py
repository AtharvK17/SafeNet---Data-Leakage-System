#Accounts views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from .forms import ForgotPasswordForm, OTPVerificationForm, ResetPasswordForm, ProfileUpdateForm, BlockUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Profile, UserActivityLog, BlockedUser
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.sessions.models import Session


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('email-username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember-me')
        
        try:
            # Check if input is email
            if '@' in username:
                user = User.objects.get(email=username)
                username = user.username
            
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if not user.is_active:
                    messages.error(request, "Your account has been blocked. Please contact support.")
                    return redirect('landing')

                login(request, user)
                
                # Handle remember me
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)

                # Log the successful login
                UserActivityLog.objects.create(
                    user=user,
                    action='Logged in',
                    details=f'User {user.username} logged in successfully.'
                )

                return redirect('landing')
            else:
                messages.error(request, "Invalid username or password.")
                return render(request, 'accounts/Login.html')
                
        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': "No account found with this email/username."
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': "An error occurred. Please try again."
            }, status=500)

    return render(request, 'accounts/Login.html')


def logout_view(request):
    if request.method == 'POST':
        user = request.user

        # Log the logout action
        UserActivityLog.objects.create(
            user=user,
            action='Logged out',
            details=f'User {user.username} logged out successfully.'
        )

        logout(request)
        return redirect('landing')  # Redirect to login page after logout
    else:
        return redirect('landing')  # Or wherever you want to redirect for GET


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email is already taken.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            # Create Profile and initialize sensitivity_score and is_blocked
            Profile.objects.create(user=user, sensitivity_score=0.0, is_blocked=False)

            # Log the successful registration
            UserActivityLog.objects.create(
                user=user,
                action='Registered account',
                details=f'User {user.username} registered a new account.'
            )

            messages.success(request, "Account created successfully.")
            return redirect('login')

    return render(request, 'Accounts/Register.html')


def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                otp = user.profile.generate_otp()
                request.session['forgot_password_username'] = username
                messages.success(request, "OTP sent successfully!")

                # Log the action of sending OTP
                UserActivityLog.objects.create(
                    user=user,
                    action='Requested OTP for password reset',
                    details=f'User {user.username} requested OTP for password reset.'
                )

                return redirect('otp_verification')
            except User.DoesNotExist:
                form.add_error('username', 'No user found with this username')
    else:
        form = ForgotPasswordForm()

    return render(request, 'Accounts/Forgot-password.html', {'form': form})


def otp_verification(request):
    username = request.session.get('forgot_password_username', None)

    if not username:
        return redirect('forgot_password')

    user = User.objects.get(username=username)

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            profile = user.profile

            if profile.otp_code == otp and profile.otp_expiry > timezone.now():
                request.session['reset_password_username'] = username
                return redirect('reset_password')
            else:
                form.add_error('otp', 'Invalid or expired OTP')

    form = OTPVerificationForm()
    return render(request, 'Accounts/Otp-verification.html', {'form': form})


def reset_password(request):
    username = request.session.get('forgot_password_username', None)

    if not username:
        messages.error(request, "Session expired or invalid request.")
        return redirect('forgot_password')

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('forgot_password')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()

            # Log the password reset action
            UserActivityLog.objects.create(
                user=user,
                action='Reset password',
                details=f'User {user.username} reset their password.'
            )

            request.session.flush()
            messages.success(request, "Password reset successfully!")
            return redirect('login')

    form = ResetPasswordForm()
    return render(request, 'Accounts/Reset-password.html', {'form': form})


@login_required
def account_settings(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            profile.save()

            # Log the profile update action
            UserActivityLog.objects.create(
                user=request.user,
                action='Updated profile settings',
                details='User updated their account settings.'
            )

            return redirect('accounts:account_settings')  # Changed from 'account-settings' to 'accounts:account_settings'

    form = ProfileUpdateForm(instance=profile)
    return render(request, 'Accounts/Account-settings-account.html', {'form': form, 'profile': profile})


@login_required
def blocked_users_view(request):
    if request.user.is_superuser:
        blocked_users = BlockedUser.objects.all()

        if request.method == 'POST':
            user_id = request.POST.get('user_id')
            try:
                user_to_block = User.objects.get(id=user_id)
                user_to_block.profile.is_blocked = True
                user_to_block.is_active = False  # Set user as inactive
                user_to_block.profile.save()
                user_to_block.save()

                # Log the block action
                UserActivityLog.objects.create(
                    user=request.user,
                    action='Blocked user',
                    details=f'User {request.user.username} blocked {user_to_block.username}.'
                )

                messages.success(request, f"User {user_to_block.username} has been blocked.")
            except User.DoesNotExist:
                messages.error(request, "User does not exist.")

        return render(request, 'dataleakage/DataDashboard.html', {'blocked_users': blocked_users})
    else:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('landing')  # Redirect to the landing page


def dashboard_view(request):
    profile = Profile.objects.get(user=request.user)
    
    # Activity scores from monitoring system
    anomaly_score = 28.57142857142857
    behavior_score = 0.0
    combined_score = 72.86  # This represents the overall sensitivity/risk score
    
    # Calculate risk levels based on the combined score
    risk_levels = {
        'severe': int(combined_score * 0.4),    # 40% weight to severe
        'moderate': int(combined_score * 0.3),  # 30% weight to moderate
        'minor': int(combined_score * 0.3)      # 30% weight to minor
    }

    context = {
        'sensitivity_score': int(combined_score),
        'anomaly_score': round(anomaly_score, 2),
        'behavior_score': round(behavior_score, 2),
        'severe_leaks': risk_levels['severe'],
        'moderate_leaks': risk_levels['moderate'],
        'minor_leaks': risk_levels['minor'],
        # ...other context data...
    }
    return render(request, 'Dashboard/Dashboard.html', context)


@login_required
@require_POST
def toggle_user_block(request, user_id):
    if not request.user.is_staff:
        return JsonResponse({
            'status': 'error',
            'message': 'Permission denied'
        }, status=403)

    target_user = get_object_or_404(User, id=user_id)
    
    # Toggle active status
    if target_user.is_active:
        target_user.is_active = False
        BlockedUser.objects.create(
            user=target_user, 
            reason="Manually blocked by administrator",
            is_active=False
        )
        action = "blocked"
        # Force logout the blocked user
        [s.delete() for s in Session.objects.all() if s.get_decoded().get('_auth_user_id') == str(target_user.id)]
    else:
        target_user.is_active = True
        BlockedUser.objects.filter(user=target_user).delete()
        action = "unblocked"
    
    target_user.save()
    
    return JsonResponse({
        'status': 'success',
        'message': f'User {target_user.username} has been {action}',
        'is_blocked': not target_user.is_active
    })
