import telebot

from config import Tokens


class TBot:
    def __init__(self):
        self._bot = telebot.TeleBot(Tokens.TELEGRAM_BOT_TOKEN)

    def send_message(self, chat_id=-1001254598595, message=''):
        self._bot.send_message(chat_id=chat_id, text=message)

    def send_caption(self, chat_id, photo_link, message, parse_mode=None):
        self._bot.send_photo(chat_id=chat_id, photo=photo_link,
                             caption=message, parse_mode=parse_mode)

    def send_birthdays(self, birthdays):
        if birthdays:
            message = f'🎂Сегодня свои дни рождения празднуют:\n {birthdays}'
            self.send_message(message=message)
        return birthdays.count('\n')
