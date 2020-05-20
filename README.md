# Micro-framework for building command-line interface

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codebeat badge](https://codebeat.co/badges/951460ba-e540-45b9-866f-044a9516f465)](https://codebeat.co/projects/github-com-thestics-argplus-master)

   As CLI build, using raw `argparse` is possible, for some programs it is 
heavily discouraged. Size of CLI code for it, written with `argparse` is huge and
hardly manageable.
   This package is intended to provide an abstraction above `argparse` to
configure big CLI-s easily.
   Package encapsulates entire CLI process creation and
expose some config-like code only, so that entire configuration can be short
and clear.

## Overall structure explanation:

#### Framework distinguishes next processes into separate independent components:

   - **Definition of overall CLI schema**:
       Python dict, which defines CLI in a following way:
           (example at `cli_tree_schema.py`)
           - Each entry represents either a parser or nested parsers
               (sub parsers).
           - Dicts are used for nested parsers
           - Lists are used to define arguments for given parser. Those parsers
               we call 'leafs' or 'final'. Each entry name has to
               be covered in `cli_configurator` (later)
           - Contains root parser with a fixed name (currently `cast`)
           - Supports special entries defined in a double-underscore case
               '\_\_cur__':
                   allows to add arguments for parser regardless of
                   whether any subparsers configured (e.g. we have next
                   structure:
                   ```cast [-v] [-h] {sub_pars1 [-v] [-t], {... some nested parsers}
                                   sub_pars2 [-t] [-k]}
                   ```
                   One parser (sub_pars1) has arguments which are related to
                   him and has subparsers, which expose final interface
                   )
               TODO: '\_\_help_dict__':
                   Reference to dict with help messages for given subparsers
       Path to each sub parser is defined in dotwise manner (for parser
           ```traceability: {
               ...
               'hdd_cdd': ['tb_config', 'output', 'site_filters'],
               ...
           }
           ```
       hdd_cdd parser is defined by key traceability.hdd_cdd
       )
   - **Definition of CLI arguments configurator**:
       As arguments tend to be not unique (one may appear many times in
       different places), CLI configurator is defined:
           - Subclass of `params_builder.CLIArgsConfigurator`, for each
               desired argument with name <arg_name> has to implement method
               based on its name in the following manner:
               `<arg_name>_adder(self, parser)` and implement addition of any
               wished parameters.
       To make implementation more clear one is highly recommended to
       implement a separate dict with help messages for each argument required.
   - **Definition of handlers manager**:
       (params_builder.handlers_manager)
       Object to store callable handlers for interfaces.
       Consider parser defined in cli_schema with path 'path.to.parser'
       To add handler to this parser one implements function which takes one
       argument `args` and registers it by key 'path.to.parser' with api
       provided by handler manager, for example:
       
       ```from argplus.params_builder import handlers_manager as hm
       @hm.register_with_key_dec('path.to.parser')
       def handler(args):
           print(args.x + args.y)
       # or
       def handler(args):
           print(args.x + args.y)
       hm.register_with_key('path.to.parser', handler)
      ```
       NOTE: all required handlers has to be registered before cli build start
       Then `argplus` at CLI creation will traverse defined cli_schema,
       and each time in encounters final parser (leaf) it will bind registered
       handler to it. If `argplus` fails to lookup desired handler,
       process fails with fatal error.
TODO: help messages for subparsers
      correct display of usage
