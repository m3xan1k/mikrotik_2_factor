from datetime import timedelta
import os

import requests

from django.utils import timezone
from clients.models import Client
from django.db.models import QuerySet


MAX_UNCONFIRMED_CONNECTIONS = int(os.environ.get('MAX_UNCONFIRMED_CONNECTIONS'))
UNCONFIRMED_TIMEOUT = int(os.environ.get('UNCONFIRMED_TIMEOUT'))


def has_exceeded_connections(payload: dict) -> bool:
    chat_id = int(payload['chat_id'])
    if client := Client.objects.filter(chat_id=chat_id).first():
        if client.unconfirmed_connections_count > MAX_UNCONFIRMED_CONNECTIONS:
            return True
    return False


def save_connected_client(payload: dict) -> Client:
    chat_id = int(payload['chat_id'])
    client: Client or None = Client.objects.filter(chat_id=chat_id).first()
    if not client:
        client = Client()
    client.chat_id = chat_id
    client.source_ip = payload['source_ip']
    client.destination_ip = payload['destination_ip']
    client.connected = True
    client.last_connection_time = timezone.now()
    client.unconfirmed_connections_count += 1
    client.save()
    return client


def save_confirmed_client(chat_id: int) -> tuple:
    client: Client = Client.objects.filter(chat_id=chat_id).first()
    if not client:
        return (None, 404)
    if not client.connected:
        return (client, 422)
    client.confirmed = True
    client.unconfirmed_connections_count = 0
    client.save()
    return (client, 200)


def save_disconnected_client(chat_id: int, banned=False) -> Client or None:
    client: Client = Client.objects.filter(chat_id=chat_id).first()
    if not client:
        return None
    client.confirmed = False
    client.connected = False
    if banned:
        client.unconfirmed_connections_count = 0
    client.save()
    return client


def get_time_exceeded_clients() -> QuerySet:
    timeout = UNCONFIRMED_TIMEOUT
    time_border = timezone.now() - timedelta(minutes=timeout)
    exceeded_clients: QuerySet = (
        Client.objects
              .filter(last_connection_time__lt=time_border,
                      connected=True,
                      confirmed=False)
              .all()
    )
    return exceeded_clients


def save_message_id(chat_id: int, response: requests.Response) -> Client or None:
    answer = response.json()
    if answer['ok'] and answer.get('result'):
        message_id = answer['result']['message_id']

        client: Client = Client.objects.filter(chat_id=chat_id).first()
        client.last_confirm_message_id = message_id
        client.save()
        return client
    return None


def bulk_update_clients(clients: QuerySet, fields: list) -> None:
    Client.objects.bulk_update(clients, fields)
