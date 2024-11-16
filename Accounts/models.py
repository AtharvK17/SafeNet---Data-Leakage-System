from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
import os


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    organization = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=50, blank=True)
    profile_picture = models.ImageField(upload_to='', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    email_notifications = models.BooleanField(default=True)
    browser_notifications = models.BooleanField(default=True)
    app_notifications = models.BooleanField(default=True)

    # New fields for data leakage management
    sensitivity_score = models.FloatField(default=0.0)  # Sensitivity score for the user

    def save(self, *args, **kwargs):
        # Only change the filename if a new profile picture is uploaded
        if self.pk and self.profile_picture:  # Check if the instance already exists
            ext = os.path.splitext(self.profile_picture.name)[1].lower()
            self.profile_picture.name = f'{self.user.username}{ext}'

        # Call the parent save method
        super().save(*args, **kwargs)  # Call the superclass's save method

        # Only print the profile picture URL if it exists
        if self.profile_picture:
            print(f"Profile picture saved at: {self.profile_picture.url}")

        # Block the user if their sensitivity score crosses the threshold
        if self.sensitivity_score >= 80.0 and self.user.is_active:
            self.block_user("Sensitivity score threshold exceeded")

    def generate_otp(self):
        otp = f'{random.randint(100000, 999999)}'
        self.otp_code = otp
        self.otp_expiry = timezone.now() + timedelta(minutes=3)
        self.save()
        return otp

    def block_user(self, reason):
        """Block the user by setting is_active=False and create a BlockedUser entry."""
        self.user.is_active = False
        self.user.save()
        BlockedUser.objects.create(user=self.user, reason=reason)
        
    def unblock_user(self):
        """Unblock the user by setting is_active=True"""
        self.user.is_active = True
        self.user.save()
        BlockedUser.objects.filter(user=self.user).delete()

    def __str__(self):
        return self.user.username


class UserActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='account_activities')
    action = models.CharField(max_length=255)  # Description of the action
    timestamp = models.DateTimeField(auto_now_add=True)  # Time of the action
    details = models.TextField(blank=True)  # Additional details about the action

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"


class BlockedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reason = models.TextField(blank=True)  # Optional reason for blocking
    blocked_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the user was blocked
    is_active = models.BooleanField(default=False)  # Add this field

    def __str__(self):
        return f"{self.user.username} (Blocked)"
