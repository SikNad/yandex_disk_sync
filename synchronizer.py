import os


class Synchronizer:
    """Класс для сравнения локальных файлов и облака."""

    def __init__(self, disk_client, local_folder_path, logger):
        self.disk = disk_client
        self.local_path = local_folder_path
        self.logger = logger
        self.previous_state = {}  # Словарь {имя_файла: время_изменения}

    def _get_local_files(self):
        """Возвращает словарь с локальными файлами и временем изменения."""
        files = {}
        for file_name in os.listdir(self.local_path):
            full_path = os.path.join(self.local_path, file_name)
            if os.path.isfile(full_path):
                files[file_name] = os.path.getmtime(full_path)
        return files

    def _process_new_files(self, current_files, cloud_files):
        """Загружает новые файлы. Если файл уже в облаке, перезаписывает."""
        new_files = [f for f in current_files if f not in self.previous_state]
        for file_name in new_files:
            if file_name in cloud_files:
                self._upload_modified(file_name)
            else:
                self._upload_new(file_name)

    def _process_modified_files(self, current_files):
        """Перезаписывает файлы, которые изменились локально."""
        modified_files = [
            f for f in current_files
            if f in self.previous_state and current_files[f] != self.previous_state[f]
        ]
        for file_name in modified_files:
            self._upload_modified(file_name)

    def _process_deleted_files(self, current_files):
        """Удаляет файлы из облака, если их удалили локально."""
        deleted_files = [f for f in self.previous_state if f not in current_files]
        for file_name in deleted_files:
            self._delete_cloud_file(file_name)

    def _upload_new(self, file_name):
        try:
            path = os.path.join(self.local_path, file_name)
            self.disk.load(path)
            self.logger.info(f'Файл {file_name} успешно записан.')
        except Exception as e:
            self.logger.error(f'Ошибка загрузки {file_name}: {e}')

    def _upload_modified(self, file_name):
        try:
            path = os.path.join(self.local_path, file_name)
            self.disk.reload(path)
            self.logger.info(f'Файл {file_name} успешно перезаписан.')
        except Exception as e:
            self.logger.error(f'Ошибка перезаписи {file_name}: {e}')

    def _delete_cloud_file(self, file_name):
        try:
            self.disk.delete(file_name)
            self.logger.info(f'Файл {file_name} успешно удален.')
        except Exception as e:
            self.logger.error(f'Ошибка удаления {file_name}: {e}')

    def run_sync(self):
        """Главный метод, который запускает полную синхронизацию."""
        current_files = self._get_local_files()
        cloud_files = self.disk.get_info()

        self._process_new_files(current_files, cloud_files)
        self._process_modified_files(current_files)
        self._process_deleted_files(current_files)

        self.previous_state = current_files
