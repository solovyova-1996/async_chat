import json
from .variables import MAX_PACKAGE_SIZE, ENCODING
def get_messages(client):
    # получение данных размером 1024
    encoded_response = client.recv(MAX_PACKAGE_SIZE)
    decode_response = encoded_response.decode(ENCODING)
    response = json.loads(decode_response)
    if isinstance(response, dict):
        return response
    else:
        raise TypeError


def send_mesages(sock, messages):
    # if not isinstance(messages, dict):
    #     raise NonDictInputError
    # сериализуем данные переданные в сообщении в json
    json_messages = json.dumps(messages)
    print(messages)
    encoded_messages = json_messages.encode(ENCODING)
    # передача данных
    sock.send(encoded_messages)
