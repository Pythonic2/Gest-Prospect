from django.contrib import admin
from django.utils.html import format_html

from .models import MessageTemplate, Prospect, Segment


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "is_default", "is_active", "updated_at")
    list_editable = ("is_active",)
    list_filter = ("is_active", "is_default")
    search_fields = ("name", "body")


@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    list_display = ("name", "segment", "phone", "website_link", "rating", "status", "whatsapp_link", "updated_at")
    list_filter = ("segment", "status")
    search_fields = ("name", "phone", "address")
    readonly_fields = ("created_at", "updated_at", "contacted_at", "whatsapp_link")

    @admin.display(description="Site")
    def website_link(self, prospect: Prospect):
        if not prospect.website_url:
            return "Sem site"
        return format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>',
            prospect.website_url,
            prospect.website_url,
        )

    @admin.display(description="WhatsApp")
    def whatsapp_link(self, prospect: Prospect):
        template = MessageTemplate.objects.filter(is_active=True, is_default=True).first()
        whatsapp_url = prospect.get_whatsapp_url(template)
        if not whatsapp_url:
            return "Sem telefone"
        return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">Abrir WhatsApp</a>', whatsapp_url)
