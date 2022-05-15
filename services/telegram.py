import telebot

from config import Tokens
from services.ghostbin import Gostbin


BIRTHDAYS_FORMAT = """🎂Сегодня свои дни рождения празднуют:\n{birthdays}"""
BEGET_NEWS_FROMAT = """ℹ️Beget news:\n{news}"""
IOS_SALE_FORMAT = """{game_name}
{sale_percent} ({price_old} ₽ → <b>{price_new} ₽</b>)
🔗 <a href="{app_link}">Скачать в App Store</a>"""
ERROR_FORMAT = """😱Ошибка <b>{error_code}</b> [<a href="{traceback_link}">Traceback</a>]"""


class TBot:
    def __init__(self):
        self._bot = telebot.TeleBot(Tokens.TELEGRAM_BOT_TOKEN)

    def _send_message(self, chat_id, message, parse_mode=None):
        self._bot.send_message(
            chat_id=chat_id, text=message, parse_mode=parse_mode)

    def _send_caption(self, chat_id, photo_link, message, parse_mode=None):
        self._bot.send_photo(chat_id=chat_id, photo=photo_link,
                             caption=message, parse_mode=parse_mode)

    def send_birthdays(self, birthdays):
        if birthdays:
            chat_id = -1001254598595
            message = BIRTHDAYS_FORMAT.format(birthdays=birthdays)
            self._send_message(chat_id=chat_id, message=message)
        return len(birthdays.splitlines())

    def send_beget_news(self, news):
        if news:
            chat_id = -1001254598595
            message = BEGET_NEWS_FROMAT.format(news=news)
            self._send_message(chat_id=chat_id, message=message)
        return len(news.splitlines())

    def send_ios_sale(self, sales):
        if sales:
            chat_id = -1001560904244
            for game in sales:
                cover = game['cover']
                message = IOS_SALE_FORMAT.format(
                    game_name=game['game_name'],
                    sale_percent=game['sale_percent'],
                    price_old=game['price_old'],
                    price_new=game['price_new'],
                    app_link=game['app_link']
                )

                self._send_caption(chat_id=chat_id, message=message,
                                   photo_link=cover, parse_mode='HTML')
        return len(sales)

    def send_error(self, error: dict):
        chat_id = -1001254598595
        traceback_link = Gostbin().post_traceback(error.get('traceback', None))

        message = ERROR_FORMAT.format(
            error_code=error.get('error_code', None),
            traceback_link=traceback_link
        )
        self._send_message(chat_id=chat_id, message=message, parse_mode='HTML')
