from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from .models import Payment, PaymentCard, PaymentMethod, PaymentHistory, Refund, PaymentSettings
from bot.utils.notifier import notify_user_payment_approved, notify_user_payment_rejected
import logging

logger = logging.getLogger(__name__)


@admin.register(PaymentCard)
class PaymentCardAdmin(admin.ModelAdmin):
    list_display = ['bank_name', 'card_display', 'full_name', 'phone_number', 'status_badge']
    list_filter = ['bank_name', 'is_active']
    search_fields = ['card_number', 'full_name', 'phone_number']

    def card_display(self, obj):
        return format_html('<code>**** **** **** {}</code>', obj.card_number[-4:])
    card_display.short_description = 'Card'

    def status_badge(self, obj):
        color = '#27ae60' if obj.is_active else '#95a5a6'
        text = '✅ Active' if obj.is_active else '⛔ Inactive'
        return format_html('<span style="background:{};color:white;padding:3px 10px;border-radius:12px;">{}</span>', color, text)
    status_badge.short_description = 'Status'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'method', 'commission_percent', 'is_active']
    list_filter = ['is_active']


class PaymentHistoryInline(admin.TabularInline):
    model = PaymentHistory
    extra = 0
    readonly_fields = ['status', 'changed_by', 'comment', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'short_id', 'user_link', 'amount_display', 'payment_type_badge',
        'status_badge', 'screenshot_thumb', 'created_at', 'action_buttons',
    ]
    list_filter = ['status', 'payment_type', 'is_fake_detected', 'created_at']
    search_fields = ['user__first_name', 'user__telegram_id', 'transaction_id', 'reference_number']
    readonly_fields = [
        'transaction_id', 'created_at', 'updated_at', 'approved_at', 'rejected_at',
        'screenshot_preview', 'net_amount',
    ]
    inlines = [PaymentHistoryInline]
    actions = ['approve_payments', 'reject_payments']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('🆔 Transaction', {'fields': ('transaction_id', 'reference_number', 'external_transaction_id')}),
        ('👤 User', {'fields': ('user',)}),
        ('💰 Amount', {'fields': ('payment_type', 'amount_uzs', 'amount_usd', 'currency', 'commission_uzs', 'net_amount')}),
        ('📦 Related', {'fields': ('program', 'membership_plan', 'enrollment', 'payment_method', 'card')}),
        ('📸 Screenshot', {'fields': ('screenshot', 'screenshot_preview', 'screenshot_verified', 'is_fake_detected', 'fake_reason')}),
        ('✅ Status', {'fields': ('status', 'approved_by', 'approval_comment', 'rejection_reason', 'approved_at', 'rejected_at')}),
        ('📝 Notes', {'fields': ('notes', 'is_test'), 'classes': ('collapse',)}),
        ('🕐 Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('<int:payment_id>/approve/', self.admin_site.admin_view(self.approve_view), name='payments_payment_approve'),
            path('<int:payment_id>/reject/', self.admin_site.admin_view(self.reject_view), name='payments_payment_reject'),
        ]
        return custom + urls

    def short_id(self, obj):
        return str(obj.transaction_id)[:8]
    short_id.short_description = 'Txn ID'

    def user_link(self, obj):
        url = reverse('admin:users_telegramuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a><br/><small>ID: {}</small>', url, obj.user.full_name, obj.user.telegram_id)
    user_link.short_description = 'User'

    def amount_display(self, obj):
        return format_html(
            '<b>{} so‘m</b><br/><small>${}</small>',
            f'{int(obj.amount_uzs):,}', f'{obj.amount_usd:.2f}'
        )
    amount_display.short_description = 'Amount'

    def status_badge(self, obj):
        colors = {
            'pending': '#f39c12', 'processing': '#3498db', 'approved': '#27ae60',
            'rejected': '#e74c3c', 'cancelled': '#95a5a6', 'refund': '#9b59b6',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background:{};color:white;padding:4px 12px;border-radius:12px;font-weight:bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def payment_type_badge(self, obj):
        colors = {'program': '#3498db', 'membership': '#e74c3c', 'coaching': '#f39c12'}
        color = colors.get(obj.payment_type, '#95a5a6')
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:12px;">{}</span>',
            color, obj.get_payment_type_display()
        )
    payment_type_badge.short_description = 'Type'

    def screenshot_thumb(self, obj):
        if obj.screenshot:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-width:60px;max-height:60px;border-radius:4px;" /></a>',
                obj.screenshot.url, obj.screenshot.url
            )
        return '—'
    screenshot_thumb.short_description = 'Screenshot'

    def screenshot_preview(self, obj):
        if obj.screenshot:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-width:500px;border:2px solid #ddd;border-radius:8px;" /></a>',
                obj.screenshot.url, obj.screenshot.url
            )
        return '—'
    screenshot_preview.short_description = 'Screenshot Preview'

    def action_buttons(self, obj):
        if obj.status != 'pending':
            return '—'
        approve_url = reverse('admin:payments_payment_approve', args=[obj.id])
        reject_url = reverse('admin:payments_payment_reject', args=[obj.id])
        return format_html(
            '<a class="button" style="background:#27ae60;color:white;padding:5px 12px;border-radius:4px;text-decoration:none;margin-right:5px;" href="{}">✅ Approve</a>'
            '<a class="button" style="background:#e74c3c;color:white;padding:5px 12px;border-radius:4px;text-decoration:none;" href="{}">❌ Reject</a>',
            approve_url, reject_url
        )
    action_buttons.short_description = 'Actions'

    def approve_view(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id)
        if payment.status != 'pending':
            messages.warning(request, f'Payment #{payment_id} is not pending (status: {payment.status}).')
        else:
            payment.status = 'approved'
            payment.approved_by = request.user
            payment.approved_at = timezone.now()
            payment.save()
            if payment.enrollment:
                payment.enrollment.status = 'active'
                payment.enrollment.save()
            PaymentHistory.objects.create(
                payment=payment, status='approved', changed_by=request.user,
                comment='Approved via admin action',
            )
            # Notify user via Telegram
            try:
                notify_user_payment_approved(payment)
                messages.success(request, f'✅ Payment #{payment_id} approved & user notified.')
            except Exception as e:
                logger.exception('Telegram notify failed')
                messages.warning(request, f'Payment approved, but Telegram notification failed: {e}')
        return redirect(reverse('admin:payments_payment_changelist'))

    def reject_view(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id)
        if payment.status != 'pending':
            messages.warning(request, f'Payment #{payment_id} is not pending.')
        else:
            payment.status = 'rejected'
            payment.rejected_at = timezone.now()
            payment.rejection_reason = 'Rejected by admin'
            payment.save()
            if payment.enrollment:
                payment.enrollment.status = 'cancelled'
                payment.enrollment.save()
            PaymentHistory.objects.create(
                payment=payment, status='rejected', changed_by=request.user,
                comment='Rejected via admin action',
            )
            try:
                notify_user_payment_rejected(payment)
                messages.success(request, f'❌ Payment #{payment_id} rejected & user notified.')
            except Exception as e:
                logger.exception('Telegram notify failed')
                messages.warning(request, f'Payment rejected, but Telegram notification failed: {e}')
        return redirect(reverse('admin:payments_payment_changelist'))

    @admin.action(description='✅ Approve selected payments')
    def approve_payments(self, request, queryset):
        approved = 0
        for p in queryset.filter(status='pending'):
            p.status = 'approved'
            p.approved_by = request.user
            p.approved_at = timezone.now()
            p.save()
            if p.enrollment:
                p.enrollment.status = 'active'
                p.enrollment.save()
            try:
                notify_user_payment_approved(p)
            except Exception:
                logger.exception('Notify fail')
            approved += 1
        self.message_user(request, f'{approved} payment(s) approved.')

    @admin.action(description='❌ Reject selected payments')
    def reject_payments(self, request, queryset):
        rejected = 0
        for p in queryset.filter(status='pending'):
            p.status = 'rejected'
            p.rejected_at = timezone.now()
            p.save()
            if p.enrollment:
                p.enrollment.status = 'cancelled'
                p.enrollment.save()
            try:
                notify_user_payment_rejected(p)
            except Exception:
                logger.exception('Notify fail')
            rejected += 1
        self.message_user(request, f'{rejected} payment(s) rejected.')


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['refund_id_short', 'payment', 'amount_uzs', 'status', 'reason', 'created_at']
    list_filter = ['status', 'reason']

    def refund_id_short(self, obj):
        return str(obj.refund_id)[:8]
    refund_id_short.short_description = 'Refund ID'


@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not PaymentSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        ('💰 UZS Limits', {'fields': ('min_amount_uzs', 'max_amount_uzs')}),
        ('💵 USD Limits', {'fields': ('min_amount_usd', 'max_amount_usd')}),
        ('📊 Conversion', {'fields': ('usd_to_uzs',)}),
        ('⏱️ Timeout', {'fields': ('payment_timeout_hours',)}),
        ('🔔 Notifications', {'fields': ('send_email_on_payment', 'send_telegram_notification')}),
        ('🔍 Security', {'fields': ('fake_detection_enabled',)}),
    )
