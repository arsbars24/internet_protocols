import base64
import socket
import ssl
import mimetypes
import logging
import random
import string

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Данные SMTP сервера
host_addr = 'smtp.yandex.ru'
port = 465
user_name = ''
application_password = ''

# Функция для отправки запроса и получения ответа построчно
def request(sock, request):
    logging.debug(f"Sending: {request.decode()}")
    sock.sendall(request + b'\r\n')
    recv_data = b""
    while True:
        chunk = sock.recv(1024)
        recv_data += chunk
        if len(chunk) < 1024:
            break
    response = recv_data.decode()
    logging.debug(f"Received: {response}")
    return response

# Функция для чтения конфигурации из файла
def read_config():
    config = {}
    with open('config.txt', 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.split(':', 1)
            config[key.strip()] = value.strip()
    return config

# Функция для создания уникальной границы
def create_boundary():
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return f"unique_boundary_string_{random_part}"

# Функция для обработки строк с точками
def handle_dot_stuffing(text):
    lines = text.split('\n')
    for i in range(len(lines)):
        if lines[i].startswith('.'):
            lines[i] = '.' + lines[i]
    return '\n'.join(lines)

# Функция для создания письма с вложениями
def create_email(config):
    boundary = create_boundary()

    email = f"From: {user_name}@yandex.ru\n"
    email += f"To: {config['to']}\n"
    email += f"Subject: {config['subject']}\n"
    email += f"MIME-Version: 1.0\n"
    email += f"Content-Type: multipart/mixed; boundary=\"{boundary}\"\n\n"
    email += f"--{boundary}\n"

    # Текстовая часть письма
    email += "Content-Type: text/plain; charset=utf-8\n"
    email += "Content-Transfer-Encoding: 7bit\n\n"
    with open('body.txt', 'r', encoding='utf-8') as file:
        email += handle_dot_stuffing(file.read()) + '\n'

    # Вложения
    attachments = config['attachments'].split(',')
    for attachment in attachments:
        attachment = attachment.strip()
        email += f"--{boundary}\n"
        mime_type, _ = mimetypes.guess_type(attachment)
        if mime_type is None:
            mime_type = "application/octet-stream"
        email += f"Content-Type: {mime_type}; name=\"{attachment}\"\n"
        email += f"Content-Disposition: attachment; filename=\"{attachment}\"\n"
        email += "Content-Transfer-Encoding: base64\n\n"
        with open(attachment, 'rb') as file:
            email += base64.b64encode(file.read()).decode() + '\n'

    email += f"--{boundary}--\n"
    return email

# Основная функция для отправки письма
def send_email():
    config = read_config()
    context = ssl.create_default_context()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ssock:
            logging.info(f"Connecting to {host_addr}:{port}")
            ssock.connect((host_addr, port))
            logging.info("Connection established")
            with context.wrap_socket(ssock, server_hostname=host_addr) as client:
                logging.debug(client.recv(1024).decode())
                logging.debug(request(client, f"EHLO {user_name}".encode('utf-8')))
                base64login = base64.b64encode(user_name.encode())
                base64password = base64.b64encode(application_password.encode())

                logging.debug(request(client, b'AUTH LOGIN'))
                logging.debug(request(client, base64login))
                logging.debug(request(client, base64password))

                logging.debug(request(client, f"MAIL FROM:<{user_name}@yandex.ru>".encode('utf-8')))

                recipients = config['to'].split(',')
                for recipient in recipients:
                    logging.debug(request(client, f"RCPT TO:<{recipient.strip()}>".encode('utf-8')))

                logging.debug(request(client, b'DATA'))

                email = create_email(config)
                client.sendall(email.encode('utf-8') + b'\r\n.\r\n')
                logging.debug(request(client, b'QUIT'))
    except socket.timeout as e:
        logging.error(f"A socket timeout occurred: {e}")
    except socket.error as e:
        logging.error(f"A socket error occurred: {e}")
    except ssl.SSLError as e:
        logging.error(f"An SSL error occurred: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    send_email()
