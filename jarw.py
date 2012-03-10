'''
JAR for Windows
Copyright (C) 2012 Igor Shishkin

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import argparse
import os
import re
import zipfile


class SuffixEncoder:

    @staticmethod
    def __findSuffix(name):
        return re.search(r"#\d+$", name)

    @staticmethod
    def isEncoded(name):
        suffix = SuffixEncoder.__findSuffix(name)
        return suffix and suffix.start()

    @staticmethod
    def encode(name, counter):
        return "{0}#{1}".format(name, counter)

    @staticmethod
    def decode(name):
        suffix = SuffixEncoder.__findSuffix(name)
        if suffix and suffix.start():
            return name[:suffix.start()]

        return name


def extract(source, target):
    ''' Extract all files from archive '''
    
    z = zipfile.ZipFile(source)
    files = {}
    for entry in z.infolist():
        normalName = os.path.normcase(entry.filename)
        if not normalName in files:
            files[normalName] = 0

        print(normalName)
        root, ext = os.path.splitext(entry.filename)
        if (files[normalName] > 0) or SuffixEncoder.isEncoded(root):
            targetName = SuffixEncoder.encode(root, files[normalName]) + ext
        else:
            targetName = entry.filename

        files[normalName] += 1
        targetPath = os.path.join(target, targetName)
        targetDir = os.path.dirname(targetPath)
        if not os.path.exists(targetDir):
            os.makedirs(targetDir)

        output = open(targetPath, "wb")
        output.write(z.read(entry))
        output.close()

    z.close()


def create(source, target, compression):
    ''' Create new archive '''

    z = zipfile.ZipFile(target, "w", compression)
    for currentPath, dirs, files in os.walk(source):
        for name in files:
            filePath = os.path.join(currentPath, name)
            archivePath = os.path.relpath(filePath, source)
            root, ext = os.path.splitext(archivePath)
            targetPath = SuffixEncoder.decode(root) + ext

            input = open(filePath, "rb")
            z.writestr(targetPath, input.read())
            input.close()

    z.close()


def main():
    parser = argparse.ArgumentParser(
        description="JAR manipulation utility", add_help=False)

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--create",
        action="store_true", help="create new archive")
    group.add_argument("-x", "--extract",
        action="store_true", help="extract all files from archive")

    parser.add_argument("-0", dest="compression",
        action="store_const", const=zipfile.ZIP_STORED,
        default=zipfile.ZIP_DEFLATED,
        help="store only; use no ZIP compression")

    parser.add_argument("source")
    parser.add_argument("target")

    args = parser.parse_args()
    if args.create:
        create(args.source, args.target, args.compression)
    elif args.extract:
        extract(args.source, args.target)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
