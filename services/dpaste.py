import requests


class DPaste:
    def __init__(self):
        self.endpoint = 'https://dpaste.org/api/'

    def post_traceback(self, traceback):
        params = {
            'content': traceback,
            'lexer': 'python',
            'format': 'url'
        }
        response = requests.post(url=self.endpoint, data=params)
        return response.text.strip() + '/slim'
