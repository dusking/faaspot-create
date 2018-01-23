#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pprint
import logging
from collections import namedtuple

from .commands.command import commands
from .cli.arguments import parser, root_parsers


ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] [%(name)-8s] %(message)s', datefmt="%H:%M:%S")
ch.setFormatter(formatter)
ch_external = logging.StreamHandler()
ch_external.setLevel(logging.WARNING)
ch_external.setFormatter(formatter)
logger = logging.getLogger(__name__)


def set_logging_level(vrbose_level):
    internal_loggers = ['faascli', '__main__', 'utils', 'aws']
    internal_loggers_level = logging.INFO
    if vrbose_level >= 1:
        ch.setLevel(logging.DEBUG)
        internal_loggers_level = logging.DEBUG
    if vrbose_level >= 2:
        ch_external.setLevel(logging.INFO)
    if vrbose_level >= 3:
        ch_external.setLevel(logging.DEBUG)
    for logger_name in internal_loggers:
        i_logger = logging.getLogger(logger_name)
        i_logger.setLevel(internal_loggers_level)
        i_logger.addHandler(ch)


def main():
    args = parser.parse_args()
    input = dict(args._get_kwargs())

    selected_root_arg = [(root, input.get(root))
                         for root in root_parsers if input.get(root)][0]
    RootArg = namedtuple('RootArg', ['root', 'action'], verbose=False)
    root_arg = RootArg(*selected_root_arg)

    # handle the verbose input, and delete it.
    # it's not relevant for the fas commands..
    set_logging_level(args.verbose)
    del input[root_arg.root]
    del input['verbose']

    command = commands.get(root_arg.root)
    try:
        command_instance = command(root_arg.action, **input)
        result = command_instance.run_function()
        if any(isinstance(result, formatted_type) for formatted_type in [dict, list]):
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(result)
        else:
            print(result)
    except Exception as ex:
        print('Failed. {0}'.format(ex))


if __name__ == '__main__':
    main()
