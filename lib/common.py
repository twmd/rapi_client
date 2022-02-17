# TODO добавить исключения
import configparser
import os.path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ast
import logging
import logging.config

def get_logger():
    # Логер
    logging.config.fileConfig(os.path.join(os.getcwd(), 'logger.conf'), disable_existing_loggers = False)
    logger = logging.getLogger('plogger')
    return logger

logger = get_logger()

def get_config(config_path: str, section: str) -> dict:
    """
    Получаем конфиг
    :param config_path: путь до файла конфигурации
    :param section: имя секции
    :return: возвращает словарь из options указанной секции
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    logger.info('Фаил конфигуркции прочитан')
    return dict(config.items(section))


def send_email(mail_setting, body, subject):
    '''Посылаем email'''

    # Переводим список в строку
    mail_to_tmp = ast.literal_eval(mail_setting['to'])
    mail_to = ', '.join(mail_to_tmp)
    message = MIMEMultipart()
    message["From"] = mail_setting['from']
    message['To'] = mail_to
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))
    try:
        smtp_obj = smtplib.SMTP(mail_setting['server'], int(mail_setting['port']))
        smtp_obj.starttls()
        smtp_obj.login(mail_setting['username'], mail_setting['password'])
        smtp_obj.sendmail(from_addr=mail_setting['from'], to_addrs=mail_to, msg=message.as_string())
        smtp_obj.quit()
        logger.info(f'Почта отправлена {mail_to} ')
    except Exception as e:
        logger.exception('Ошибка отправки почты')

if __name__ == '__main__':
    pass
