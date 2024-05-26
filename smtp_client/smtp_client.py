import base64
import socket
import ssl

# Данные SMTP сервера
host_addr = 'smtp.yandex.ru'
port = 465
user_name = 'ВАШ ЛОГИН'
application_password = 'ВАШ ПАРОЛЬ'


# Функция для отправки запроса и получения ответа
def request(socket, request):
    socket.send(request + b'\r\n')
    recv_data = socket.recv(65535).decode()
    return recv_data


# Функция для чтения конфигурации из файла
def read_config():
    config = {}
    with open('config.txt', 'r') as file:
        for line in file:
            key, value = line.split(':', 1)
            config[key.strip()] = value.strip()
    return config


# Функция для создания письма с вложениями
def create_email(config):
    boundary = "unique_boundary_string_123456"  # Уникальная граница для MIME частей
    email = f"From: {user_name}\n"
    email += f"To: {config['to']}\n"
    email += f"Subject: {config['subject']}\n"
    email += f"Content-Type: multipart/mixed; boundary=\"{boundary}\"\n\n"
    email += f"--{boundary}\n"

    # Текстовая часть письма
    email += "Content-Type: text/plain; charset=utf-8\n\n"
    with open('body.txt', 'r') as file:
        email += file.read() + '\n'

    # Вложения
    attachments = config['attachments'].split(',')
    for attachment in attachments:
        attachment = attachment.strip()
        email += f"--{boundary}\n"
        mime_type = "application/octet-stream"
        if attachment.endswith(".jpg"):
            mime_type = "image/jpeg"
        elif attachment.endswith(".pdf"):
            mime_type = "application/pdf"
        email += f"Content-Type: {mime_type}\n"
        email += f"Content-Disposition: attachment; filename=\"{attachment}\"\n"
        email += "Content-Transfer-Encoding: base64\n\n"
        with open(attachment, 'rb') as file:
            email += base64.b64encode(file.read()).decode() + '\n'

    email += f"--{boundary}--\n"
    return email


# Основная функция для отправки письма
def send_email():
    config = read_config()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((host_addr, port))
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        client = context.wrap_socket(client, server_hostname=host_addr)

        print(client.recv(1024).decode())
        print(request(client, bytes(f"EHLO {user_name}", 'utf-8')))
        base64login = base64.b64encode(user_name.encode())
        base64password = base64.b64encode(application_password.encode())

        print(request(client, b'AUTH LOGIN'))
        print(request(client, base64login))
        print(request(client, base64password))

        print(request(client, bytes(f'MAIL FROM:<{user_name}@yandex.ru>', 'utf-8')))

        recipients = config['to'].split(',')
        for recipient in recipients:
            print(request(client, bytes(f'RCPT TO:<{recipient.strip()}>', 'utf-8')))

        print(request(client, b'DATA'))

        email = create_email(config)
        print(request(client, bytes(email, 'utf-8')))
        print(request(client, b'.'))

        print(request(client, b'QUIT'))


if __name__ == "__main__":
    send_email()
