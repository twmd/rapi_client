#TODO добавить исключения
import configparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ast

def get_config(config_path: str, section: str) -> dict:
    """
    Получаем конфиг
    :param config_path: путь до файла конфигурации
    :param section: имя секции
    :return: возвращает словарь из options указанной секции
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    return dict(config.items(section))

def send_email(mail_setting, body, subject):
    '''Посылаем email'''
    # try:
    #Переводим список в строку
    mail_to_tmp = ast.literal_eval(mail_setting['to'])
    mail_to = ', '.join(mail_to_tmp)
    message = MIMEMultipart()
    message["From"] = mail_setting['from']
    message['To'] = mail_to
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))
    smtp_obj = smtplib.SMTP(mail_setting['server'], int(mail_setting['port']))
    smtp_obj.starttls()
    smtp_obj.login(mail_setting['username'], mail_setting['password'])
    smtp_obj.sendmail(from_addr=mail_setting['from'], to_addrs=mail_to, msg=message.as_string())
    smtp_obj.quit()
    # except Exception as e:
    #     print(str(e) + ' !!!!exception')