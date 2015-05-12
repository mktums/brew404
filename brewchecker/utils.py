# coding: utf-8
import os
import sys
import time
from signal import SIGINT

import click
from pip.utils import rmtree
from pip.vcs.git import Git

from brewchecker.settings import settings


def echo(message=None, nl=True, err=False, _color=None):
    log = settings.get('LOG')
    msg = message if message else u''
    if nl:  # Nasty click.echo's bug =(
        msg += u'\n'
    if log:
        click.echo(msg, log, nl=False, err=err, color=_color)
    if not settings.get('QUIET'):
        click.echo(msg, None, nl=False, err=err, color=_color)


def is_ok(response_code):
    if response_code in (200, 226):
        return True
    return False


def get_brew_repo():
    return Git(settings.get('BREW_GIT_URL'))


def get_brew_last_commit(repo):
    return repo.get_revision(settings.get('BREW_CLONE_DIR'))


def update_sources():
    s = get_brew_repo()
    echo(u"Cloning Homebrew sources... ", nl=False)
    s.obtain(settings.get('BREW_CLONE_DIR'))
    echo(click.style(u"done!", "green"))
    echo(u"Last commit: " + click.style(u"{}\n".format(get_brew_last_commit(s)[:8]), "green"))
    return s


class CD:
    """Context manager for changing the current working directory"""
    def __init__(self, new_path):
        self.newPath = os.path.expanduser(new_path)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def clean():
    echo(u'Cleaning up {}...'.format(settings.get('BASE_DIR')), nl=False)
    rmtree(settings.get('BASE_DIR'))
    echo(click.style(u'done!', 'green'))


class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.interval = self.end - self.start
