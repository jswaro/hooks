#!/usr/bin/env python

"""
Git pre-commit hook to validate commit messages.

Forked from Addam Hardy's hook at:
http://addamhardy.com/blog/2013/06/05/good-commit-messages-and-enforcing-them-with-git-hooks/

:author: Michael Cleaver <mcleaver@cray.com>
"""

import sys
import os
from subprocess import call

print os.environ.get('EDITOR')

if os.environ.get('EDITOR') != 'none':
    editor = os.environ['EDITOR']
else:
    editor = "vim"

message_file = sys.argv[1]
real_lineno = 0

def check_format_rules(line):
    """
    Checks the format of the line according to some basic rules.

    - First noncomment line must be 50 char or less
    - Second noncomment line must be empty
    - All other noncomment lines must be 72 char or less except for:
      - URLs
      - directory paths
      - quotes

    :param line: str line to be processed
    :return: str error message if error else bool False
    """
    global real_lineno
    if real_lineno == 1:
        if len(line) > 50:
            return ("Error {0}: First line should be less than 50 characters "
                    "in length.".format(real_lineno))
    if real_lineno == 2:
        if line:
            return "Error {0}: Second line should be empty.".format(real_lineno)
    exempt_prefixes = ['/', "./", "http", "www.", '>']
    exempt = any([line.startswith(x) for x in exempt_prefixes])
    if not exempt and len(line) > 72:
        return ("Error {0}: No line should be over 72 characters "
                "long.".format(real_lineno))
    return False


def main():
    global real_lineno
    while True:
        commit_msg = list()
        errors = list()
        with open(message_file) as commit_fd:
            for lineno, line in enumerate(commit_fd):
                stripped_line = line.strip()
                commit_msg.append(line)
                # Ignore comment unless it's line 2
                if not line.startswith('#') or real_lineno == 1:
                    real_lineno += 1
                    e = check_format_rules(stripped_line)
                    if e:
                        errors.append(e)
        if errors:
            with open(message_file, 'w') as commit_fd:
                commit_fd.write("{0}\n".format("# GIT COMMIT MESSAGE FORMAT "
                                               "ERRORS:"))
                for error in errors:
                    commit_fd.write("#    {0}\n".format(error))
                for line in commit_msg:
                    commit_fd.write(line)
            re_edit = raw_input("Invalid git commit message format. "
                                "Edit/Cancel/Force? (E/c/f) ")
            if re_edit.lower() in ('c', "cancel"):
                sys.exit(1)
            elif re_edit.lower() in ('f', "force"):
                continue
            else:
                call('{0} {1}'.format(editor, message_file), shell=True)
                continue
        break

if __name__ == "__main__":
    main()

