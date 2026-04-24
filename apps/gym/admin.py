from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import GymProgram, MembershipPlan, Schedule, NutritionPlan, Discount, Testimonial


class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 0
    fields = ['day_of_week', 'start_time', 'end_time', 'trainer', 'capacity']


@admin.register(GymProgram)
class GymProgramAdmin(admin.ModelAdmin):
    list_display = [
        'icon', 'name', 'price_display', 'trainer_link',
        'duration_badge', 'benefits_count', 'is_active_badge',
    ]
    list_filter = ['is_active', 'code', 'trainer']
    search_fields = ['name', 'description']
    readonly_fields = ['image_preview', 'benefits_preview', 'requirements_preview', 'created_at', 'updated_at']
    inlines = [ScheduleInline]

    fieldsets = (
        ('📋 Program Info', {
            'fields': ('name', 'code', 'description', 'image', 'image_preview')
        }),
        ('💰 Pricing & Duration', {
            'fields': ('price_uzs', 'price_usd', 'duration_days')
        }),
        ('👨‍🏫 Trainer', {'fields': ('trainer',)}),
        ('✅ Benefits', {
            'fields': ('benefits', 'benefits_preview'),
            'description': 'Enter each benefit on a new line'
        }),
        ('⚠️ Requirements', {
            'fields': ('requirements', 'requirements_preview'),
            'description': 'Enter each requirement on a new line'
        }),
        ('✅ Status', {'fields': ('is_active',)}),
        ('🕐 Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    ICONS = {
        'weight_loss': '⚖️', 'muscle_gain': '💪', 'boxing': '🥊',
        'crossfit': '🏋️', 'personal_training': '👨‍🏫',
        'women_fitness': '👩‍🦰', 'teen_fitness': '🧒',
    }

    def icon(self, obj):
        return format_html('<span style="font-size:24px;">{}</span>', self.ICONS.get(obj.code, '🏋️'))
    icon.short_description = ''

    def price_display(self, obj):
        return format_html(
            '<span style="background:#27ae60;color:white;padding:4px 10px;border-radius:12px;font-weight:bold;">{} so‘m / ${}</span>',
            f'{int(obj.price_uzs):,}', f'{obj.price_usd:.2f}'
        )
    price_display.short_description = 'Price'

    def trainer_link(self, obj):
        if obj.trainer:
            url = reverse('admin:users_trainer_change', args=[obj.trainer.id])
            return format_html('<a href="{}">{}</a>', url, obj.trainer.name)
        return '—'
    trainer_link.short_description = 'Trainer'

    def duration_badge(self, obj):
        return format_html(
            '<span style="background:#9b59b6;color:white;padding:3px 10px;border-radius:12px;">{} days</span>',
            obj.duration_days
        )
    duration_badge.short_description = 'Duration'

    def benefits_count(self, obj):
        return format_html(
            '<span style="background:#3498db;color:white;padding:3px 10px;border-radius:12px;">{} benefits</span>',
            len(obj.get_benefits_list())
        )
    benefits_count.short_description = 'Benefits'

    def is_active_badge(self, obj):
        color = '#27ae60' if obj.is_active else '#e74c3c'
        text = '✅ Active' if obj.is_active else '❌ Inactive'
        return format_html('<span style="background:{};color:white;padding:4px 10px;border-radius:12px;">{}</span>', color, text)
    is_active_badge.short_description = 'Status'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width:300px;border-radius:8px;" />', obj.image.url)
        return '—'
    image_preview.short_description = 'Preview'

    def benefits_preview(self, obj):
        items = obj.get_benefits_list()
        if not items:
            return format_html('<em style="color:#999;">No benefits added yet</em>')
        html = '<ul style="background:#ecf0f1;padding:15px 30px;border-radius:8px;margin:0;">'
        for b in items:
            html += f'<li style="margin:5px 0;">✅ {b}</li>'
        html += '</ul>'
        return format_html(html)
    benefits_preview.short_description = 'Benefits Preview'

    def requirements_preview(self, obj):
        items = obj.get_requirements_list()
        if not items:
            return format_html('<em style="color:#999;">No requirements added yet</em>')
        html = '<ul style="background:#fef5e7;padding:15px 30px;border-radius:8px;margin:0;">'
        for r in items:
            html += f'<li style="margin:5px 0;">⚠️ {r}</li>'
        html += '</ul>'
        return format_html(html)
    requirements_preview.short_description = 'Requirements Preview'


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ['tier_badge', 'name', 'price_display', 'duration_badge', 'is_active_badge']
    list_filter = ['is_active', 'tier']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('📋 Plan', {'fields': ('tier', 'name', 'description')}),
        ('💰 Pricing', {'fields': ('price_monthly_uzs', 'price_monthly_usd', 'duration_days')}),
        ('✅ Benefits', {'fields': ('benefits', 'max_enrollments'), 'description': 'Benefits should be a JSON list: ["Benefit 1", "Benefit 2"]'}),
        ('Status', {'fields': ('is_active',)}),
        ('🕐 Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    TIER_COLORS = {'starter': '#95a5a6', 'standard': '#3498db', 'pro': '#f39c12', 'vip': '#9b59b6'}

    def tier_badge(self, obj):
        return format_html(
            '<span style="background:{};color:white;padding:4px 12px;border-radius:12px;font-weight:bold;">{}</span>',
            self.TIER_COLORS.get(obj.tier, '#95a5a6'), obj.get_tier_display()
        )
    tier_badge.short_description = 'Tier'

    def price_display(self, obj):
        return format_html(
            '<span style="background:#27ae60;color:white;padding:4px 10px;border-radius:12px;font-weight:bold;">{} so‘m / ${}</span>',
            f'{int(obj.price_monthly_uzs):,}', f'{obj.price_monthly_usd:.2f}'
        )
    price_display.short_description = 'Monthly Price'

    def duration_badge(self, obj):
        return format_html(
            '<span style="background:#9b59b6;color:white;padding:3px 10px;border-radius:12px;">{} days</span>',
            obj.duration_days
        )
    duration_badge.short_description = 'Duration'

    def is_active_badge(self, obj):
        color = '#27ae60' if obj.is_active else '#e74c3c'
        text = '✅' if obj.is_active else '❌'
        return format_html('<span style="background:{};color:white;padding:4px 10px;border-radius:12px;">{}</span>', color, text)
    is_active_badge.short_description = 'Status'


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['program', 'day_display', 'time_display', 'trainer', 'capacity']
    list_filter = ['program', 'day_of_week', 'trainer']
    search_fields = ['program__name']

    DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    def day_display(self, obj):
        return self.DAYS[obj.day_of_week]
    day_display.short_description = 'Day'

    def time_display(self, obj):
        return f"{obj.start_time.strftime('%H:%M')} – {obj.end_time.strftime('%H:%M')}"
    time_display.short_description = 'Time'


@admin.register(NutritionPlan)
class NutritionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'program', 'calories_display', 'macros', 'is_active']
    list_filter = ['is_active', 'program']
    search_fields = ['name', 'program__name']

    fieldsets = (
        ('📋 Plan', {'fields': ('program', 'name', 'description')}),
        ('📊 Nutrition', {'fields': ('calories', 'protein_g', 'carbs_g', 'fat_g')}),
        ('🍽️ Meal Plan (JSON)', {
            'fields': ('meal_plan',),
            'description': 'Example: {"breakfast": "Oats", "lunch": "Chicken salad", "dinner": "Fish"}'
        }),
        ('Status', {'fields': ('is_active',)}),
    )

    def calories_display(self, obj):
        return format_html(
            '<span style="background:#e74c3c;color:white;padding:3px 10px;border-radius:12px;font-weight:bold;">{} cal</span>',
            obj.calories
        )
    calories_display.short_description = 'Calories'

    def macros(self, obj):
        return format_html(
            '<small>P: <b>{}g</b> / C: <b>{}g</b> / F: <b>{}g</b></small>',
            obj.protein_g, obj.carbs_g, obj.fat_g
        )
    macros.short_description = 'Macros'


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['code_badge', 'discount_display', 'validity', 'uses', 'is_active']
    list_filter = ['is_active', 'valid_from', 'valid_until']
    search_fields = ['code', 'description']

    def code_badge(self, obj):
        return format_html(
            '<span style="background:#1abc9c;color:white;padding:4px 12px;border-radius:12px;font-weight:bold;font-family:monospace;">{}</span>',
            obj.code
        )
    code_badge.short_description = 'Code'

    def discount_display(self, obj):
        if obj.discount_percent:
            return format_html('<b style="color:#e74c3c;">{}% OFF</b>', obj.discount_percent)
        if obj.discount_uzs:
            return format_html('<b style="color:#e74c3c;">{} UZS</b>', f'{int(obj.discount_uzs):,}')
        return '—'
    discount_display.short_description = 'Discount'

    def validity(self, obj):
        if obj.is_valid():
            return format_html('<span style="color:#27ae60;">✅ Valid</span>')
        return format_html('<span style="color:#e74c3c;">❌ Expired</span>')
    validity.short_description = 'Validity'

    def uses(self, obj):
        if obj.max_uses:
            return f"{obj.current_uses} / {obj.max_uses}"
        return f"{obj.current_uses} / ∞"
    uses.short_description = 'Uses'


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'program', 'rating_display', 'is_approved_badge', 'created_at']
    list_filter = ['is_approved', 'rating', 'program']
    search_fields = ['user__first_name', 'text']
    readonly_fields = ['before_preview', 'after_preview', 'created_at']
    actions = ['approve', 'reject']

    fieldsets = (
        ('👤 User', {'fields': ('user', 'program')}),
        ('⭐ Review', {'fields': ('rating', 'text')}),
        ('📸 Images', {'fields': ('before_image', 'before_preview', 'after_image', 'after_preview')}),
        ('✅ Approval', {'fields': ('is_approved',)}),
    )

    def user_name(self, obj):
        return obj.user.full_name
    user_name.short_description = 'User'

    def rating_display(self, obj):
        return '⭐' * obj.rating
    rating_display.short_description = 'Rating'

    def is_approved_badge(self, obj):
        if obj.is_approved:
            return format_html('<span style="background:#27ae60;color:white;padding:3px 10px;border-radius:12px;">✅ Approved</span>')
        return format_html('<span style="background:#f39c12;color:white;padding:3px 10px;border-radius:12px;">⏳ Pending</span>')
    is_approved_badge.short_description = 'Status'

    def before_preview(self, obj):
        if obj.before_image:
            return format_html('<img src="{}" style="max-width:200px;border-radius:8px;" />', obj.before_image.url)
        return '—'
    before_preview.short_description = 'Before'

    def after_preview(self, obj):
        if obj.after_image:
            return format_html('<img src="{}" style="max-width:200px;border-radius:8px;" />', obj.after_image.url)
        return '—'
    after_preview.short_description = 'After'

    @admin.action(description='✅ Approve selected')
    def approve(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f'{count} testimonial(s) approved.')

    @admin.action(description='❌ Reject selected')
    def reject(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f'{count} testimonial(s) rejected.')
