import requests


class TimeChecker:

    @staticmethod
    def run() -> None:
        url = 'http://nginx/clients/timecheck/'
        response = requests.get(url)
        return response
