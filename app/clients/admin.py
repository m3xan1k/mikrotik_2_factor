from django.contrib import admin
from clients.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'source_ip', 'destination_ip', 'connected',
                    'confirmed', 'last_connection_time', 'unconfirmed_connections_count')
