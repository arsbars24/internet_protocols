import socket
import ssl
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

HOST = 'pop.yandex.ru'
PORT = 995
USERNAME = 'your_username'
PASSWORD = 'your_password'

def send_request(sock, request):
    logging.debug(f"Sending: {request.decode()}")
    sock.send(request + b'\r\n')

def receive_response(sock):
    response = b""
    while True:
        chunk = sock.recv(1024)
        response += chunk
        if len(chunk) < 1024:
            break
    logging.debug(f"Received: {response.decode()}")
    return response.decode()

def list_messages(sock):
    send_request(sock, b'LIST')
    return receive_response(sock)

def get_headers(sock, msg_num):
    send_request(sock, f"TOP {msg_num} 0".encode())
    return receive_response(sock)

def get_message(sock, msg_num):
    send_request(sock, f"RETR {msg_num}".encode())
    return receive_response(sock)

def parse_email(data):
    headers, body = data.split('\r\n\r\n', 1)
    logging.info("Headers:\n" + headers)
    logging.info("Body:\n" + body[:500])  # Ограничить вывод тела для краткости
    return headers, body

def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            ssl_client_socket = ssl.wrap_socket(client_socket)

            logging.info(receive_response(ssl_client_socket))

            send_request(ssl_client_socket, b'USER ' + USERNAME.encode())
            logging.info(receive_response(ssl_client_socket))

            send_request(ssl_client_socket, b'PASS ' + PASSWORD.encode())
            logging.info(receive_response(ssl_client_socket))

            logging.info(list_messages(ssl_client_socket))

            msg_num = 1  # Получить первое сообщение
            headers = get_headers(ssl_client_socket, msg_num)
            logging.info("Headers of the first message:\n" + headers)

            message = get_message(ssl_client_socket, msg_num)
            headers, body = parse_email(message)

            send_request(ssl_client_socket, b'QUIT')
            logging.info(receive_response(ssl_client_socket))

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
