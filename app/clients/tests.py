import json
import os
from datetime import timedelta

from django.test import TestCase
from django.shortcuts import reverse
from django.http import JsonResponse
from django.utils import timezone

from clients.models import Client
from clients.views import (
    ConnectView, DisconnectView, ConfirmView, TimeCheckView
)


class TestViews(TestCase):

    CONNECT_URL = reverse(ConnectView.name)
    DISCONNECT_URL = reverse(DisconnectView.name)
    CONFIRM_URL = reverse(ConfirmView.name)
    TIMECHECK_URL = reverse(TimeCheckView.name)

    def test_bad_payload(self):
        payload = {
            'chat_id': '',
            'source_ip': '1.1.1.1',
            'destination_ip': '2.2.2.2',
        }
        response: JsonResponse = self.client.post(
            self.CONNECT_URL, content_type='application/json', data=json.dumps(payload),
        )
        self.assertEqual(response.status_code, 400)
        msg = json.loads(response.content.decode('utf-8')).get('msg')
        self.assertEqual(msg, 'chat_id required in request body')

    def test_connect(self):
        payload = {
            'chat_id': '1',
            'source_ip': '1.1.1.1',
            'destination_ip': '2.2.2.2',
        }
        response: JsonResponse = self.client.post(
            self.CONNECT_URL, content_type='application/json', data=json.dumps(payload),
        )
        self.assertEqual(response.status_code, 400)
        client = Client.objects.filter(chat_id=1).first()
        self.assertFalse(client.connected)
        self.assertFalse(client.confirmed)

    def test_exceeded_connections(self):
        max_conn = int(os.environ.get('MAX_UNCONFIRMED_CONNECTIONS'))
        client = Client.objects.create(
            chat_id=2,
            source_ip='2.2.2.2',
            destination_ip='255.255.255.255',
            unconfirmed_connections_count=(max_conn + 1),
            last_connection_time=timezone.now(),
        )
        payload = {
            'chat_id': client.chat_id,
            'source_ip': client.source_ip,
            'destination_ip': client.destination_ip,
        }
        response: JsonResponse = self.client.post(
            self.CONNECT_URL, content_type='application/json', data=json.dumps(payload),
        )
        msg = json.loads(response.content.decode('utf-8')).get('msg')
        self.assertEqual(msg, 'client was not properly banned on router')

    def test_disconnect_not_found(self):
        payload = {'chat_id': '999'}
        response: JsonResponse = self.client.post(
            self.DISCONNECT_URL, content_type='application/json', data=json.dumps(payload),
        )
        self.assertEqual(response.status_code, 404)

    def test_disconnect_success(self):
        client = Client.objects.create(
            chat_id=3,
            source_ip='2.2.2.2',
            destination_ip='255.255.255.255',
            unconfirmed_connections_count=0,
            last_connection_time=timezone.now(),
            connected=True,
        )
        payload = {'chat_id': client.chat_id}
        response: JsonResponse = self.client.post(
            self.DISCONNECT_URL, content_type='application/json', data=json.dumps(payload),
        )
        self.assertEqual(response.status_code, 200)
        msg = json.loads(response.content.decode('utf-8')).get('msg')
        self.assertEqual(msg, 'client disconnected')

    def test_confirm_not_found(self):
        payload = {'chat_id': '999'}
        response: JsonResponse = self.client.post(
            self.CONFIRM_URL, content_type='application/json', data=json.dumps(payload),
        )
        self.assertEqual(response.status_code, 404)

    def test_confirm_not_connected(self):
        client = Client.objects.create(
            chat_id=4,
            source_ip='2.2.2.2',
            destination_ip='255.255.255.255',
            unconfirmed_connections_count=0,
            last_connection_time=timezone.now(),
            connected=False,
        )
        payload = {'chat_id': client.chat_id}
        response: JsonResponse = self.client.post(
            self.CONFIRM_URL, content_type='application/json', data=json.dumps(payload),
        )
        self.assertEqual(response.status_code, 422)

    def test_confirm_connected(self):
        client = Client.objects.create(
            chat_id=5,
            source_ip='2.2.2.2',
            destination_ip='255.255.255.255',
            unconfirmed_connections_count=0,
            last_connection_time=timezone.now(),
            connected=True,
        )
        payload = {'chat_id': client.chat_id}
        response: JsonResponse = self.client.post(
            self.CONFIRM_URL, content_type='application/json', data=json.dumps(payload),
        )
        self.assertEqual(response.status_code, 200)
        msg = json.loads(response.content.decode('utf-8')).get('msg')
        self.assertEqual(msg, 'router not available')

    def test_disconnect_clients(self):
        timeout = int(os.environ.get('UNCONFIRMED_TIMEOUT'))
        time_border = timedelta(minutes=(timeout + 1))
        exceeded_client = Client.objects.create(
            chat_id=6,
            source_ip='2.2.2.2',
            destination_ip='255.255.255.255',
            unconfirmed_connections_count=0,
            last_connection_time=timezone.now() - time_border,
            connected=True,
            confirmed=False,
        )
        normal_client = Client.objects.create(
            chat_id=7,
            source_ip='2.2.2.2',
            destination_ip='255.255.255.255',
            unconfirmed_connections_count=0,
            last_connection_time=timezone.now(),
            connected=True,
            confirmed=False,
        )

        response: JsonResponse = self.client.get(self.TIMECHECK_URL)
        msg = json.loads(response.content.decode('utf-8')).get('msg')
        exceeded_client.refresh_from_db()
        normal_client.refresh_from_db()

        self.assertEqual(msg, '1 clients disconnected')
        self.assertFalse(exceeded_client.connected)
        self.assertTrue(normal_client.connected)
