import readAndSave
import requests
from bs4 import BeautifulSoup
import urllib

def read_info():
    info = readAndSave.read_json('id_pass.json', 'utf8')
    id, password = info['id'], info['password']

    return id, password




class AutoReserveEngoo:
    def __init__(self):
        id, password = read_info()
        #self.cookie = get_header(id, password) #여기서 클로저는 안되나?
        self.teacher_num = None
        self.time_to_learn = None

    def reserve(self):
        pass

    def find_others(self):
        pass

me = AutoReserveEngoo()
