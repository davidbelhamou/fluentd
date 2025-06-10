import contextlib
import platform
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

POS_FILE_PATH = '/var/log/fluentd/pos/python-logs.pos'
OLD_BASE_PATH_NAME = '/var/log/app'
NEW_BASE_PATH_NAME = './log'


class RemoveReadLogFiles:

    def __init__(self, pos_file_path: str | Path):
        self.pos_file_path = pos_file_path
        self.log_files_in_pos = []

    def _read_pos_file(self):
        with open(self.pos_file_path, 'r') as r:
            self.log_files_in_pos = r.readlines()

    @staticmethod
    def _parse_pos_file_lines(list_of_files: list[str]):
        pos_file_list = []
        for line in list_of_files:
            split_line = line.split("\t")
            path = split_line[0]
            size = int(split_line[1], 16)  # the size is written by fluentd in hexadecimal
            hash_file = int(split_line[2], 16)
            pos_file_list.append({'path': path, 'size': size, 'hash': hash_file})
        return pos_file_list

    @staticmethod
    def _format_path_for_local_dev(file_path: str, is_dev_mode=False):
        if is_dev_mode:
            return file_path.replace(OLD_BASE_PATH_NAME, NEW_BASE_PATH_NAME)
        return file_path

    @property
    def get_pos_log_file_list(self):
        self._read_pos_file()
        return self.log_files_in_pos

    def get_size_of_file(self, file_path: str | Path) -> int:
        stats = os.stat(self._format_path_for_local_dev(file_path))  # remove this in prod
        return stats.st_size

    def get_file_creation_datetime(self, file_path: str | Path) -> datetime:
        stats = None
        with contextlib.suppress(FileNotFoundError):
            # in case the file is in pos_file but the file already has been deleted
            stats = os.stat(self._format_path_for_local_dev(file_path))
        if platform.system() == 'Windows':
            return datetime.fromtimestamp(stats.st_birthtime) if stats else None
        else:
            return datetime.fromtimestamp(stats.st_ctime) if stats else None

    def delete_indexed_log_files(self):
        files_list = self._parse_pos_file_lines(self.get_pos_log_file_list)
        for log_file in files_list:
            creation_time = self.get_file_creation_datetime(log_file['path'])

            if creation_time and (creation_time < datetime.now() - timedelta(minutes=5)):

                if log_file['size'] < self.get_size_of_file(log_file['path']):

                    with contextlib.suppress(FileNotFoundError):
                        os.remove(self._format_path_for_local_dev(log_file['path']))
                        logger.info(f"File: {log_file['path']} hase been removed")
                else:
                    logger.info(f"File: {log_file['path']} has not been completely read")
            else:
                logger.info(f"File: {log_file['path']}  is not old enough or have been deleted")

def main():
    a = RemoveReadLogFiles(POS_FILE_PATH)
    a.delete_indexed_log_files()


if __name__ == '__main__':
    logger.info("Starting the log cleaner")
    main()