# Account related forms are defined here
from django import forms
from .models import Profile, BlockedUser


class ForgotPasswordForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, label="Enter your username")


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True, label="Enter the OTP")


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}),
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        label="Confirm Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'address',
            'organization',
            'country',
            'profile_picture',
            'date_of_birth'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control'}),
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d')
        }


class BlockUserForm(forms.ModelForm):
    class Meta:
        model = BlockedUser
        fields = ['reason']  # Assuming you want to specify a reason for blocking
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Reason for blocking this user'}),
        }
