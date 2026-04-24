from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import timedelta
from django.utils import timezone

class Language(models.Model):
    LANG_CHOICES = [
        ('uz', 'O\'zbek'),
        ('ru', 'Русский'),
        ('en', 'English'),
    ]
    code = models.CharField(max_length=2, choices=LANG_CHOICES, unique=True)
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    
    is_subscribed = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Telegram User'
        verbose_name_plural = 'Telegram Users'
        ordering = ['-last_active']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_blocked']),
            models.Index(fields=['is_subscribed']),
        ]
    
    def __str__(self):
        return f"{self.first_name} ({self.telegram_id})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()


class Trainer(models.Model):
    name = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255)
    bio = models.TextField()
    image = models.ImageField(upload_to='trainers/')
    phone = models.CharField(max_length=20)
    telegram_username = models.CharField(max_length=255, blank=True)
    instagram = models.CharField(max_length=255, blank=True)
    experience_years = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Trainer'
        verbose_name_plural = 'Trainers'
        ordering = ['name']
    
    def __str__(self):
        return self.name