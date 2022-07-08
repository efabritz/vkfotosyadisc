import requests
import logging
import json

from pprint import pprint

def read_token(filename):
    with open(filename, 'r') as file:
        return file.read().strip()

class VKFoto:
    url = ''
    likes = 0
    def __init__(self, name, date, size, width = 0, height = 0):
        self.name = name
        self.date = date
        self.size = size
        self.width = width
        self.height = height

class VkDownload:
    URL = "https://api.vk.com/method/"
    def __init__(self, token, version):
        self.params =  {
        'access_token': token,
        'v': version
    }

    def download_fotos_vk(self, id, amount = 5):
        fotos_list = []
        url = f"{self.URL}photos.get"
        get_params = {
            'owner_id': id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1,
            'count': amount
        }
        request = requests.get(url, params = {**self.params, **get_params})
        fotos_json = request.json()
        logging.info('Fotos were downloaded form VK')

        likes_count = []
        for foto in fotos_json['response']['items']:
            largest_size = 's'
            url = ''
            width = ''
            height = ''
            sizes = foto['sizes']
            for size in sizes:
                if size['type'] > largest_size:
                    largest_size = size['type']
                    url = size['url']
                    width = size['width']
                    height = size['height']

            foto_name = ''
            type = url[-3:]

            if foto['likes']['count'] not in likes_count:
                likes_count.append(foto['likes']['count'])
                foto_name = f"{foto['likes']['count']}.{type}"
            else:
                foto_name = f"{foto['date']}.{type}"

            vkfoto = VKFoto(foto_name, foto['date'], largest_size, width, height)
            vkfoto.url = url

            logging.info('Fotos were added to the class object')
            fotos_list.append(vkfoto)
        return fotos_list


class YaUploader:
    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def create_post_path(self, path):
        put_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {'path': path}
        path_request = requests.put(url=put_url, params=params, headers=headers)
        logging.info('Catalog created on Yandex disc')
        return path_request.status_code

    def post_request(self, url, disk_file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"url": url, "path": disk_file_path, "overwrite": "true"}
        response = requests.post(upload_url, headers=headers, params=params)
        if response.status_code == 202:
            logging.info('Fotos were successfully sent to Yandex disc')
            print("Success")

if __name__ == '__main__':
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logging.info('Started')
    id = 636054
    logging.info('Fotos are downloaded form VK')
    vk_token = read_token('token.txt')
    downloader = VkDownload(vk_token, '5.131')
    fotos = downloader.download_fotos_vk(id)

    ya_token = read_token('yatoken.txt')
    ya_catalog = 'vkfotos2'
    json_string = []
    for foto in fotos:
        url = foto.url
        logging.info('Fotos are about to be send to Yandex disc')
        uploader = YaUploader(ya_token)
        uploader.create_post_path(ya_catalog)
        disk_file_path = f'{ya_catalog}/{foto.name}'
        uploader.post_request(url, disk_file_path)
        json_string.append({'file_name': foto.name, 'size': foto.size})
    logging.info('Json file is to be created')
    with open('json_data.json', 'w') as outfile:
        json.dump(json_string, outfile)
    logging.info('Finished')

