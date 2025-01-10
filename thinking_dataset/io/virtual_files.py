# @file thinking_dataset/io/virtual_files.py
# @description Handles metadata for virtual file operations.
# @version 1.0.1
# @license MIT

import datetime


class VirtualFile:

    def __init__(self, name: str, size: int, last_modified: float):
        self.name = name
        self.size = size
        self.last_modified = last_modified

    def __repr__(self):
        last_write_time = datetime.datetime.fromtimestamp(
            self.last_modified).strftime('%m/%d/%Y %I:%M %p')
        return f"{last_write_time} {self.size} {self.name}"


class VirtualFiles:

    def __init__(self):
        self.files = []

    def add_file(self, name: str, size: int, last_modified: float):
        self.files.append(VirtualFile(name, size, last_modified))

    def list_detailed(self):
        print("\n    Repository\n")
        print(f"{'Mode':<10} {'LastWriteTime':<25} {'Length':<10} {'Name'}")
        print(f"{'-'*10} {'-'*25} {'-'*10} {'-'*4}")
        for file in self.files:
            last_write_time = datetime.datetime.fromtimestamp(
                file.last_modified).strftime('%m/%d/%Y %I:%M %p')
            print(f"-{'-'*5:<9} {last_write_time:<25} "
                  f"{file.size:<10} {file.name}")

    def get_files(self):
        return self.files
