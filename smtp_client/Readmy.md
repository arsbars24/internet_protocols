# SMTP Клиент для Отправки Писем с Вложениями

Этот проект представляет собой SMTP клиент для отправки электронных писем с вложениями. Письмо и вложения задаются через конфигурационный файл.

## Примеры файлов
### Конфигурационный файл (`config.txt`)

subject: Тестовое письмо с вложениями
to: recipient1@example.com, recipient2@example.com
attachments: attachment1.jpg, attachment2.pdf

### Текстовый файл (`body.txt`)

Здравствуйте,

Это тестовое письмо с вложениями.

С наилучшими пожеланиями,
Ваше Имя

## Использование
1. Заполните файл `config.txt` с нужными данными.

2. Напишите текст письма в файле `body.txt`.

3. Поместите все файлы-аттачменты в ту же директорию.

4. Запустите скрипт `smtp_client.py`:
    ```bash
    python smtp_client.py
    ```

## Примечания
- Скрипт автоматически обрабатывает строки, начинающиеся с точкой, чтобы соответствовать требованиям SMTP RFC.
- Граница (boundary) для MIME частей создается случайным образом для обеспечения уникальности.

## Требования
- Python 3.x
- Доступ к SMTP серверу (например, `smtp.yandex.ru` для отправки через Yandex).

## Логирование
Все операции логируются с помощью модуля `logging`. Логи можно просматривать в консоли для отладки и мониторинга процесса отправки.
