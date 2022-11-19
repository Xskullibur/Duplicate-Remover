"""
This script identifies duplicate and invalid files from a directory and removes them.
"""

from collections import defaultdict
from utils import progressBar
import hashlib
import argparse
import os

# Formatters
NO_DUPLICATES_MSG = 'No Duplicate Files Found'
INVALID_FILES_DETECTED_MSG = 'Invalid Files Detected:'
REMOVING_INVALID_FILES_MSG = 'Removing invalid files...'
REMOVING_DUPLICATE_FILES_MSG = "Removing Duplicate Files..."
GETTING_FILES_MSG = 'Getting files from: "{}"'
BLUE_BOLD_UNDERLINE_ANSI = '\033[1;4m'
RED_BOLD_ANSI = '\033[31;49;1m'
STOP_ESCAPE_ANSI = '\033[0m'

# Default Values
FILE_SIZE_INDEX = 6
FILE_MTIME_INDEX = 8

# Messages
CANCELLED_BY_USER_MSG = 'File deletion cancelled by user: {}'
DELETE_CONFIRMATION_MSG = 'Are you sure you want to delete {} ([y]es, [n]o)'
SUCCESSFULLY_REMOVED_MSG = 'Successfully removed: {}'

# Error Messages
DIRECTORY_IS_EMPTY_MSG = 'Directory is empty'
ERROR_PATH_NOT_FOUND_MSG = 'ERROR: Path not found, '
INVALID_DIRECTORY_MSG = 'ERROR: Expected a directory but received a file, '
EMPTY_DIRECTORY_MSG = 'ERROR: Received empty directory'


# Helper Functions
def valid_file(file_entry: os.DirEntry):
    """
    Validate file by its size
    :param file_entry: DirEntry
    :return: bool
    """
    return file_entry.stat()[FILE_SIZE_INDEX] > 0


def get_hash(_filepath: str):
    """
    Get the MD5 hash of a file
    :param _filepath: str
    :return: str
    """
    with open(_filepath, 'rb') as file:
        return hashlib.md5(file.read()).hexdigest()


