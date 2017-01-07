from datetime import datetime
import os
import os.path
import re
import tempfile

import neovim

def today():
    """Get date in right format"""
    return datetime.now().strftime('%d-%m-%Y')


def inital_content():
    """Get header of diary"""
    return """---
title:		'Diary {}'
location:	'Krasnoyarsk, Markovskogo'
---

""".format(today())


def sort_key(string):
    match = re.match('.*diary_(\d{2})-(\d{2})-(\d{4})\.(?:rst|md){1}$', string)
    if match is None:
        return None
    else:
        return (int(match.group(3)), int(match.group(2)), int(match.group(1)), )


def grep(path, regex):
    regObj = re.compile('.*' + regex)
    res = []
    for root, dirs, fnames in os.walk(path):
        for fname in fnames:
            if regObj.match(fname):
                res.append(os.path.join(root, fname))
    return res


def all_notes(path, pattern):
    for folder, subfolders, files in os.walk(path):
        for file in files:
            file_path = os.path.join(os.path.abspath(folder), file)
            if file_path.startswith(os.path.join(path, '.git')):
                continue
            else:
                with open(file_path, 'r') as note:
                    if pattern in note.read():
                        yield file_path
                    else:
                        continue


def get_tags(line):
    tags_line = line.split(':')[1]
    [tag.strip() for tag in tags_line.split(' ')]

def by_tag(path, pattern):
    for folder, subfolders, files in os.walk(path):
        for file in files:
            file_path = os.path.join(os.path.abspath(folder), file)
            if file_path.startswith(os.path.join(path, '.git')):
                continue
            else:
                with open(file_path, 'r') as note:
                    for line in note:
                        if 'tags' in line:
                            line.split(',')
                    if pattern in note.read():
                        yield file_path
                    else:
                        continue


@neovim.plugin
class Main(object):
    """Root class for plugin"""
    def __init__(self, vim):
        self.vim = vim

    @neovim.command("Diary", nargs='*')
    def diary(self, args):
        home = os.getenv('HOME', '~')
        if args:
            dir, f = 'notes', args[0] + '.md'
        else:
            dir, f = 'diary', 'diary_' + today() + '.md'
        path = os.path.join(home, 'notebook', dir, f)
        self.vim.command('e {}'.format(path))
        if not os.path.exists(path):
            buf = self.vim.current.buffer
            buf[:] = inital_content().split("\n")

    @neovim.command("DiaryFind", nargs='*')
    def diary_find(self, args):
        pattern = 'diary' if not args else args[0]
        home = os.getenv('HOME', '~')
        _, path = tempfile.mkstemp('notes')
        files = grep(os.path.join(home, 'notebook'), pattern)
        files.sort(key=sort_key, reverse=True)

        with open(path, 'w') as tmp:
            for line in files:
                tmp.write(line + "\n")
        self.vim.command('view {}'.format(path))

    @neovim.command("DiaryFindIn", nargs='*')
    def diary_find_in(self, args):
        pattern = '' if not args else args[0]
        home = os.getenv('HOME', '~')
        _, path = tempfile.mkstemp('notes')
        notes = all_notes(os.path.join(home, 'notebook'), pattern)

        with open(path, 'w') as tmp:
            for line in notes:
                tmp.write(line + "\n")
        self.vim.command('view {}'.format(path))


    @neovim.command("DiaryFindIn", nargs='*')
    def diary_find_tag(self, args):
        pattern = '' if not args else args[0]
        home = os.getenv('HOME', '~')
        _, path = tempfile.mkstemp('notes')
        notes = all_notes(os.path.join(home, 'notebook'), pattern)

        with open(path, 'w') as tmp:
            for line in notes:
                tmp.write(line + "\n")
        self.vim.command('view {}'.format(path))
