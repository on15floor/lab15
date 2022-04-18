from datetime import datetime

import tinvest

from config import Tokens, Vars


API_SECRET = Tokens.TINKOFF_SECRET_KEY
TINKOFF_TAX_PLUST = Vars.TINKOFF_TAX_PLUS
TINKOFF_ACCOUNTS = Vars.TINKOFF_ACCOUNTS


class Tinkoff:
    def __init__(self):
        self._client = tinvest.SyncClient(API_SECRET)
        self.accounts = {_id: _type for _id, _type in self._get_user_accounts()}
        self.usd_currency = self._get_usd_currency()

    def _get_user_accounts(self):
        if TINKOFF_ACCOUNTS:
            for _id, _type in TINKOFF_ACCOUNTS.items():
                yield _id, _type
            return
        accounts = self._client.get_accounts().payload.accounts
        for acc in accounts:
            _id = acc.broker_account_id
            _type = 'IIS' \
                if str(acc.broker_account_type).endswith('iis') else 'BASE'
            yield _id, _type

    def _get_usd_currency(self) -> float:
        res = self._client.get_market_orderbook(figi="BBG0013HGFT4", depth=1)
        return float(res.payload.last_price)

    def get_portfolio(self):
        portfolio = {'accounts': []}
        exchange_usd_operations = list()
        exchange_usd_profit = 0

        for account_id, account_type in self.accounts.items():
            account = {'id': account_id, 'type': account_type}
            account.update(self._get_tickers(account_id))
            operations, exchange_usd = self._get_operations(account_id)
            account.update(operations)
            account['profit_rub'] = self.get_profit(account)

            exchange_usd_operations += exchange_usd['operations']
            exchange_usd_profit += exchange_usd['profit']
            portfolio['accounts'].append(account)

        portfolio['stats'] = self.get_stats(portfolio['accounts'])
        portfolio.update({
            'exchange_usd': {
                'operations': self._fmt_date(exchange_usd_operations),
                'profit': exchange_usd_profit
            }
        })

        return portfolio

    def _get_tickers(self, account_id):
        free_usd = stocks_usd = stocks_rub = 0
        tickers = dict()

        response = self._client.get_portfolio(broker_account_id=account_id)
        for position in response.payload.positions:
            ticker = position.ticker
            balance = float(position.balance)
            if ticker == 'USD000UTSTOM':
                free_usd = balance
            else:
                company = position.name
                balance = float(position.balance)
                currency = position.average_position_price.currency.value
                price_avg = float(position.average_position_price.value)
                profit = float(position.expected_yield.value)
                price_now = (balance * price_avg + profit) / balance
                total = balance * price_now
                tickers[ticker] = {
                    'balance': balance,
                    'company': company,
                    'currency': currency,
                    'price_avg': price_avg,
                    'profit': profit,
                    'price_now': price_now,
                    'total': total
                }
                if currency == 'USD':
                    stocks_usd += total
                else:
                    stocks_rub += total

        res = {
            'tickers': tickers,
            'free_usd': free_usd,
            'free_rub': self._get_free_rub(account_id),
            'stocks_usd': stocks_usd,
            'stocks_rub': stocks_rub
            }
        res['free_sum'] = self.get_sum_rub(res, 'free')
        res['stocks_sum'] = self.get_sum_rub(res, 'stocks')

        return res

    def _get_free_rub(self, account_id):
        response = self._client.get_portfolio_currencies(
            broker_account_id=account_id)
        for position in response.payload.currencies:
            if position.currency.value == 'RUB':
                return float(position.balance)

    def _get_operations(self, account_id):
        operations = {
            'dividend_usd': 0.00,
            'dividend_rub': 0.00,
            'pay_in_usd': 0.00,
            'pay_in_rub': 0.00,
            'pay_out_usd': 0.00,
            'pay_out_rub': 0.00,
        }
        exchange_usd = {
            'operations': [],
            'profit': 0.00
        }
        response = self._client.get_operations(
            broker_account_id=account_id,
            from_=datetime(2020, 1, 1), to=datetime.now())
        for position in response.payload.operations:
            if position.operation_type.value == 'Dividend':
                key = f'dividend_{position.currency.value.lower()}'
                operations[key] += float(position.payment)
            elif position.operation_type.value == 'PayIn':
                key = f'pay_in_{position.currency.value.lower()}'
                operations[key] += float(position.payment)
            elif position.operation_type.value == 'PayOut':
                key = f'pay_out_{position.currency.value.lower()}'
                operations[key] += float(position.payment)
            elif position.figi == 'BBG0013HGFT4' and \
                    position.operation_type.value == 'Buy':
                amount = position.quantity
                price = float(position.price)
                total = amount * price
                profit = amount * self.usd_currency - total
                exchange = {
                    'date': position.date,
                    'amount': amount,
                    'price': price,
                    'total': total,
                    'profit': profit,
                }
                exchange_usd['operations'].append(exchange)
                exchange_usd['profit'] += profit
            pass

        sums = {
            'dividend_sum': self.get_sum_rub(operations, 'dividend'),
            'pay_in_sum': self.get_sum_rub(operations, 'pay_in'),
            'pay_out_sum': self.get_sum_rub(operations, 'pay_out'),
        }
        operations.update(sums)

        return operations, exchange_usd

    @staticmethod
    def get_profit(account: dict):
        stocks_sum = account.get('stocks_sum', 0)
        free_sum = account.get('free_sum', 0)
        pay_out_sum = account.get('pay_out_sum', 0)
        pay_in_sum = account.get('pay_in_sum')
        return stocks_sum + free_sum - pay_out_sum - pay_in_sum

    def get_sum_rub(self, data: dict, key: str):
        return data[f'{key}_rub'] + data[f'{key}_usd'] * self.usd_currency

    @staticmethod
    def get_stats(accounts):
        stats = {
            'dividend_usd': 0.00,                       # Дивиденды USD
            'dividend_rub': 0.00,                       # Дивиденды RUB
            'dividend_sum': 0.00,                       # Дивиденды Всего
            'pay_in_usd': 0.00,                         # Внесено USD
            'pay_in_rub': 0.00,                         # Внесено RUB
            'pay_in_sum': 0.00,                         # Внесено Всего
            'pay_out_usd': 0.00,                        # Выведено USD
            'pay_out_rub': 0.00,                        # Выведено RUB
            'pay_out_sum': 0.00,                        # Выведено Всего
            'free_usd': 0.00,                           # Свободные USD
            'free_rub': 0.00,                           # Свободные RUB
            'free_sum': 0.00,                           # Свободно Всего
            'stocks_usd': 0.00,                         # Акций USD
            'stocks_rub': 0.00,                         # Акций RUB
            'stocks_sum': 0.00,                         # Акций Всего
            'profit_rub': float(TINKOFF_TAX_PLUST)      # Профит
        }

        for acc in accounts:
            for key in stats.keys():
                stats[key] += acc.get(key, 0)

        return stats

    @staticmethod
    def _fmt_date(data: list):
        data.sort(key=lambda k: k['date'])
        for el in data:
            el['date'] = el['date'].strftime('%d.%m.%Y')
        return data
