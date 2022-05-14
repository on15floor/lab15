import os
import ftplib
from datetime import datetime

from config import Vars


cur_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(cur_dir, '..'))
backups_dir = os.path.join(parent_dir, 'db/backups')


def print_header(text):
    print('=' * 80 + f'\n{text}')


def get_last_backup():
    backups = os.listdir(backups_dir)
    backup_paths = [os.path.join(backups_dir, basename) for basename in backups]
    return max(backup_paths, key=os.path.getctime)


def main():
    print_header('Start dumping')
    ftp = ftplib.FTP(Vars.HOST_SRV)
    ftp.login(Vars.HOST_LGN, Vars.HOST_PWD)

    ftp.cwd('/lab15.ru/lab15/db')

    ftp.sendcmd("TYPE i")
    if ftp.size("db.sqlite3") == os.path.getsize(get_last_backup()):
        print_header(f'The latest version of the backup has already been saved')
    else:
        backup_name = f'db_{datetime.now().strftime("%Y_%m_%d")}.sqlite3'
        target = os.path.join(backups_dir, backup_name)

        ftp.sendcmd("TYPE A")
        ftp.retrbinary('RETR db.sqlite3', open(target, 'wb').write)
        target_size = os.path.getsize(get_last_backup())
        print_header(f'The dump is saved: {target} [{target_size} bytes]')


if __name__ == '__main__':
    main()
