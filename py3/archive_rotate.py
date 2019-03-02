import os
import pathlib
import shutil
import sys
import datetime

# config
_location = '/tmp/testqq'
_min_disk_space_bytes = 30 * 10 ** 9
_max_files_to_remove = 10
_min_path_length = 10
_remove_function = shutil.rmtree  # for directories
# _remove_function = os.remove  # for files

# consts
_EXIT_STATUS_OK = 0
_EXIT_STATUS_PATH_TOO_SHORT = 1
_EXIT_STATUS_DIRECTORY_NOT_FOUND = 2


class Cleaner:
    def __init__(self):
        self.log = []
        self.print_log = False

    def ls(self, _dir, comment=None):
        files = os.listdir(_dir)
        self.log += ['[{}] directory: {}, content: {}'.format(comment, _dir, files)]

    @staticmethod
    def bytes_free_on_drive():
        fs_stat = os.statvfs(_location)
        return fs_stat.f_bavail * fs_stat.f_bsize

    def remove_first_file(self):
        files = os.listdir(_location)
        files.sort()
        if len(files) < 1:
            self.log += ['no more files in directory, exiting']
            self.end(_EXIT_STATUS_OK)
        file_to_remove = os.path.join(_location, files[0])
        if len(file_to_remove) >= _min_path_length:
            self.log += ['removing: {}'.format(file_to_remove)]
            _remove_function(file_to_remove)
        else:
            self.log += ['path too short: {}, operation aborted'.format(file_to_remove)]
            self.end(_EXIT_STATUS_PATH_TOO_SHORT)

    def check_directory(self):
        if not pathlib.Path(_location).exists():
            self.log += ['directory: {} not found'.format(_location)]
            self.end(_EXIT_STATUS_DIRECTORY_NOT_FOUND)

    def remove_files(self):
        self.ls(_location, 'before')
        no_of_files_to_remove = _max_files_to_remove
        while no_of_files_to_remove > 0:
            self.remove_first_file()
            no_of_files_to_remove -= 1
        self.ls(_location, 'after')

    def begin(self):
        self.log += ['begin: {}'.format(datetime.datetime.now())]

    def end(self, _exit_status):
        self.log += ['end: {}, with status: {}'.format(datetime.datetime.now(), _exit_status)]
        if self.print_log or _exit_status != 0:
            for entry in self.log:
                print(entry)
        sys.exit(_exit_status)

    def execute(self):
        self.begin()
        self.check_directory()
        bytes_free = self.bytes_free_on_drive()
        self.log += ['drive: {}, bytes free: {}'.format(_location, bytes_free)]
        if bytes_free < _min_disk_space_bytes:
            self.print_log = True  # to print log only if something is removed or failure happen
            self.remove_files()
        else:
            self.log += ["no action needed"]
            self.end(_EXIT_STATUS_OK)


if __name__ == "__main__":
    Cleaner().execute()
