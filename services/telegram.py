# noinspection PyPackageRequirements
import telebot

from config import Tokens, Config
from services.ip_api import IpApi
from services.dpaste import DPaste
from core.models import Reminerds, Birthdays, BegetNews, IosSales


BIRTHDAYS_HEADER = '🎂<b>Дни рождения сегодня:</b>\n'
REMINDER_HEADER = '💡<b>Напоминание:</b>\n'
BEGET_NEWS_HEADER = 'ℹ️<b>Beget news:</b>\n'
HR_HEADER = f"\n{'-' * 30}\n"

IOS_SALE_FORMAT = """{game_name}
{sale_percent} ({price_old} ₽ → <b>{price_new} ₽</b>)
🔗 <a href="{app_link}">Скачать в App Store</a>"""
ERROR_FORMAT = """😱Ошибка <b>{error_code}</b> [<a href="{traceback_link}">Traceback</a>]
🌍{ip}[{country}, {city}]"""


class TBot:
    def __init__(self):
        self._bot = telebot.TeleBot(Tokens.TELEGRAM_BOT_TOKEN)

    def _send_message(self, chat_id, message, parse_mode=None):
        self._bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=parse_mode,
            disable_web_page_preview=True
        )

    def _send_caption(self, chat_id, photo_link, message, parse_mode=None):
        self._bot.send_photo(
            chat_id=chat_id,
            photo=photo_link,
            caption=message,
            parse_mode=parse_mode
        )

    def send_daily(self):
        chat_id = -1001254598595
        msg = ''
        daily_map = {
            BIRTHDAYS_HEADER: list(Birthdays().get_birthdays_today()),
            REMINDER_HEADER: list(Reminerds().get_reminders_today()),
            BEGET_NEWS_HEADER: list(BegetNews().get_beget_news_today())
        }

        for header, data in daily_map.items():
            if data:
                if msg:
                    msg = msg + HR_HEADER
                msg = msg + header + '\n'.join(data)
        if msg:
            self._send_message(chat_id=chat_id, message=msg, parse_mode='HTML')
            return True
        return False

    def send_ios_sale(self):
        sales = IosSales().get_ios_sale_today()
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

    def send_error(self, error: dict, ip: str):
        chat_id = -1001254598595
        traceback_link = DPaste().post_traceback(error.get('traceback', None))
        ip_data = IpApi(ip)

        message = ERROR_FORMAT.format(
            error_code=error.get('error_code', None),
            traceback_link=traceback_link,
            ip=ip,
            country=ip_data.get_country(),
            city=ip_data.get_city()
        )
        if not Config.FLASK_DEBUG:
            self._send_message(
                chat_id=chat_id, message=message, parse_mode='HTML')
