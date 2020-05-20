#!/usr/bin/env python3
# -*-encoding: utf-8-*-
# Author: Danil Kovalenko

import argparse
import typing as tp
import logging
from pprint import pformat

from argplus.err import ArgplusException


log = logging.getLogger(__name__)


class CLIHandlerLookupError(LookupError):
    pass


class ArgumentAdderLookupError(LookupError):
    pass


class CLIArgsConfigurator:
    """
    Base class for any AgsConfigurator, class which implements builder methods
    for each desired CLI parameters.
    """

    def __init__(self, args_help: dict):
        self.args_help = args_help

    def add_argument(self, parser, arg_name):
        adder = self._get_adder(arg_name)
        kw_arguments = adder()

        help_msg = self.args_help.get(arg_name, '')
        if not help_msg:
            log.warning(f'Failed to find help message for: {arg_name}')

        kw_arguments['help'] = help_msg
        name_or_flags = kw_arguments.pop('name_or_flags')
        parser.add_argument(*name_or_flags, **kw_arguments)

    def to_args_dict(self, *args, **kwargs):
        args = {
            'name_or_flags': [*args],
            **kwargs
        }
        return args

    def _get_adder(self, arg_name):
        """Get adder method by argument name"""
        method_name = arg_name + '_adder'
        method = getattr(self, method_name, NotImplemented)
        if method is NotImplemented:
            raise ArgumentAdderLookupError(f'{arg_name} unknown for '
                                           f'{type(self).__name__}')
        return method

    def add_callback(self, parser, func):
        parser.set_defaults(func=func)

    def add_arguments(self,
                      parser: argparse.ArgumentParser,
                      arg_names: tp.Iterable[str],
                      handler: tp.Callable = None):
        """
        Binds arguments to parser. Assigns handler

        """
        for arg_name in arg_names:
            self.add_argument(parser, arg_name)

        if handler is not None:
            self.add_callback(parser, handler)



class _HandlersManager(dict):
    """Subclass of dict to store and retrieve CLI handlers"""

    def register_with_key(self, name, func):
        """Registers CLI handlers, allows to explicitly define, key"""
        self.__setitem__(name, func)

    def register_with_key_dec(self, name):
        """
        Decorator to register CLI handler with explicitly given key

        :param name: name of interface to configure - dot-separated path in
                    `cli_tree_schema`. For example for traceabiltiy prs_tests
                    key should be named as follows: `traceability.prs_tests`
                    Dot here represents nested parsers.
        :return: wrapper for function, saves function as handler and returns it
        """
        def wrapper(func):
            self.register_with_key(name, func)
            return func

        return wrapper

    def add_handler(self, func):
        self.__setitem__(func.__name__, func)

    def get_handler(self, name):
        try:
            return self.__getitem__(name)
        except KeyError:
            raise CLIHandlerLookupError(
                'Unknown handler `{}`. Known handler names: `{}`. '
                'Perhaps, it should be implemented and '
                'registered with `handlers_manager.register_with_key`, or '
                '`handlers_manager.register_with_key_dec`'
                ''.format(name, pformat(tuple(self.keys())))
            )


handlers_manager = _HandlersManager()


def add_parser(hook: argparse._SubParsersAction, name: str, help_dict: dict):
    """
    Shortcut for parser configuration

    :param hook: sub parser action hook to bind subparsers to
    :param name: sub parser name
    :param help_dict: mapping with help messages
        NOTE: mapping should contain message for key `name`
    """
    help_ = help_dict.get(name, None)
    if not help_:
        log.error('Help message for {} is not defined!'.format(name))
        help_ = 'No help here yet :C'
    hook.add_parser(name, help=help_)


if __name__ == '__main__':

    @handlers_manager.register_with_key_dec('foo.bar2')
    def foo_bar2(): return 2

    print(handlers_manager.items())