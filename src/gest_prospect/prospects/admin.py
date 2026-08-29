from django.contrib import admin
from django.utils.html import format_html

from .models import Prospect


@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "rating", "status", "whatsapp_link", "updated_at")
    list_filter = ("status",)
    search_fields = ("name", "phone", "address")
    readonly_fields = ("created_at", "updated_at", "contacted_at", "whatsapp_link")

    @admin.display(description="WhatsApp")
    def whatsapp_link(self, prospect: Prospect):
        if not prospect.whatsapp_url:
            return "Sem telefone"
        return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">Abrir WhatsApp</a>', prospect.whatsapp_url)
