from django.db import models


class Client(models.Model):
    name = models.TextField(blank=True, null=False)
    chat_id = models.BigIntegerField(db_index=True)
    source_ip = models.TextField(blank=True, null=False)
    caller_id = models.TextField(blank=True, null=False)
    destination_ip = models.TextField(blank=True, null=False)
    connected = models.BooleanField(default=False)
    confirmed = models.BooleanField(default=False)
    unconfirmed_connections_count = models.IntegerField(default=0)
    last_connection_time = models.DateTimeField()
    last_confirm_message_id = models.IntegerField(null=True)

    def __str__(self):
        return self.chat_id.__str__()
