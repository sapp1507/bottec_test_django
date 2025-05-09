from django.contrib import admin

from mailing.models import MailingCampaign, MailingLog


class MailingLogInline(admin.TabularInline):
    model = MailingLog
    extra = 0
    readonly_fields = ('campaign', 'user', 'is_sent', 'error_message')
    can_delete = False


@admin.register(MailingCampaign)
class MailingCampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'campaign_type', 'is_active', 'schedule_time')
    list_filter = ('campaign_type', 'is_active')
    search_fields = ('name', 'message_text')
    filter_horizontal = ('target_groups',)
    inlines = (MailingLogInline,)
    fieldsets = (
        (None, {
            'fields': ('name', 'campaign_type', 'is_active', 'schedule_time')
        }),
        ('Контент', {
            'fields': ('message_text', 'photo', 'poll_question', 'poll_options')
        }),
        ('Аудитория', {
            'fields': ('target_groups',),
        }),
    )


@admin.register(MailingLog)
class MailingLogAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'user', 'is_sent', 'error_message')
    list_filter = ('is_sent', 'campaign')
    search_fields = ('user__username', 'user__full_name')
    readonly_fields = ('created_at',)

