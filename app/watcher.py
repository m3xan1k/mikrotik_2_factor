from helpers.request_templates import (
    get_updates,
    send_confirm_request,
)


class Watcher:

    # parse telegram response to retrieve chat_id, update_id and callback data
    @staticmethod
    def parse_response(response: dict) -> dict:
        has_callback_data = False
        try:
            message = response['result'][0]['callback_query']['message']
            has_callback_data = True
        except KeyError:
            message = response['result'][0].get('message')
        if not message:
            return None
        chat_id = message['chat']['id']
        update_id = response['result'][0]['update_id']
        if has_callback_data:
            callback_data = message['reply_markup']['inline_keyboard'][0][0]['callback_data']
        else:
            callback_data = None
        return {
            'chat_id': chat_id,
            'update_id': update_id,
            'callback_data': callback_data,
        }

    @staticmethod
    def run() -> None:

        watcher = Watcher()
        last_update_id = 0

        # endless loop to watch chat updates
        while True:
            response = get_updates(last_update_id)
            if not response:
                continue

            # this may happen when token not provided
            if not response.status_code == 200:
                # TODO: logging or notification
                continue

            _json = response.json()

            if _json.get('ok') is True and _json['result']:
                parsed_response: dict = watcher.parse_response(_json)
                last_update_id = _json['result'][0]['update_id']
                if not parsed_response:
                    continue
                chat_id = int(parsed_response['chat_id'])

                # this may happen when user sends text message and not clicking button
                if not parsed_response['callback_data']:
                    # TODO: log?
                    continue

                # otherwise things must be ok and watcher triggers api to confirm client
                send_confirm_request(chat_id)


if __name__ == '__main__':
    Watcher.run()
