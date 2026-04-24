from django.db import models
from apps.users.models import Trainer
from django.db import models
from django.db.models import Q, CheckConstraint

class GymProgram(models.Model):
    PROGRAM_CHOICES = [
        ('weight_loss', '⚖️ Weight Loss'),
        ('muscle_gain', '💪 Muscle Gain'),
        ('boxing', '🥊 Boxing'),
        ('crossfit', '🏋️ CrossFit'),
        ('personal_training', '👨‍🏫 Personal Training'),
        ('women_fitness', '👩‍🦰 Women Fitness'),
        ('teen_fitness', '🧒 Teen Fitness'),
    ]
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, choices=PROGRAM_CHOICES, unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='programs/')
    
    # Pricing
    price_uzs = models.DecimalField(max_digits=10, decimal_places=0)
    price_usd = models.DecimalField(max_digits=5, decimal_places=2)
    duration_days = models.IntegerField(default=30)
    
    # Trainer
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='programs'
    )
    
    benefits = models.TextField(
        blank=True,
        null=True,
        help_text="Enter benefits, one per line (press Enter after each benefit)"
    )
    requirements = models.TextField(
        blank=True,
        null=True,
        help_text="Enter requirements, one per line (press Enter after each requirement)"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Gym Program"
        verbose_name_plural = "Gym Programs"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_code_display()})"
    
    def get_benefits_list(self):
        """Convert benefits text to list"""
        if self.benefits:
            return [b.strip() for b in self.benefits.split('\n') if b.strip()]
        return []
    
    def get_requirements_list(self):
        """Convert requirements text to list"""
        if self.requirements:
            return [r.strip() for r in self.requirements.split('\n') if r.strip()]
        return []


class MembershipPlan(models.Model):
    TIER_CHOICES = [
        ('starter', '🥉 Starter'),
        ('standard', '🥈 Standard'),
        ('pro', '🥇 Pro'),
        ('vip', '👑 VIP'),
    ]
    
    tier = models.CharField(max_length=50, choices=TIER_CHOICES, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price_monthly_uzs = models.DecimalField(max_digits=10, decimal_places=2)
    price_monthly_usd = models.DecimalField(max_digits=10, decimal_places=2)
    
    benefits = models.JSONField(default=list)
    duration_days = models.IntegerField(default=30)
    max_enrollments = models.IntegerField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Membership Plan'
        verbose_name_plural = 'Membership Plans'
        ordering = ['tier']
    
    def __str__(self):
        return self.name


class Schedule(models.Model):
    program = models.ForeignKey(GymProgram, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=[(i, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i]) for i in range(7)])
    start_time = models.TimeField()
    end_time = models.TimeField()
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, blank=True)
    capacity = models.IntegerField(default=20)
    
    class Meta:
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'
        unique_together = ['program', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.program.name} - {self.get_day_of_week_display()}"


class NutritionPlan(models.Model):
    program = models.ForeignKey(GymProgram, on_delete=models.CASCADE, related_name='nutrition_plans')
    name = models.CharField(max_length=255)
    description = models.TextField()
    meal_plan = models.JSONField()  # Detailed meal plan
    calories = models.IntegerField()
    protein_g = models.IntegerField()
    carbs_g = models.IntegerField()
    fat_g = models.IntegerField()
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Nutrition Plan'
        verbose_name_plural = 'Nutrition Plans'
    
    def __str__(self):
        return self.name


class Discount(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    discount_percent = models.IntegerField()
    discount_uzs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    applicable_programs = models.ManyToManyField(GymProgram, blank=True)
    applicable_plans = models.ManyToManyField(MembershipPlan, blank=True)
    
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    max_uses = models.IntegerField(null=True, blank=True)
    current_uses = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Discount'
        verbose_name_plural = 'Discounts'
    
    def __str__(self):
        return f"{self.code} - {self.discount_percent}%"
    
    def is_valid(self):
        from django.utils import timezone
        return self.is_active and self.valid_from <= timezone.now() <= self.valid_until


class Testimonial(models.Model):
    user = models.ForeignKey('users.TelegramUser', on_delete=models.CASCADE)
    program = models.ForeignKey(GymProgram, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField(choices=[(i, f"{i} ⭐") for i in range(1, 6)])
    text = models.TextField()
    before_image = models.ImageField(upload_to='testimonials/before/')
    after_image = models.ImageField(upload_to='testimonials/after/')
    
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.rating}⭐"