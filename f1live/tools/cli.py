#!/usr/bin/python
"""
A command-line interface.
"""
import sys

__all__ = ['query_yes_no', 'ask']

def query_yes_no(question, default="yes"):
    """
    Ask a yes or no question to standard output.

    @param question: question prompted to the user.
    @type question: C{string}.
    @param default: default answer to question: 'yes' (default) or 'no'.
    @type default: C{string}.
    @raise ValueError: when value of 'default' argument is unknown.
    """
    valid = {"yes":"yes", "y":"yes", "ye":"yes", "no":"no", "n":"no"}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("Unknown value of 'default' argument")
    while 1:
        print "{0} {1}".format(question, prompt),
        try:
            choice = raw_input().lower()
        except KeyboardInterrupt:
            print
            sys.exit()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            print "Please respond with 'yes' or 'no' (or 'y' or 'n').\n"

def ask(question, default=''):
    """
    Ask a question to standard output.

    @param question: question prompted to the user.
    @type question: C{string}.
    @param default: default answer to question (default='').
    @type default: C{string}.
    @return: standard input or default if empty answer is given.
    @rtype: C{string}.
    """
    print question,
    try:
        _input = raw_input()
    except KeyboardInterrupt:
        print
        sys.exit()
    if not _input:
        return default
    return _input

