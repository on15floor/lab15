import subprocess

from config import PROJECT_PATH


def get_gitlog():
    _format = '--format=format:' \
              '<span class="one-dark-text-purple">%h</span>-' \
              '<span class="one-dark-text-green">(%ar)</span> %s - ' \
              '<span class="one-dark-text-blue"><b>%an</b></span>' \
              '<span class="badge bg-warning text-dark">%d</span>'
    command = [
        'git',
        'log',
        '--graph',              # Вывести граф
        '--all',                # Все ветки
        _format,                # Форматирование
        '--abbrev-commit',      # Сокращенный номер коммита
        '--date=relative',      # Desc
        '--since=6 month ago',  # Коммиты за последние 6 месяцев
    ]
    result = subprocess.run(command, cwd=PROJECT_PATH, stdout=subprocess.PIPE)
    git_log = result.stdout.decode("utf-8")
    return git_log.replace('\n', '<br />')
