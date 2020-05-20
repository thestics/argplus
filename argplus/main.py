#!/usr/bin/env python3
# -*-encoding: utf-8-*-
# Author: Danil Kovalenko

"""
Main module for `argplus`. Defines entry-point function `build_parsers_tree`
which, reliably on default schema in `cli_tree_schema` builds CLI for cast
"""

# TODO: perhaps actual schema has to be an argument to main function, rather
#       then some value in package

# TODO: add help dicts at configuration as __help_dict__

import logging
import argparse
import typing as tp

from argplus.err import ArgplusException
from argplus.params_builder import handlers_manager, CLIArgsConfigurator


log = logging.getLogger(__name__)


class CastCLIBuildError(ArgplusException):
    pass


class SubParserHolder:
    """
    Holder for parser and subparsers action based on hook

    Supports two init scenarios:

    - default:
        sub_parsers_action -> new_parser + new_parser.sub_parsers_action

    - custom (for root parser):
        root_parser -> root_parser + root_parser.sub_parsers_action

    This class helps to manage parser (to add arguments) and subparsers
    (to create nested parsers) as one entity, so it is easier to understand
    traversal process
    """

    def __init__(self,
                 hook: argparse._SubParsersAction,
                 name: str,
                 sub_node: tp.Union[list, dict] = None,
                 help_dict=None):
        if help_dict is None:
            help_dict = {}

        # we want avoid addition of subparsers for final parsers (leafs),
        # so we could use positionals safely (otherwise `argparse` will confuse)
        # positional arguments with subparsers. Thus we peek into nested node
        # to determine whether it is a nested parser.
        subparsers_needed = isinstance(sub_node, dict)
        help_ = help_dict.get(name, '')
        self.parser = hook.add_parser(name, help=help_)

        if subparsers_needed:
            self.sub_parsers = self.parser.add_subparsers()
        else:
            self.sub_parsers = None

    @classmethod
    def from_root_parser(cls, parser):
        """Alternative constructor"""
        self = cls.__new__(cls)
        self.parser = parser
        self.sub_parsers = parser.add_subparsers()
        return self


class ParserTreeBuilder:

    def __init__(self,
                 tree_schema:      dict,
                 constants_dict:   dict,
                 cli_configurator: tp.Type[CLIArgsConfigurator] = CLIArgsConfigurator):
        self._tree_schema = tree_schema
        self._constants = constants_dict
        self._cli_configurator = cli_configurator(constants_dict['ARGS_HELP'])
        self._validate_tree()
        self._validate_constants()
        self._traverser = Traverser(self._cli_configurator)

    def _validate_tree(self):
        pass

    def _validate_constants(self):
        pass

    def _build_params(self, sub_parser, params: list, callback: tp.Callable):
        """
        For given argparse.Parser builds interface and binds callback

        :param sub_parser: argparse.Parser
        :param params: names of cast cli parameters (from `cli_configurator`
                        to be added to given interface)
        :param callback: handler function to be called upon trigger of given
                        interface
        """
        for p in params:
            self._cli_configurator.add_argument(sub_parser, p)
        self._cli_configurator.add_callback(sub_parser, callback)

    def build_parsers_tree(self):
        """
        Builds parsers with respect to what defined in `parsers_tree_definition`.

        """

        # extract tree root
        prog_name, root = self._tree_schema.copy().popitem()

        # traverse tree and bind handlers to interfaces
        parser = argparse.ArgumentParser(
            prog=prog_name, description=self._constants['PROG_HELP']
        )

        holder = SubParserHolder.from_root_parser(parser)
        self._traverser.traverse(holder, root, '')
        return parser


class Traverser:

    def __init__(self, cli_configurator: CLIArgsConfigurator):
        self._cli_configurator = cli_configurator

    def traverse(self,
                 holder: SubParserHolder,
                 node: tp.Union[list, dict],
                 cur_path: str):

        # nested parsers case
        if isinstance(node, dict):
            for sub_name, sub_node in node.items():

                # if current field is `__cur__` - add provided arguments to the
                # upper node and avoid recursive call
                if self._is_special_args(holder, sub_name, sub_node):
                    continue

                # create new sub parser and sub parsers action
                # (one needed to bind possible arguments, defined with `__cur__`
                # another for nested parsers)
                new_holder = SubParserHolder(holder.sub_parsers, sub_name,
                                             sub_node)

                # update path to node
                new_path = self._handle_path(cur_path, sub_name)

                # make recursive call
                self.traverse(new_holder, sub_node, new_path)

        # arguments definition case
        if isinstance(node, list):
            # fetch handler from registered handlers by `cur_path`
            handler = handlers_manager.get_handler(cur_path)
            # bind
            self._cli_configurator.add_arguments(holder.parser, node, handler)

    def _handle_path(self, cur_path: str, name: str) -> str:
        """If first iteration -- no leading dot needed"""
        if not cur_path:
            return name
        return '{}.{}'.format(cur_path, name)

    def _is_special_args(self,
                         holder: SubParserHolder,
                         node_name: str,
                         node: tp.Union[list, dict]
                         ) -> bool:
        """
        Check if defined node - __magic__ arguments for parent node.
        Define them as arguments rather then as subparsers.
        """
        if node_name == '__cur__' and type(node) is list:
            self._cli_configurator.add_arguments(holder.parser, node)
            return True
        return False


def build_parsers_tree(tree_schema:      dict,
                       constants_dict:   dict,
                       cli_configurator: tp.Type[CLIArgsConfigurator] = CLIArgsConfigurator
                       ) -> argparse.ArgumentParser:
    """
    Build CLI tree

    :param tree_schema:      definition of CLI tree. Defines which parsers will
                             have which arguments
    :param constants_dict:   definition of constants used when building a CLI
    :param cli_configurator: CLI parameters configurator
    :return:
    """
    p = ParserTreeBuilder(tree_schema, constants_dict, cli_configurator)
    return p.build_parsers_tree()
