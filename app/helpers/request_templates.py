import json
import os

import requests


BASE_URL = f'https://api.telegram.org/bot{os.environ.get("TOKEN")}'

if proxy_conn_string := os.environ.get('PROXY'):
    PROXIES = {
        'http': proxy_conn_string,
        'https': proxy_conn_string,
    }
else:
    PROXIES = None


class Message:
    @staticmethod
    def authorized(source_ip: str) -> str:
        return f'Your ip address {source_ip} authorized'

    @staticmethod
    def unavailable(source_ip: str) -> str:
        return f'Your ip address {source_ip} not authorized. \
            Either you are disconnected or router is unavailable. Try again later.'

    @staticmethod
    def unautorized() -> str:
        return 'You are not authorized.'

    @staticmethod
    def confirm_connection() -> str:
        return 'Are you trying connect to network?'

    @staticmethod
    def banned() -> str:
        return 'You are banned. Connections without confirmation exceeded.'

    @staticmethod
    def confirmation_time_exceeded() -> str:
        return 'Connection time without confirmation exceeded'


def get_updates(last_update_id: int) -> requests.Response:
    limit = 1
    offset = last_update_id + 1
    timeout = 100
    params = {'limit': limit, 'offset': offset, 'timeout': timeout}
    url = f'{BASE_URL}/getupdates'
    response = requests.get(url=url, params=params, proxies=PROXIES)
    return response


def send_message(chat_id: int, message_text: str) -> requests.Response:
    params = {'text': message_text, 'chat_id': chat_id}
    url = f'{BASE_URL}/sendmessage'
    response = requests.get(url=url, params=params, proxies=PROXIES)
    return response


def send_confirm_button(chat_id: int, payload: dict) -> requests.Response:
    message_text = Message.confirm_connection()
    button_text = 'Confirm'
    del payload['chat_id']
    reply_markup = {'inline_keyboard': [[{'text': button_text, 'callback_data': str(payload)}]]}
    headers = {'content-type': 'application/json'}
    data = {'text': message_text, 'chat_id': chat_id, 'reply_markup': reply_markup}
    url = f'{BASE_URL}/sendmessage'
    response = requests.post(url=url, data=json.dumps(data), headers=headers, proxies=PROXIES)
    return response


def send_confirm_request(chat_id: int) -> requests.Response:
    headers = {'content-type': 'application/json'}
    data = {'chat_id': chat_id}
    url = 'http://nginx/clients/confirm/'
    response = requests.post(url=url, headers=headers, data=json.dumps(data))
    return response


def delete_confirm_button(chat_id: int, message_id: int) -> requests.Response:
    params = {'chat_id': chat_id, 'message_id': message_id}
    url = f'{BASE_URL}/deletemessage'
    response = requests.get(url=url, params=params, proxies=PROXIES)
    return response
