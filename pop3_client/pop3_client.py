import socket
import ssl

HOST = 'pop.yandex.ru'
PORT = 995
USERNAME = 'your_username'
PASSWORD = 'your_password'

def send_request(sock, request):
    """
    Отправляет запрос через сокет.

    Args:
        sock: Сокет для отправки запроса.
        request: Запрос для отправки.
    """
    sock.send(request + b'\r\n')

def receive_response(sock):
    """
    Получает ответ от сервера.

    Args:
        sock: Сокет для получения ответа.

    Returns:
        str: Ответ от сервера.
    """
    return sock.recv(1024).decode()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        ssl_client_socket = ssl.wrap_socket(client_socket)

        print(receive_response(ssl_client_socket))

        send_request(ssl_client_socket, b'USER ' + USERNAME.encode())
        print(receive_response(ssl_client_socket))

        send_request(ssl_client_socket, b'PASS ' + PASSWORD.encode())
        print(receive_response(ssl_client_socket))

        send_request(ssl_client_socket, b'RETR 1')  # Получить первое письмо
        print(receive_response(ssl_client_socket))

        send_request(ssl_client_socket, b'QUIT')

if __name__ == "__main__":
    main()
