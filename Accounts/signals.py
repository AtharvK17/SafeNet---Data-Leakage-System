#Accounts signals.py for the Accounts app
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from Dataleakage.detection import AnomalyDetector, UserBehaviorAnalyzer, AdvancedDataLeakDetector
from .models import Profile, UserActivityLog
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=UserActivityLog)
def handle_user_activity(sender, instance, created, **kwargs):
    if created:  # We only care about new logs
        user = instance.user
        username = getattr(user, 'username', f'User_{user.id}')
        logger.info(f"Processing activity for user {username}: {instance.action}")

        # Initialize the analyzers with the user instance
        anomaly_detector = AnomalyDetector(user=user)
        behavior_analyzer = UserBehaviorAnalyzer(user=user)
        detector = AdvancedDataLeakDetector()

        # Get the anomalies and scores
        anomalies, anomaly_score = anomaly_detector.detect_anomalies()
        behavior_score = behavior_analyzer.analyze_behavior()

        # Calculate combined score using the detector's method
        combined_score = detector._combine_scores(
            sensitivity_score=100,  # Default to safe when no file is involved
            context_score=0,  # No context score for user activity
            anomaly_score=anomaly_score,
            user_behavior_score=behavior_score
        )

        logger.info(f"Activity scores - Anomaly: {anomaly_score}, Behavior: {behavior_score}, Combined: {combined_score}")

        # Log all anomalies detected
        if anomalies:
            logger.warning(f"Anomalies for {username}: {anomalies}")
            
        # Update the profile score with the combined score
        if instance.action in ['Uploaded file', 'Deleted file']:
            try:
                if hasattr(user, 'profile'):
                    profile = user.profile
                    previous_score = getattr(profile, 'sensitivity_score', 0)
                    profile.sensitivity_score = combined_score  # Removed max() to allow score to decrease
                    profile.save(update_fields=['sensitivity_score'])
                    
                    # Force a database refresh
                    profile.refresh_from_db()
                    if profile.sensitivity_score == combined_score:
                        logger.info(f"Successfully updated {username}'s sensitivity score: {previous_score} -> {combined_score}")
                    else:
                        logger.error(f"Failed to update {username}'s sensitivity score in the database. Expected: {combined_score}, Got: {profile.sensitivity_score}")
            except Exception as e:
                logger.error(f"Error updating sensitivity score for {username}: {str(e)}")