# Main Functions
def get_args():
    """
    Get user arguments from terminal
    :return: Arguments parsed by user
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', '-d', type=str, required=True,
                        help='Indicate the directory of interest to look for duplicate files')
    parser.add_argument('--invalid-files', '-i', action='store_true', default=False,
                        help='Use this flag to delete all invalid files found in the directory')
    parser.add_argument('--recursive', '-r', action='store_true', default=False,
                        help='use this flag to recursively search for duplicate files')
    parser.add_argument('--confirmation', '-c', action='store_true', default=False,
                        help='Use this flag to provide a confirmation message everytime the script attempts to delete '
                             'a file')
    return parser.parse_args()


def valid_arguments(_directory: str):
    """
    Validate arguments sent by user
    :param _directory: str
    :return: bool
    """
    if not _directory:
        # Missing Directory
        print(RED_BOLD_ANSI + EMPTY_DIRECTORY_MSG)
        return False

    if not os.path.isdir(_directory):
        # Invalid Directory
        print(RED_BOLD_ANSI + INVALID_DIRECTORY_MSG, _directory)
        return False

    if not os.path.exists(_directory):
        # Path not found
        print(RED_BOLD_ANSI + ERROR_PATH_NOT_FOUND_MSG, _directory)
        return False

    return True


def get_files(_directory: str, _recursive: bool):
    """
    Get all files in provided directory
    :param _directory: str
    :param _recursive: bool
    :return: List[DirEntry]
    """
    print(GETTING_FILES_MSG.format(_directory))
    _file_entries = []

    # List all files in directory
    dir_entry = os.scandir(_directory)

    # Validate files exist in directory
    if not dir_entry:
        print(RED_BOLD_ANSI + DIRECTORY_IS_EMPTY_MSG, directory)

    # Iterate through all the directories
    for entry in dir_entry:
        # Check if it's a file or directory
        if entry.is_file():
            _file_entries.append(entry)
        elif entry.is_dir() and _recursive:
            _file_entries += get_files(entry.path, _recursive)

    return _file_entries


def get_duplicates(_file_entries: list[os.DirEntry]):
    """
    Get all duplicate files in provided directory
    :param: _file_entries: list[os.DirEntry]
    :return: bool
    """
    # Sort files by modified time
    _file_entries.sort(key=lambda entry: entry.stat()[FILE_MTIME_INDEX])

    # Filter invalid files
    _invalid_files = [entry.path for entry in progressBar(_file_entries,
                                                          prefix='Identifying Invalid Files:',
                                                          suffix='Complete',
                                                          length=50) if not valid_file(entry)]

    # Get file hashes
    hash_dict = defaultdict(list)
    [hash_dict[get_hash(entry.path)].append(entry.path) for entry in progressBar(_file_entries,
                                                                                 prefix='Getting File Hashes:',
                                                                                 suffix='Complete',
                                                                                 length=50)]
    # Filter duplicate files
    _duplicate_files = [files for files in progressBar(hash_dict.values(),
                                                       prefix='Filtering Duplicate Files:',
                                                       suffix='Complete',
                                                       length=50) if len(files) > 1]
    return _invalid_files, _duplicate_files


def remove_duplicates_files(_duplicate_files, _prompt_flag):
    """
    Remove all duplicate files except for the first index
    :param _duplicate_files: list[str]
    :param _prompt_flag: bool
    """
    # Iterate through the different duplicate files
    for duplicates in progressBar(_duplicate_files, prefix='Deleting Duplicate Files:', suffix='Complete', length=50):
        # Iterate through the duplicate files
        for file_path in duplicates[1:]:

            if _prompt_flag:
                # Prompt user for confirmation
                res = input(DELETE_CONFIRMATION_MSG.format(BLUE_BOLD_UNDERLINE_ANSI + file_path + STOP_ESCAPE_ANSI))
                while res not in ['y', 'n']:
                    # Check for valid reply
                    res = input(DELETE_CONFIRMATION_MSG.format(BLUE_BOLD_UNDERLINE_ANSI + file_path + STOP_ESCAPE_ANSI))

                if res == 'y':
                    os.remove(file_path)
                    print(SUCCESSFULLY_REMOVED_MSG.format(file_path))
                else:
                    print(CANCELLED_BY_USER_MSG.format(file_path))

            else:
                os.remove(file_path)
                print(SUCCESSFULLY_REMOVED_MSG.format(file_path))


def remove_invalid_files(_invalid_files, _prompt_flag):
    """
    Remove all files with no file sizes
    :param _invalid_files: list[str]
    :param _prompt_flag: bool
    :return: bool
    """
    for file_path in progressBar(_invalid_files, prefix='Deleting Invalid Files:', suffix='Complete', length=50):
        if _prompt_flag:
            # Prompt user for confirmation
            res = input(DELETE_CONFIRMATION_MSG.format(BLUE_BOLD_UNDERLINE_ANSI + file_path + STOP_ESCAPE_ANSI))
            while res not in ['y', 'n']:
                # Check for valid reply
                res = input(DELETE_CONFIRMATION_MSG.format(BLUE_BOLD_UNDERLINE_ANSI + file_path + STOP_ESCAPE_ANSI))

            if res == 'y':
                os.remove(file_path)
                print(SUCCESSFULLY_REMOVED_MSG.format(file_path))
            else:
                print(CANCELLED_BY_USER_MSG.format(file_path))

        else:
            os.remove(file_path)
            print(SUCCESSFULLY_REMOVED_MSG.format(file_path))


if __name__ == '__main__':
    # Get user input and validate
    args = get_args()
    directory = args.directory
    recursive_flag = args.recursive
    prompt_flag = args.confirmation
    remove_invalid_file_flag = args.invalid_files
    if not valid_arguments(directory):
        exit(1)

    # Get files
    file_entries = get_files(directory, recursive_flag)
    invalid_files, duplicate_files = get_duplicates(file_entries)

    # Delete Duplicate Files
    if duplicate_files:
        print(REMOVING_DUPLICATE_FILES_MSG)
        remove_duplicates_files(duplicate_files, prompt_flag)
    else:
        print(NO_DUPLICATES_MSG)

    # Delete Invalid Files
    if remove_invalid_file_flag:
        print(REMOVING_INVALID_FILES_MSG)
        remove_invalid_files(invalid_files, prompt_flag)
    elif invalid_files:
        print(INVALID_FILES_DETECTED_MSG)
        [print(file_path) for file_path in invalid_files]

    print('Operation Completed')
