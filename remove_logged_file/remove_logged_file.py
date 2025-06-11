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
    '/var/log/fluentd/pos/service1-logs.pos',
    '/var/log/fluentd/pos/service2-logs.pos'
]
OLD_BASE_PATH_NAME = '/var/log/app'
NEW_BASE_PATH_NAME = './log'
MINUTES_TO_WAIT_BEFORE_DELETE = 5
# Allow for small differences in file sizes (e.g. due to newlines or buffering)
MAX_SIZE_DIFF = 50  # bytes


class RemoveReadLogFiles:

    def __init__(self, pos_file_path: str | Path):
        self.pos_file_path = pos_file_path
        self.log_files_in_pos = []

    def _read_pos_file(self):
        try:
            with open(self.pos_file_path, 'r') as r:
                self.log_files_in_pos = r.readlines()
                logger.info(f"Read {len(self.log_files_in_pos)} files from pos file {self.pos_file_path}")
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
            formatted_path = self._format_path_for_local_dev(file_path)
            stats = os.stat(formatted_path)
            size = stats.st_size
            logger.debug(f"File {formatted_path} size: {size}")
            return size
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

    def is_file_old_enough_to_delete(self, file_path: str | Path) -> bool:
        """Check if the file is old enough to be deleted based on MINUTES_TO_WAIT_BEFORE_DELETE"""
        creation_time = self.get_file_creation_datetime(file_path)
        if not creation_time:
            logger.warning(f"Could not get creation time for {file_path}")
            return False
        
        age = datetime.now() - creation_time
        is_old_enough = age >= timedelta(minutes=MINUTES_TO_WAIT_BEFORE_DELETE)
        logger.info(f"File {file_path} age: {age.total_seconds()/60:.1f} minutes, old enough to delete: {is_old_enough}")
        return is_old_enough

    def delete_indexed_log_files(self):
        """Delete log files that have been fully read by fluentd and are old enough"""
        files_list = self._parse_pos_file_lines(self.get_pos_log_file_list)
        logger.info(f"Found {len(files_list)} files in pos file to check")
        for file_info in files_list:
            file_path = file_info['path']
            file_size = self.get_size_of_file(file_path)
            pos_size = file_info['size']
            size_diff = abs(file_size - pos_size)
            logger.info(f"Checking file {file_path}: current size={file_size}, pos size={pos_size}, diff={size_diff}")
            
            # Check if the file is old enough to be deleted
            if not self.is_file_old_enough_to_delete(file_path):
                logger.info(f"Skipping file {file_path}: not old enough to delete (must be at least {MINUTES_TO_WAIT_BEFORE_DELETE} minutes old)")
                continue
            
            # Check if the size difference is within our allowed tolerance
            if size_diff <= MAX_SIZE_DIFF:
                try:
                    formatted_path = self._format_path_for_local_dev(file_path)
                    os.remove(formatted_path)
                    logger.info(f"Deleted file: {formatted_path}")
                except FileNotFoundError:
                    logger.warning(f"File already deleted: {file_path}")
                except Exception as e:
                    logger.error(f"Error deleting file {file_path}: {e}")
            else:
                logger.info(f"Skipping file {file_path}: sizes don't match (current={file_size}, pos={pos_size}, diff={size_diff})")


def main():
    for pos_file in POS_FILES:
        logger.info(f"Processing pos file: {pos_file}")
        cleaner = RemoveReadLogFiles(pos_file)
        cleaner.delete_indexed_log_files()


if __name__ == '__main__':
    logger.info("Starting the log cleaner")
    main()