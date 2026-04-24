from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from apps.users.models import TelegramUser
from apps.gym.models import GymProgram, MembershipPlan
from apps.enrollments.models import Enrollment
import uuid

class PaymentCard(models.Model):
    BANK_CHOICES = [
        ('aloqa', 'Aloqa Bank'),
        ('sqb', 'SQB Bank'),
        ('visa', 'Visa'),
        ('mastercard', 'Master Card'),
    ]
    
    bank_name = models.CharField(max_length=100, choices=BANK_CHOICES)
    card_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Payment Card'
        verbose_name_plural = 'Payment Cards'
        ordering = ['bank_name']
    
    def __str__(self):
        return f"{self.bank_name} - {self.card_number[-4:]}"


class PaymentMethod(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Karta orqali to\'lash'),
        ('click', 'Click orqali to\'lash'),
        ('payme', 'Payme orqali to\'lash'),
        ('uzum', 'Uzum orqali to\'lash'),
    ]
    
    method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
    
    def __str__(self):
        return self.name


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda 🕐'),
        ('processing', 'Qayta ishlanmoqda 🔄'),
        ('approved', 'Tasdiqlandi ✅'),
        ('rejected', 'Rad etildi ❌'),
        ('cancelled', 'Bekor qilindi 🚫'),
        ('refund', 'Qaytarma 💰'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('program', 'Kursga to\'lash'),
        ('membership', 'Membership to\'lashi'),
        ('coaching', 'Coach bilan sessiya'),
    ]
    
    # Transaction ID (unique)
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    
    # User info - CHANGED related_name
    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='user_payments'  # Changed from 'payments'
    )
    
    # Payment type va amount
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPE_CHOICES)
    amount_uzs = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(1000)]
    )
    amount_usd = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.5)]
    )
    currency = models.CharField(
        max_length=3,
        choices=[('UZS', 'UZS'), ('USD', 'USD')],
        default='UZS'
    )
    
    # Related objects
    program = models.ForeignKey(
        GymProgram,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='program_payments'  # Changed from 'payments'
    )
    membership_plan = models.ForeignKey(
        MembershipPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='membership_payments'  # Changed from 'payments'
    )
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_record'
    )
    
    # Payment method
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    card = models.ForeignKey(
        PaymentCard,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    # Screenshot (manual payment uchun)
    screenshot = models.ImageField(upload_to='payments/%Y/%m/%d/')
    screenshot_verified = models.BooleanField(default=False)
    is_fake_detected = models.BooleanField(default=False)
    fake_reason = models.TextField(blank=True, null=True)
    
    # Approval info - CHANGED related_name
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_approvals'  # Changed from 'approved_payments'
    )
    approval_comment = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Transaction details
    reference_number = models.CharField(max_length=100, blank=True, null=True, unique=True)
    external_transaction_id = models.CharField(max_length=200, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Commission
    commission_uzs = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Payment method commission"
    )
    net_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount after commission"
    )
    
    # Additional info
    notes = models.TextField(blank=True, null=True)
    is_test = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['payment_type', 'status']),
        ]
        permissions = [
            ('can_approve_payment', 'Can approve payments'),
            ('can_reject_payment', 'Can reject payments'),
            ('can_refund_payment', 'Can refund payments'),
        ]
    
    def __str__(self):
        return f"{self.transaction_id} - {self.user.full_name} ({self.amount_uzs} {self.currency})"
    
    def save(self, *args, **kwargs):
        # Calculate net amount
        if self.commission_uzs:
            self.net_amount = self.amount_uzs - self.commission_uzs
        else:
            self.net_amount = self.amount_uzs
        
        super().save(*args, **kwargs)
    
    @property
    def is_completed(self):
        return self.status == 'approved'
    
    @property
    def is_pending(self):
        return self.status == 'pending'
    
    @property
    def is_failed(self):
        return self.status in ['rejected', 'cancelled']
    
    @property
    def days_since_creation(self):
        return (timezone.now() - self.created_at).days


class PaymentHistory(models.Model):
    STATUS_LOG_CHOICES = [
        ('created', 'To\'lov yaratildi'),
        ('screenshot_uploaded', 'Screenshot yuklandi'),
        ('under_review', 'Tekshiruvda'),
        ('approved', 'Tasdiqlandi'),
        ('rejected', 'Rad etildi'),
        ('refund_initiated', 'Qaytarma boshlandi'),
    ]
    
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='history'  # ✅ OK - no clash
    )
    status = models.CharField(max_length=50, choices=STATUS_LOG_CHOICES)
    changed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Payment History'
        verbose_name_plural = 'Payment Histories'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.payment.transaction_id} - {self.get_status_display()}"


class Refund(models.Model):
    REFUND_STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('processing', 'Qayta ishlanmoqda'),
        ('completed', 'Tamamlandi'),
        ('failed', 'Muvaffaqiyatsiz'),
    ]
    
    REFUND_REASON_CHOICES = [
        ('user_request', 'Foydalanuvchi so\'rovi'),
        ('duplicate', 'Nusxa to\'lov'),
        ('fraud', 'Firibgar to\'lov'),
        ('system_error', 'Sistema xatosi'),
        ('no_show', 'Dars o\'tkazdi'),
    ]
    
    refund_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='refund_record'  # Changed to avoid clashes
    )
    
    amount_uzs = models.DecimalField(max_digits=12, decimal_places=2)
    amount_usd = models.DecimalField(max_digits=12, decimal_places=2)
    
    reason = models.CharField(max_length=50, choices=REFUND_REASON_CHOICES)
    description = models.TextField()
    
    status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='pending')
    
    initiated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='refund_initiations'  # ✅ Fixed related_name
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund: {self.payment.transaction_id} - {self.amount_uzs} UZS"


class PaymentSettings(models.Model):
    min_amount_uzs = models.DecimalField(max_digits=12, decimal_places=2, default=1000)
    max_amount_uzs = models.DecimalField(max_digits=12, decimal_places=2, default=100000000)
    
    min_amount_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0.10)
    max_amount_usd = models.DecimalField(max_digits=12, decimal_places=2, default=10000)
    
    usd_to_uzs = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=12000,
        help_text="1 USD = X UZS"
    )
    
    payment_timeout_hours = models.IntegerField(default=24, help_text="Soat ichida to'lash kerak")
    
    send_email_on_payment = models.BooleanField(default=True)
    send_telegram_notification = models.BooleanField(default=True)
    
    fake_detection_enabled = models.BooleanField(default=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Payment Settings'
        verbose_name_plural = 'Payment Settings'
    
    def __str__(self):
        return "Payment Settings"
    
    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
