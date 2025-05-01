from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        get_user_model(), 
        on_delete=models.CASCADE,
        related_name='password_reset_tokens'
    )
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Reset token for {self.user.username}"
    
    def is_valid(self):
        # Token es válido si no ha sido usado y tiene menos de 24 horas
        expiration_time = timezone.now() - timezone.timedelta(hours=24)
        return not self.used and self.created_at > expiration_time