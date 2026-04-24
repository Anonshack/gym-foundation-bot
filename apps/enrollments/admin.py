from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        'enrollment_id', 'user_link', 'program_link',
        'status_badge', 'progress_bar', 'created_at',
    ]
    list_filter = ['status', 'program', 'is_active', 'created_at']
    search_fields = ['user__first_name', 'user__telegram_id', 'program__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    actions = ['mark_active', 'mark_completed', 'mark_cancelled']

    fieldsets = (
        ('📋 Enrollment', {'fields': ('user', 'program')}),
        ('✅ Status', {'fields': ('status', 'is_active')}),
        ('📅 Duration', {'fields': ('start_date', 'end_date')}),
        ('📝 Notes', {'fields': ('notes',)}),
        ('🕐 Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def enrollment_id(self, obj):
        return f"#{obj.id}"
    enrollment_id.short_description = 'ID'

    def user_link(self, obj):
        url = reverse('admin:users_telegramuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.full_name)
    user_link.short_description = 'User'

    def program_link(self, obj):
        url = reverse('admin:gym_gymprogram_change', args=[obj.program.id])
        return format_html('<a href="{}">{}</a>', url, obj.program.name)
    program_link.short_description = 'Program'

    def status_badge(self, obj):
        colors = {'pending': '#f39c12', 'active': '#27ae60', 'completed': '#3498db', 'cancelled': '#e74c3c'}
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background:{};color:white;padding:4px 12px;border-radius:12px;font-weight:bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def progress_bar(self, obj):
        if obj.status == 'completed':
            pct = 100
        elif obj.status == 'cancelled':
            return format_html('<span style="color:#e74c3c;">Cancelled</span>')
        elif obj.end_date and obj.start_date:
            total = (obj.end_date - obj.start_date).days or 1
            elapsed = (timezone.now() - obj.start_date).days
            pct = max(0, min(100, int(elapsed / total * 100)))
        else:
            pct = 0
        color = '#27ae60' if pct < 100 else '#3498db'
        return format_html(
            '<div style="width:120px;background:#ecf0f1;border-radius:10px;overflow:hidden;height:20px;">'
            '<div style="width:{}%;background:{};height:100%;text-align:center;color:white;font-size:11px;font-weight:bold;line-height:20px;">{}%</div>'
            '</div>',
            pct, color, pct
        )
    progress_bar.short_description = 'Progress'

    @admin.action(description='✅ Mark as Active')
    def mark_active(self, request, queryset):
        count = queryset.update(status='active')
        self.message_user(request, f'{count} activated.')

    @admin.action(description='🏁 Mark as Completed')
    def mark_completed(self, request, queryset):
        count = queryset.update(status='completed')
        self.message_user(request, f'{count} completed.')

    @admin.action(description='❌ Mark as Cancelled')
    def mark_cancelled(self, request, queryset):
        count = queryset.update(status='cancelled')
        self.message_user(request, f'{count} cancelled.')
