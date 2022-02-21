#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import os
import ast
import datetime
from lib.apiclient import ApiClientBase
from lib.common import get_config, send_email, get_logger
import sys

# Наследуемся от базового класса, получаем доступ к его методам и делам что хотим
class RoomyScript(ApiClientBase):
    # Создаем словари/словарь как удобнее с нужными uri для работы
    script_uri = {
        'get_scripts': r'/api/Script/GetScripts'
    }

    run_info_uri = {
        'get_script_history': r'/api/RunInfo/GetScriptsRunHistoryByScript',

    }

    def __init__(self, server, username, password, scripts_name):
        super(RoomyScript, self).__init__(server=server, username=username, password=password)
        self.scripts_name = scripts_name

    def _get_scripts_id(self):
        '''
        Получаем список имен скриптов, возвращаем словарь с именем и ID
        :return:
        '''
        script_id = {}
        data = self.api_get(self.script_uri['get_scripts'])
        for item in data:
            if item['name'] in self.scripts_name:
                script_id.update({item['name']: item['id']})
        logger.info('UID скриптов получен')
        return script_id

    @staticmethod
    def keys(data: dict, name: str, keys: list):
        '''
        Выбираем ключи которые нам необходимо вернуть
        :param data: Словарь для парсинга
        :param name: Имя робота
        :param keys: Ключи которые необходимо вернуть
        :return:
        '''
        data_dict = {}
        data_dict.update({'name': name})
        # Удаляем ключ name что бы не задублировался
        if 'name' in keys:
            keys.remove('name')
        for key in keys:
            try:
                data_dict.update({key: data[key]})
            except Exception as e:
                logger.exception('Функция filter ошибка')
                sys.exit(1)
        return data_dict

    def get_script_run_status(self, keys=None):
        '''
        Получаем json со статусами по скриптам
        :param keys: Ключи для фильтрации
        :return:
        '''
        scripts_id = self._get_scripts_id()
        data_list = []
        if keys:
            # TODO: добавить exception
            for k, v in scripts_id.items():
                try:
                    # Получаем последний объект списка
                    data = self.api_get(uri=self.run_info_uri['get_script_history'], params='scriptId=' + v)[-1]
                except Exception as e:
                    logger.exception('Получение данныех с сервера')
                    sys.exit(1)
                else:
                    logger.info('Данные с сервера о статусе скрипта получены')
                    data_list.append(self.keys(data=data, name=k, keys=keys))
        else:
            for k, v in scripts_id.items():
                try:
                    data = self.api_get(uri=self.run_info_uri['get_script_history'], params='scriptId=' + v)[-1]
                except Exception as e:
                    logger.exception('Получение данныех с сервера')
                    sys.exit(1)
                else:
                    logger.info('Данные с сервера о статусе скрипта получены')
                    data_list.append(data)
        return data_list


def check_script_work(dict_list: list):
    # TODO добавить проверку времяни
    status_code = {
        '-1': 'Запущен',
        '0': 'Завершено',
        '1': 'Завершено с предупреждениями',
        '2': 'Завершено с ошибками',
        '3': 'Критическая ошибка',
        '4': 'Прервано',
    }
    current_data = datetime.datetime.now()
    body = ''
    subject = ''
    for data in dict_list:
        if data['result'] == 0:
            # TODO переписать на форматированные строки, режит глаза
            body = body + data['name'] + ' выполнился успешно: ' + data['endDate'].split('.')[0] + '\n'
            subject = 'Все роботы отработали'
        else:
            body = body + data['name'] + ' не выполнился: ' + data['endDate'].split('.')[0] + ' ' + status_code[
                str(data['result'])] + '\n'
            subject = 'Роботы не отработали'
    return body, subject


if __name__ == '__main__':
    logger = get_logger()
    logger.info('Скрипт запустился')

    # end_data = datetime.datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S.%f')
    # Путь к файлу конфигурации, находится в каталоге со скриптом
    config_path = os.path.join(os.getcwd(), 'setting.ini')
    try:
        # получаем данные для подключения к серверу
        srv_connect_data = get_config(config_path, 'ROOMY_API_DATA')
        tmp_scripts_data = get_config(config_path, 'SCRIPT_DATA')
        # Список скриптов для мониторинга
        mail_setting = get_config(config_path, 'MAIL')
    except configparser.NoSectionError as e:
        logger.exception('Ошибка чтения файла конфигурации')
        sys.exit(1)
    else:
        scripts = ast.literal_eval(tmp_scripts_data['script_list'])
        # Создаем экземляр класа
        r_script = RoomyScript(server=srv_connect_data['roomy_api_path'], username=srv_connect_data['roomy_api_user'],
                               password=srv_connect_data['roomy_api_password'], scripts_name=scripts)
        # Вызываем аутентефикацию
        r_script.auth(auth_url='/api/Authorization/Authorize')
        # Получаем словарь с именем скриптов и их id
        script_run_list = r_script.get_script_run_status(keys=['endDate', 'result', 'name'])
        # Проверяем статусы выполнения
        body, subject = check_script_work(script_run_list)
        # Шлем email
        send_email(mail_setting=mail_setting, body=body, subject=subject)
        logger.info('Скрипт закончил работу')
