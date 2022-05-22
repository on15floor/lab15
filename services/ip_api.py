import requests


class IpApi:
    def __init__(self, ip):
        self.endpoint = 'http://ip-api.com/json/'
        self.ip = ip
        self.data = self.get_info_by_ip()

    def get_info_by_ip(self):
        response = requests.get(url=self.endpoint + self.ip)
        return response.json()

    def get_country(self):
        return self.data.get('country', 'Unknown')

    def get_city(self):
        return self.data.get('city', 'Unknown')
