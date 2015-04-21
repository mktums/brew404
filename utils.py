# coding: utf-8
import os
from pip.vcs.git import Git
from pip.vcs.mercurial import Mercurial
from pip.vcs.subversion import Subversion, get_rev_options
import requests
import sys

from settings import CLONE_DIR, HOMEBREW_GIT_URL


def color(this_color, string_):
    return "\033[" + this_color + "m" + string_ + "\033[0m"


def bold(string_):
    return color('1', string_)


def color_status(response_code):
    if response_code == requests.codes.ok:
        return color('38;05;10', u"\u2714")
    else:
        return color('38;05;9', u"\u2718") + ' ' + unicode(response_code)


def update_sources():
    s = Git(HOMEBREW_GIT_URL)
    if not os.path.exists(CLONE_DIR):
        sys.stdout.write("  Cloning Homebrew sources… ")
        s.obtain(CLONE_DIR)
        sys.stdout.write('Done!\n')
    else:

        sys.stdout.write("  Updating Homebrew sources… ")
        s.update(CLONE_DIR, ('master',))
        sys.stdout.write('Done!\n')

    print bold(u"\u2139 Last commit: {}".format(
        s.get_revision(CLONE_DIR)[:8]
    ))


class CustomGit(Git):
    def get_bare(self, dest):
        url, _ = self.get_url_rev()
        rev_options = ['origin/master']
        rev_display = ''
        if self.check_destination(dest, url, rev_options, rev_display):
            self.run_command(['clone', '-q', '--bare', url, dest], show_stdout=False)

    def check_commit(self, sha, location):
        return self.run_command(['rev-parse', '--verify', sha], show_stdout=False, cwd=location)


class CustomHg(Mercurial):
    def check_commit(self, sha, location):
        return self.run_command(['log', '-T', "'{node}\n'", '-r', sha], show_stdout=False, cwd=location)

    def check_branch(self, branch, location):
        return self.run_command(['log', '-T', "'{branch}\n'", '-r', "branch({})".format(branch), '-l', '1'],
                                show_stdout=False, cwd=location)


class CustomSVN(Subversion):
    def obtain(self, dest):
        url, rev = self.get_url_rev()
        rev_options = get_rev_options(url, rev)
        if rev:
            rev_display = ' (to revision %s)' % rev
        else:
            rev_display = ''
        if self.check_destination(dest, url, rev_options, rev_display):
            self.run_command(['checkout', '-q'] + rev_options + [url, dest], show_stdout=False)

    def info(self, rev, location):
        return self.run_command(['info', location, '-r', rev], show_stdout=False, extra_environ={'LANG': 'C'})
