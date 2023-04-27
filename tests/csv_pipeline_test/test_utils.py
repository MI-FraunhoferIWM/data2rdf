import os


def check_file_identifier_in_folder(folder, identifier):
    for file in os.listdir(folder):
        if identifier in file:
            return True
    return False
