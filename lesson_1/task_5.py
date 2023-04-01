# 5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты
# из байтовового в строковый тип на кириллице.
import subprocess
from chardet.universaldetector import UniversalDetector

detector = UniversalDetector()


def ping_resurs(url_resurse, detector):
    """
    This function that pings resource and decodes the response
    :param url_resurse:url address
    :param detector: object detector to detect encoding
    """
    ping_ls = ['ping', url_resurse]
    ping = subprocess.Popen(ping_ls, stdout=subprocess.PIPE)
    for line in ping.stdout:
        detector.feed(line)
        if detector.done:
            break
    detector.close()
    encoding_res = detector.result.get('encoding')
    ping = subprocess.Popen(ping_ls, stdout=subprocess.PIPE)
    for line in ping.stdout:
        print(line.decode(encoding_res))


if __name__ == '__main__':
    for url in 'yandex.ru', 'youtube.com':
        ping_resurs(url,detector)
