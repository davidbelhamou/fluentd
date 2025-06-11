import contextlib
import platform
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

POS_FILES = [
    '/var/log/fluentd/pos/python-logs.pos',
    '/var/log/fluentd/pos/service1-logs.pos'
]
OLD_BASE_PATH_NAME = '/var/log/app'
NEW_BASE_PATH_NAME = './log'
MINUTES_TO_WAIT_BEFORE_DELETE = 5


class RemoveReadLogFiles:

    def __init__(self, pos_file_path: str | Path):
        self.pos_file_path = pos_file_path
        self.log_files_in_pos = []

    def _read_pos_file(self):
        try:
            with open(self.pos_file_path, 'r') as r:
                self.log_files_in_pos = r.readlines()
        except FileNotFoundError:
            logger.warning(f"Pos file not found: {self.pos_file_path}")
            self.log_files_in_pos = []

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
        try:
            stats = os.stat(self._format_path_for_local_dev(file_path))
            return stats.st_size
        except FileNotFoundError:
            logger.warning(f"File not found: {file_path}")
            return 0

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
        """Delete log files that have been fully read by fluentd"""
        files_list = self._parse_pos_file_lines(self.get_pos_log_file_list)
        for file_info in files_list:
            file_path = file_info['path']
            file_size = self.get_size_of_file(file_path)
            if file_size == file_info['size']:
                try:
                    os.remove(self._format_path_for_local_dev(file_path))
                    logger.info(f"Deleted file: {file_path}")
                except FileNotFoundError:
                    logger.warning(f"File already deleted: {file_path}")
                except Exception as e:
                    logger.error(f"Error deleting file {file_path}: {e}")


def main():
    for pos_file in POS_FILES:
        logger.info(f"Processing pos file: {pos_file}")
        cleaner = RemoveReadLogFiles(pos_file)
        cleaner.delete_indexed_log_files()


if __name__ == '__main__':
    logger.info("Starting the log cleaner")
    main()