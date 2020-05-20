#!/usr/bin/env python3
# -*-encoding: utf-8-*-
# Author: Danil Kovalenko


import argplus


cli_def = {
    'example': {
        'reduce_to': {
            '__cur__': ['offset', 'scale'],
            'sum': ['numeric_args'],
            'max': ['numeric_args'],
            'mean': ['numeric_args']
        }
    }
}

constants = {
    'PROG_HELP': 'An example program for `argplus`. Implements some math ops',

    'ARGS_HELP': {
        'left': 'Left operand',
        'right': 'Right operand',
        'operand': 'Single operand',
        'offset': 'Numerical offset for output',
        'scale': 'Numerical multiplier for output',
        'numeric_args': 'Any number of numerical arguments'
    },

    'PARSERS_HELP': {
        'prod': 'Product of two numbers',
        'neg': 'negative number',
        'reduce_to': {
            'sum': 'Reduce numbers to its sum',
            'max': 'Reduce numbers to its max',
            'mean': 'Reduce number to its mean',
        }
    }
}


class CalcArgsConfigurator(argplus.CLIArgsConfigurator):

    def left_adder(self):
        return self.to_args_dict('left', type=float)

    def right_adder(self):
        return self.to_args_dict('right', type=float)

    def operand_adder(self):
        return self.to_args_dict('operand', type=float)

    def offset_adder(self):
        return self.to_args_dict('-o', '--offset', type=float, default=0)

    def scale_adder(self):
        return self.to_args_dict('-s', '--scale', type=float, default=1)

    def numeric_args_adder(self):
        return self.to_args_dict('numeric_args', type=float, nargs='+',
                                 metavar='N')


@argplus.handlers_manager.register_with_key_dec('prod')
def prod_handler(args):
    pass


@argplus.handlers_manager.register_with_key_dec('neg')
def neg_handler(args):
    pass


@argplus.handlers_manager.register_with_key_dec('reduce_to.sum')
def reduce_sum(args):
    print((sum(args.numeric_args) + args.offset) * args.scale)


@argplus.handlers_manager.register_with_key_dec('reduce_to.max')
def reduce_max(args):
    pass


@argplus.handlers_manager.register_with_key_dec('reduce_to.mean')
def reduce_mean(args):
    pass


parser = argplus.build_parsers_tree(cli_def, constants, CalcArgsConfigurator)
argplus.parse(parser)
