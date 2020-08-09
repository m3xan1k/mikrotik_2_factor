import json

from django.views import View
from django.http import HttpRequest, JsonResponse

from helpers import crud
from helpers.request_templates import (
    send_confirm_button, send_message, Message,
    delete_confirm_button,
)

from helpers import shell


class ConnectView(View):

    name = 'connect'

    def post(self, request: HttpRequest) -> JsonResponse:

        # serialize request body to python dict
        body_unicode = request.body.decode('utf-8')
        payload = json.loads(body_unicode)

        chat_id = int(payload['chat_id'])

        # check if client has too much unconfirmed connections to ban or not
        if crud.has_exceeded_connections(payload):
            ban: bool = shell.ban_ip_address(payload)
            reset: bool = shell.disconnect_client(payload)

            # if client was not properly banned on router
            if not ban or not reset:
                pass
                return JsonResponse({'msg': 'client was not properly banned on router'})

            crud.save_disconnected_client(chat_id)
            res = send_message(chat_id, Message.banned())
            print(res.json(), res.url)
            return JsonResponse({'msg': 'client banned'})

        # if ok save client and send confirmation button to tg
        crud.save_connected_client(payload)
        response = send_confirm_button(chat_id, payload)
        crud.save_message_id(chat_id, response)
        return JsonResponse({'msg': 'client connected'})


class DisconnectView(View):

    name = 'disconnect'

    def post(self, request: HttpRequest) -> JsonResponse:

        # serialize request body to python dict
        body_unicode = request.body.decode('utf-8')
        payload = json.loads(body_unicode)

        # try to find and save client
        client = crud.save_disconnected_client(int(payload['chat_id']))
        if not client:
            return JsonResponse(content={'msg': 'client not found'}, status=404)
        delete_confirm_button(client.chat_id, client.last_confirm_message_id)
        return JsonResponse({'msg': 'client disconnected'})


class ConfirmView(View):

    name = 'confirm'

    def post(self, request: HttpRequest) -> JsonResponse:

        # serialize request body to python dict
        body_unicode = request.body.decode('utf-8')
        payload = json.loads(body_unicode)

        chat_id = int(payload['chat_id'])

        # try to save client and check different cases of client state
        client, status = crud.save_confirmed_client(chat_id)

        # clean button after all
        delete_confirm_button(chat_id, client.last_confirm_message_id)

        # if client not found or client not connected
        if status == 404:
            return JsonResponse({'msg': 'client not found'}, status=status)

        if status == 422:
            return JsonResponse({'msg': 'client not connected'}, status=status)

        # successfully saved client authorizes on router
        ip_addresses = {'source_ip': client.source_ip, 'destination_ip': client.destination_ip}
        router_response = shell.authorize_ip_address(ip_addresses)

        # for some reason router may not respond, so client will become unconfirmed and disconnected
        if not router_response:
            crud.save_disconnected_client(chat_id)
            send_message(chat_id, Message.unavailable(ip_addresses))
            return JsonResponse({'msg': 'router not available'}, status=status)

        # send success message if all good
        send_message(chat_id, Message.authorized(ip_addresses))

        return JsonResponse({'msg': 'client confirmed'})


class TimeCheckView(View):

    name = 'timecheck'

    def get(self, request: HttpRequest) -> JsonResponse:

        # check if there are exceeded(unconfirmed timeout) clients
        if exceeded_clients := crud.get_time_exceeded_clients():
            for client in exceeded_clients:
                ip_addresses = {
                    'source_ip': client.source_ip,
                    'destination_ip': client.destination_ip,
                }

                # disconnect them on router, change db state and delete button
                shell.disconnect_client(ip_addresses)
                client.connected = False
                delete_confirm_button(client.chat_id, client.last_confirm_message_id)

            # sql bulk update, much faster then change every instance in a loop
            crud.bulk_update_clients(exceeded_clients, ['unconfirmed_connections_count', 'connected'])
            return JsonResponse({'msg': f'{len(exceeded_clients)} clients disconnected'})
        return JsonResponse({'msg': 'No disconnected clients'})
