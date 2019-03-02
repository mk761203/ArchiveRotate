#!/usr/bin/python
# https://github.com/mk761203/ArchiveRotate

import os
import sys
import datetime
from optparse import OptionParser

# consts
_EXIT_STATUS_OK = 0
_EXIT_STATUS_LACK_OF_PARAMS = 1
_EXIT_STATUS_PATH_TOO_SHORT = 10
_EXIT_STATUS_DIR_NOT_FOUND = 11

# config
parser = OptionParser()
parser.add_option("-p", "--path", type="string", help="[required] location where backup files/folders are stored")
parser.add_option("-m", "--min-disk-space", type="long", help="[required] minimum required disk space in bytes")
parser.add_option("-e", "--eval-min-disk-space", type="string",
                  help="expression which evaluate to minimum required disk space in bytes e.g. 30 * 10 ** 9")
parser.add_option("-n", "--max-files-to-remove", type="long", default=1, help="maximum number of files to remove")
parser.add_option("-d", "--min-path-length", type="long", default=2, help="minimum path length (defense)")
parser.add_option("-l", "--log-directory-content", action='store_true', default=False,
                  help="write to log directory content before and after rotate")
(opts, args) = parser.parse_args(sys.argv)
_location = opts.path
_min_disk_space_bytes = eval(opts.eval_min_disk_space) if opts.eval_min_disk_space else opts.min_disk_space
_max_files_to_remove = opts.max_files_to_remove
_min_path_length = opts.min_path_length
_log_directory_content = opts.log_directory_content
# import shutil; _remove_function = shutil.rmtree  # for directories
_remove_function = os.remove  # for files

if None in [_location, _min_disk_space_bytes]:
    print('\nLack of required parameter(s).\n')
    parser.print_help()
    sys.exit(_EXIT_STATUS_LACK_OF_PARAMS)


class ArchiveRotate:
    def __init__(self):
        self.log = []
        self.print_log = False

    def ls(self, _dir, comment=None):
        files = os.listdir(_dir)
        if _log_directory_content:
            self.log += ['[{0}] file: {1}, content: {2}'.format(comment, _dir, files)]

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
            self.log += ['removing: {0}'.format(file_to_remove)]
            _remove_function(file_to_remove)
        else:
            self.log += ['path too short: {0}, operation aborted'.format(file_to_remove)]
            self.end(_EXIT_STATUS_PATH_TOO_SHORT)

    def check_directory(self):
        if not os.path.exists(_location):
            self.log += ['file: {0} not found'.format(_location)]
            self.end(_EXIT_STATUS_DIR_NOT_FOUND)

    def remove_files(self):
        self.ls(_location, 'before')
        no_of_files_to_remove = _max_files_to_remove
        while no_of_files_to_remove > 0 and self.bytes_free_on_drive() < _min_disk_space_bytes:
            self.remove_first_file()
            no_of_files_to_remove -= 1
        self.ls(_location, 'after')

    def begin(self):
        self.log += ['begin: {0}'.format(datetime.datetime.now())]

    def end(self, _exit_status):
        self.log += ['end: {0}, with status: {1}'.format(datetime.datetime.now(), _exit_status)]
        if self.print_log or _exit_status != 0:
            for entry in self.log:
                print(entry)
        sys.exit(_exit_status)

    def get_free_space(self):
        bytes_free = self.bytes_free_on_drive()
        self.log += ['drive: {0}, bytes free: {1}'.format(_location, bytes_free)]
        return bytes_free

    def execute(self):
        self.begin()
        self.check_directory()
        if self.get_free_space() < _min_disk_space_bytes:
            self.log += ['not enough disk space, rotate needed']
            self.print_log = True  # to print log only if something is removed or failure happen
            self.remove_files()
        else:
            self.log += ["no action needed"]
        self.get_free_space()
        self.end(_EXIT_STATUS_OK)


if __name__ == "__main__":
    ArchiveRotate().execute()
