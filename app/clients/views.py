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

        if not payload['chat_id']:
            return JsonResponse({'msg': 'chat_id required in request body'}, status=400)
        chat_id = int(payload['chat_id'])

        # check if client has too much unconfirmed connections to ban or not
        if crud.has_exceeded_connections(payload):
            ban: bool = shell.ban_ip_address(payload['source_ip'], payload['caller_id'])

            # if client was not properly banned on router
            if not ban:
                return JsonResponse({'msg': 'client was not properly banned on router'})

            crud.save_disconnected_client(chat_id, banned=True)
            send_message(chat_id, Message.banned())
            return JsonResponse({'msg': 'client banned'})

        # if ok save client and send confirmation button to tg
        crud.save_connected_client(payload)
        response = send_confirm_button(chat_id, payload)

        # wrong chat id may cause unsuccessfull response
        if not response.status_code == 200:
            crud.save_disconnected_client(chat_id)
            return JsonResponse({'msg': 'client disconnected. maybe bad chat_id'}, status=400)

        # if ok save btn message id finally
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
            return JsonResponse({'msg': 'client not found'}, status=404)
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

        # if client not found
        if status == 404:
            return JsonResponse({'msg': 'client not found'}, status=status)

        # clean button after all
        delete_confirm_button(chat_id, client.last_confirm_message_id)

        # if client not connected
        if status == 422:
            return JsonResponse({'msg': 'client not connected'}, status=status)

        # successfully saved client authorizes on router
        router_response = shell.authorize_ip_address(client.source_ip)

        # for some reason router may not respond, so client will become unconfirmed and disconnected
        if not router_response:
            crud.save_disconnected_client(chat_id)
            send_message(chat_id, Message.unavailable(client.source_ip))
            return JsonResponse({'msg': 'router not available'}, status=status)

        # send success message if all good
        send_message(chat_id, Message.authorized(client.source_ip))

        return JsonResponse({'msg': 'client confirmed'})


class TimeCheckView(View):

    name = 'timecheck'

    def get(self, request: HttpRequest) -> JsonResponse:

        # check if there are exceeded(unconfirmed timeout) clients
        if exceeded_clients := crud.get_time_exceeded_clients():
            ips_to_disconnect = []
            for client in exceeded_clients:

                client.connected = False
                delete_confirm_button(client.chat_id, client.last_confirm_message_id)
                ips_to_disconnect.append(client.caller_id)

            # disconnect them on router, change db state and delete button
            shell.disconnect_client(ips_to_disconnect)
            # sql bulk update, much faster then change every instance in a loop
            crud.bulk_update_clients(exceeded_clients, ['connected'])
            return JsonResponse({'msg': f'{len(exceeded_clients)} clients disconnected'})
        return JsonResponse({'msg': 'No disconnected clients'})
