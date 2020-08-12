from django.contrib import admin
from clients.models import Client

from helpers import shell


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):

    actions = ['remove_ban']

    list_display = ('chat_id', 'source_ip', 'destination_ip', 'connected',
                    'confirmed', 'last_connection_time', 'unconfirmed_connections_count')

    def remove_ban(self, request, queryset):
        queryset.update(unconfirmed_connections_count=0)
        for client in queryset:
            res = shell.unban_ip_address(client.source_ip)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
