import logging


def setup_logger(log_file_path):
    """Настраивает и возвращает объект логгера."""
    logger = logging.getLogger('file_synchronizer')

    # Устанавливаем максимальный уровень логирования (INFO и выше, включая ERROR)
    logger.setLevel(logging.INFO)

    # Если у логгера уже есть обработчики, не добавляем их повторно
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')

        # Формат лога: дата время уровень сообщение
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
