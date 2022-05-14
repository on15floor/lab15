import os
import time
from datetime import datetime as dt


cur_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(cur_dir, '..'))
host_dir = os.path.abspath(os.path.join(project_dir, '..'))


def print_info(text):
    print('=' * 80 + f'\n[{dt.now().strftime("%H:%M:%S")}] {text}')


def sleep(seconds):
    for i in range(0, seconds):
        print('.', end='')
        time.sleep(1)
    print()


def exec_cmd(command, cwd):
    os.chdir(cwd)

    if isinstance(command, str):
        os.system(command)

    if isinstance(command, tuple):
        for cmd in command:
            os.system(cmd)


def main():
    start_time = dt.now()
    print_info('Starting updating Lab15.ru')

    exec_cmd('source venv/bin/activate', host_dir)
    exec_cmd(('git pull',
              'pip install --upgrade pip',
              'pip install -q -r requirements.txt',
              'pip install "pymongo[srv]"'),
             project_dir)

    print_info('Restarting application')
    exec_cmd('touch tmp/restart.txt', host_dir)
    sleep(5)

    print_info(f'Finished, execution time: {dt.now() - start_time}')


if __name__ == '__main__':
    main()
