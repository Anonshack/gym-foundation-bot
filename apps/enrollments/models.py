from django.db import models
from django.utils import timezone
from datetime import timedelta
from apps.users.models import TelegramUser
from apps.gym.models import GymProgram, MembershipPlan

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='enrollments')
    program = models.ForeignKey(GymProgram, on_delete=models.CASCADE, related_name='enrollments')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        ordering = ['-created_at']
        unique_together = ['user', 'program']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.program.name}"
    
    def save(self, *args, **kwargs):
        if not self.end_date and self.program.duration_days:
            self.end_date = self.start_date + timedelta(days=self.program.duration_days)
        super().save(*args, **kwargs)