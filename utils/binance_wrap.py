import hashlib
import hmac
import json
import time
import urllib
from urllib.parse import urlparse
from config import Tokens

import requests


API_URL = 'https://api.binance.com/'
API_KEY = Tokens.BINANCE_API_KEY
API_SECRET = bytearray(Tokens.BINANCE_API_SECRET, encoding='utf-8')


class Binance:
    def __init__(self):
        self.pairs_price_usdt = {k: v for k, v in self._get_all_pairs()}

    def _call_api(self, url):
        url = API_URL + url + '?' + self._get_payload()
        headers = {
            "X-MBX-APIKEY": API_KEY,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.request(method='GET', url=url, headers=headers)
        return json.loads(response.text)

    @staticmethod
    def _get_payload():
        payload = {'timestamp': int(time.time() - 1) * 1000}
        payload_str = urllib.parse.urlencode(payload).encode('utf-8')
        sign = hmac.new(
            key=API_SECRET,
            msg=payload_str,
            digestmod=hashlib.sha256).hexdigest()
        return payload_str.decode("utf-8") + "&signature=" + str(sign)

    @staticmethod
    def _get_all_pairs():
        response = requests.get('https://api1.binance.com/api/v3/ticker/24hr')
        for pair in json.loads(response.text):
            symbol = pair['symbol']
            if symbol.endswith('USDT'):
                yield symbol, pair['lastPrice']

    def _get_price_usdt(self, ticker):
        return float(self.pairs_price_usdt.get(f'{ticker}USDT', 0))

    @staticmethod
    def _fmt_usd(amount: float) -> float:
        return round(amount, 2)

    @staticmethod
    def _fmt_crypto(amount: float) -> str:
        return f'{amount:.8f}'

    def get_wallet(self):
        account = self._call_api('api/v3/account')
        wallet = {
            'balance': 0,
            'coins': []
        }

        for coin in account['balances']:
            amount = float(coin['free'])
            if amount:
                ticker = coin['asset']
                price_usdt = self._get_price_usdt(ticker)
                balance_usdt = amount * price_usdt

                wallet['coins'].append({
                    'ticker': ticker,
                    'amount': self._fmt_crypto(amount),
                    'price_usdt': self._fmt_usd(price_usdt),
                    'balance_usdt': self._fmt_usd(balance_usdt)
                })
                wallet['balance'] += balance_usdt

        wallet['balance'] = self._fmt_usd(wallet['balance'])
        return wallet

    def get_deposits(self):
        account = self._call_api('/sapi/v1/lending/daily/token/position')
        deposit = {
            'balance': 0,
            'coins': []
        }

        for coin in account:
            ticker = coin['asset']
            amount_freeze = float(coin['totalAmount'])
            earn = float(coin['totalInterest'])
            amount_total = amount_freeze + earn
            price_in_usd = self._get_price_usdt(ticker)
            balance = amount_total * price_in_usd

            deposit['coins'].append({
                'ticker': ticker,
                'amount_freeze': self._fmt_crypto(amount_freeze),
                'earn': self._fmt_crypto(earn),
                'amount_total': self._fmt_crypto(amount_total),
                'price_in_usd': self._fmt_usd(price_in_usd),
                'balance': self._fmt_usd(balance),
                'profit': self._fmt_usd(earn * price_in_usd)
            })
            deposit['balance'] += balance

        deposit['balance'] = self._fmt_usd(deposit['balance'])
        return deposit
