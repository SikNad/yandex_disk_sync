import configparser
import sys
import os
import time
from logger import setup_logger
from yandex_disk import YandexDisk
from synchronizer import Synchronizer


def main():
    # 1. Читаем настройки
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    try:
        token = config['auth']['token']
        local_path = config['sync']['local_path']
        cloud_path = config['sync']['cloud_path']
        period = int(config['sync']['sync_period'])
        log_file = config['sync']['log_file']
    except KeyError as e:
        print(f'Ошибка в config.ini: отсутствует параметр {e}')
        sys.exit(1)

    # 2. Проверяем наличие локальной папки
    if not os.path.exists(local_path):
        print(f'Ошибка: Папка {local_path} не существует. Создайте её.')
        sys.exit(1)

    # 3. Настраиваем логирование
    logger = setup_logger(log_file)
    logger.info(f'Программа синхронизации файлов начинает работу с директорией {local_path}.')

    # 4. Инициализируем классы и создаем папку в облаке
    disk = YandexDisk(token, cloud_path)

    try:
        disk.create_folder()
    except Exception as e:
        print(f"Ошибка создания папки в облаке: {e}")
        sys.exit(1)

    synchronizer = Synchronizer(disk, local_path, logger)

    # 5. Запускаем цикл
    print("Программа запущена. Нажмите Ctrl+C для остановки.")
    try:
        while True:
            synchronizer.run_sync()
            time.sleep(period)
    except KeyboardInterrupt:
        logger.info('Программа остановлена пользователем.')
        print("\nПрограмма остановлена.")
        sys.exit(0)


if __name__ == '__main__':
    main()
