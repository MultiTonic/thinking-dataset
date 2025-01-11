# @file thinking_dataset/io/rfiles.py
# @description Manages a collection of remote files.
# @version 1.0.2
# @license MIT

from thinking_dataset.io.rfile import RFile


class RFiles:

    def __init__(self):
        self.files = []

    def add_file(self, name: str, size: int, modified: str):
        self.files.append(RFile(name, size, modified))

    def list_detailed(self):
        print("\n    Repository\n")
        print(f"{'Mode':<10} {'LastWriteTime':<25} {'Length':<10} {'Name'}")
        print(f"{'-'*10} {'-'*25} {'-'*10} {'-'*4}")
        for file in self.files:
            print(file)

    def get_files(self):
        return self.files

    def __iter__(self):
        return iter(self.files)
