#!/data/data/com.termux/files/usr/bin/python


from utils import (
    cwd,
)
#!/data/data/com.termux/files/usr/bin/python


from os.path import dirname as dirn
from os.path import isfile as isf
from os.path import join as jn
from pathlib import Path
import os


class DirectoryWalker:
    # a forward iterator that traverses a directory tree

    def __init__(self, directory):
        self.stack = [directory]
        self.files = []
        self.index = 0

    def __getitem__(self, index):
        while 1:
            try:
                file = self.files[self.index]
                self.index = self.index + 1
            except IndexError:
                # pop next directory from stack
                self.directory = self.stack.pop()
                self.files = os.listdir(self.directory)
                self.index = 0
            else:
                # got a filename
                fullname = jn(self.directory, file)
                if os.path.isdir(fullname) and not os.path.islink(fullname):
                    self.stack.append(fullname)
                return fullname


if __name__ == "__main__":
    cwd = Path.cwd()
    for file in DirectoryWalker(str(cwd)):
        if isf(file) and file.endswith("README.pdf"):
            dirname1 = dirn(file)
            full_name = file
            dirs = dirname1.split("/")
            last_dir = dirs[len(dirs) - 1]
            new_name = last_dir + ".pdf"
            if not (os.path.exists(new_name)):
                try:
                    os.rename(file, jn(dirname1, new_name))
                    print("file %s renamed to %s" % (full_name, new_name))

                except IOError as e:
                    print(e)
