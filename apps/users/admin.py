from django.contrib import admin
from django.utils.html import format_html
from .models import TelegramUser, Language, Trainer


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'users_count']
    search_fields = ['code', 'name']
    ordering = ['code']

    def users_count(self, obj):
        count = TelegramUser.objects.filter(language=obj).count()
        return format_html(
            '<span style="background:#3498db;color:white;padding:3px 10px;border-radius:10px;font-weight:bold;">{}</span>',
            count
        )
    users_count.short_description = 'Users'


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = [
        'avatar', 'name', 'specialization',
        'experience_badge', 'phone', 'is_active_badge',
    ]
    list_filter = ['is_active', 'experience_years']
    search_fields = ['name', 'specialization', 'phone', 'telegram_username']
    readonly_fields = ['image_preview', 'created_at', 'updated_at']

    fieldsets = (
        ('👤 Personal Info', {
            'fields': ('name', 'specialization', 'bio', 'image', 'image_preview')
        }),
        ('📱 Contact', {
            'fields': ('phone', 'telegram_username', 'instagram')
        }),
        ('🎖️ Experience', {
            'fields': ('experience_years', 'is_active')
        }),
        ('🕐 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def avatar(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;" />',
                obj.image.url
            )
        return format_html('<div style="width:40px;height:40px;border-radius:50%;background:#ccc;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;">{}</div>', obj.name[:1].upper() if obj.name else '?')
    avatar.short_description = ''

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:300px;max-height:300px;border-radius:8px;" />',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Preview'

    def experience_badge(self, obj):
        return format_html(
            '<span style="background:#9b59b6;color:white;padding:3px 10px;border-radius:10px;">{} yrs</span>',
            obj.experience_years
        )
    experience_badge.short_description = 'Exp'

    def is_active_badge(self, obj):
        color = '#27ae60' if obj.is_active else '#95a5a6'
        text = '✅ Active' if obj.is_active else '⛔ Inactive'
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:10px;">{}</span>',
            color, text
        )
    is_active_badge.short_description = 'Status'


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = [
        'telegram_id', 'full_name', 'username_link', 'phone',
        'language_badge', 'subscribed_badge', 'blocked_badge', 'last_active',
    ]
    list_filter = ['is_subscribed', 'is_blocked', 'language', 'created_at']
    search_fields = ['telegram_id', 'username', 'first_name', 'last_name', 'phone']
    readonly_fields = ['telegram_id', 'created_at', 'updated_at', 'last_active']
    actions = ['block_users', 'unblock_users']

    fieldsets = (
        ('👤 Identity', {
            'fields': ('telegram_id', 'username', 'first_name', 'last_name', 'phone')
        }),
        ('🌐 Preferences', {
            'fields': ('language',)
        }),
        ('🔐 Status', {
            'fields': ('is_subscribed', 'is_blocked', 'blocked_reason')
        }),
        ('🕐 Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_active'),
            'classes': ('collapse',)
        }),
    )

    def username_link(self, obj):
        if obj.username:
            return format_html('<a href="https://t.me/{}" target="_blank">@{}</a>', obj.username, obj.username)
        return '—'
    username_link.short_description = 'Username'

    def language_badge(self, obj):
        if not obj.language:
            return '—'
        flags = {'uz': '🇺🇿', 'ru': '🇷🇺', 'en': '🇺🇸'}
        return format_html(
            '<span style="background:#34495e;color:white;padding:3px 10px;border-radius:10px;">{} {}</span>',
            flags.get(obj.language.code, '🌐'),
            obj.language.code.upper()
        )
    language_badge.short_description = 'Lang'

    def subscribed_badge(self, obj):
        if obj.is_subscribed:
            return format_html('<span style="color:#27ae60;font-size:18px;">✅</span>')
        return format_html('<span style="color:#95a5a6;font-size:18px;">○</span>')
    subscribed_badge.short_description = 'Sub'

    def blocked_badge(self, obj):
        if obj.is_blocked:
            return format_html('<span style="background:#e74c3c;color:white;padding:3px 10px;border-radius:10px;">🚫 Blocked</span>')
        return format_html('<span style="color:#27ae60;">OK</span>')
    blocked_badge.short_description = 'Status'

    @admin.action(description='🚫 Block selected users')
    def block_users(self, request, queryset):
        count = queryset.update(is_blocked=True, blocked_reason='Blocked by admin')
        self.message_user(request, f'{count} user(s) blocked.')

    @admin.action(description='✅ Unblock selected users')
    def unblock_users(self, request, queryset):
        count = queryset.update(is_blocked=False, blocked_reason='')
        self.message_user(request, f'{count} user(s) unblocked.')
