import os
import requests


class YandexDisk:
    """Класс для работы с API Яндекс.Диска."""

    def __init__(self, token, cloud_folder_path):
        self.token = token
        self.cloud_folder_path = cloud_folder_path
        self.headers = {
            'Authorization': f'OAuth {self.token}',
            'Content-Type': 'application/json'
        }
        self.base_url = 'https://cloud-api.yandex.net/v1/disk/resources'

    def create_folder(self):
        """Создает папку в облаке, если её нет."""
        params = {'path': self.cloud_folder_path}
        response = requests.put(self.base_url, headers=self.headers, params=params)
        # 201 - создана, 409 - уже существует (это нормально)
        if response.status_code not in [201, 409]:
            response.raise_for_status()

    def _get_upload_url(self, cloud_file_path, overwrite):
        """Вспомогательный метод: получает ссылку для загрузки."""
        params = {'path': cloud_file_path, 'overwrite': str(overwrite).lower()}
        response = requests.get(f'{self.base_url}/upload', headers=self.headers, params=params)
        response.raise_for_status()
        return response.json().get('href')

    def load(self, local_path):
        """Загружает новый файл (с перезаписью, если такой уже есть)."""
        file_name = os.path.basename(local_path)
        cloud_path = f'{self.cloud_folder_path}/{file_name}'
        upload_url = self._get_upload_url(cloud_path, overwrite=False)

        with open(local_path, 'rb') as file:
            response = requests.put(upload_url, data=file)
            response.raise_for_status()
        return True

    def reload(self, local_path):
        """Перезаписывает существующий файл."""
        file_name = os.path.basename(local_path)
        cloud_path = f'{self.cloud_folder_path}/{file_name}'
        upload_url = self._get_upload_url(cloud_path, overwrite=True)

        with open(local_path, 'rb') as file:
            response = requests.put(upload_url, data=file)
            response.raise_for_status()
        return True

    def delete(self, filename):
        """Удаляет файл из облака."""
        cloud_path = f'{self.cloud_folder_path}/{filename}'
        params = {'path': cloud_path, 'permanently': 'true'}
        response = requests.delete(self.base_url, headers=self.headers, params=params)
        response.raise_for_status()
        return True

    def get_info(self):
        """Возвращает словарь {имя_файла: время_изменения} из облака."""
        params = {'path': self.cloud_folder_path, 'limit': 1000}
        response = requests.get(self.base_url, headers=self.headers, params=params)

        if response.status_code == 404:  # Если папки еще нет
            return {}

        response.raise_for_status()
        items = response.json().get('_embedded', {}).get('items', [])
        return {item['name']: item['modified'] for item in items}
