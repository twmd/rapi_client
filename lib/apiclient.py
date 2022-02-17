import json
import requests
import datetime
from .common import get_logger

logger = get_logger()
logger.info('Модуль запустился')

class ApiClientBase:
    '''Базовый класс подключения к API'''
    #TODO: добавить сохранение токена и проверку?
    def __init__(self, server: str, username: str, password: str):
        self.server = server
        self.username = username
        self.password = password
        self.access_token = ''
        logger.info('Класс ApiClientBase инициализирован')
    def api_get(self, uri='', address_ext='', params=''):
        '''
        Метод get
        :param uri:
        :param address_ext:
        :param params:
        :return:
        '''
        headers = {"Content-Type": "application/json", 'Authorization': 'Bearer {}'.format(self.access_token)}
        try:
            resp = requests.get(self.server + uri + address_ext, headers=headers, params=params)
        except Exception as e:
            logger.exception(f'Ошибка метода get к серверу {self.server}')
        else:
            logger.info('api_get отработала')
            return resp.json()

    def api_post(self, uri='', data='', address_ext=''):
        '''
        Метод post
        :param uri:
        :param data:
        :param address_ext:
        :return:
        '''
        headers = {"Content-Type": "application/json", 'Authorization': 'Bearer {}'.format(self.access_token)}
        try:
            resp = requests.post(self.server + uri + address_ext, headers=headers, data=data)
        except Exception as e:
            logger.exception(f'Ошибка метода post к серверу {self.server}')
        else:
            logger.info('api_post отработала')
            return resp.json()

    def auth(self, auth_url):
        # TODO: Если будет потребность доделать что бы работали с access токеном (обновление)
        '''Аутентификация на сервере'''
        auth_data = {
            "login": self.username,
            "password": self.password,
            "authLocateData": str(datetime.datetime.now())
        }
        json_auth_data = json.dumps(auth_data)
        try:
            data = self.api_post(uri=auth_url, data=json_auth_data)
        except Exception as e:
            logger.exception('Функция auth')
        else:
            try:
                self.access_token = data['accessToken']
            except Exception as e:
                logger.exception('Ошибка чтения AccessToken из данных')
            else:
                logger.info('accessToken получен')

if __name__ == '__main__':
    pass
