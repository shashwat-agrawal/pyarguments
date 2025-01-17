import argparse
import copy
import re

class CallbackAction(argparse.Action):
    def __init__(self, **in_args):
        callbacks = {}
        if 'callbacks' in in_args:
            if not isinstance(in_args['callbacks'], dict):
                raise Exception('callbacks is not dictionary for option [' + ','.join(in_args['option_strings'])+ ']')
            for callback in in_args['callbacks']:
                if not callable(in_args['callbacks'][callback]):
                    raise Exception(f'callback [{callback}] is not callable for option [' + ','.join(in_args['option_strings'])+ ']')
            callbacks = copy.deepcopy(in_args['callbacks'])

            del in_args['callbacks']
        super().__init__(**in_args)
        self.callbacks = callbacks

    def check_callbacks(self, option_string, values):
        if len(self.callbacks.keys()) > 0:
            for callback in sorted(list(self.callbacks.keys())):
                self.callbacks[callback](option_string, values)

class Store(CallbackAction):
    def __call__(self, parser, namespace, values, option_string):
        if (isinstance(values, list) and len(values) == 0) or values is None:
            raise Exception(f'option: {option_string} provided without value' )
        self.check_callbacks(option_string, values)
        setattr(namespace, self.dest, values)
    
class StoreList(CallbackAction):
    def __init__(self, **in_args):
        if 'nargs' not in in_args:
            in_args['nargs'] = '*'
        super().__init__(**in_args)

    def __call__(self, parser, namespace, values, option_string):
        if (isinstance(values, list) and len(values) == 0) or values is None:
            raise Exception(f'option: {option_string} provided without value' )

        if not hasattr(namespace, self.dest) or not isinstance(getattr(namespace, self.dest), list):
            setattr(namespace, self.dest, [])

        value_array = getattr(namespace, self.dest)
        if isinstance(values, list):
            for value in values:
                self.check_callbacks(option_string, value)
            value_array.extend(values)
        else:
            self.check_callbacks(option_string, values)
            value_array.append(values)
        setattr(namespace, self.dest, value_array)

class StoreDict(CallbackAction):
    def __init__(self, **in_args):
        if 'nargs' not in in_args:
            in_args['nargs'] = '*'
        super().__init__(**in_args)

    def __call__(self, parser, namespace, values, option_string):
        if (isinstance(values, list) and len(values) == 0) or values is None:
            raise Exception(f'option: {option_string} provided without value' )

        if not hasattr(namespace, self.dest) or not isinstance(getattr(namespace, self.dest), dict):
            setattr(namespace, self.dest, {})
        def set_value(value):
            nonlocal self, namespace, option_string
            if not bool(re.search('=', value)):
                raise Exception(f'option [{option_string}] value [{value}] not in form key=[value]')

            self.check_callbacks(option_string, value)

            value_dict = copy.deepcopy(getattr(namespace, self.dest))
            value_array = re.split('=', value, maxsplit = 2)
            value_dict[value_array[0]] = ''
            if len(value_array) > 1:
                value_dict[value_array[0]] = value_array[1]

            setattr(namespace, self.dest, value_dict)
        if isinstance(values, list):
            for value in values:
                set_value(value)
        else:
            set_value(value)

class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, **in_args):
        self._destinations = []
        super().__init__(**in_args,
            formatter_class = argparse.RawTextHelpFormatter
        )

    def add_argument(self, *args, **kwargs):
        if 'dest' not in kwargs and kwargs['action'] != 'help':
            raise Exception('destination not found while adding argument with args: [' + ','.join(args) + ']')

        super().add_argument(*args, **kwargs)
        if 'dest' in kwargs:
            to_check = kwargs['dest']
            to_check_array = re.split('[.]', kwargs['dest'])
            if len(to_check_array) > 1:
                to_check = '.'.join(to_check_array[:-1])
            for dest in self._destinations:
                if dest == to_check:
                    raise Exception('Unable to handle conflicting destination values [' + kwargs['dest'] + f'] and [{to_check}]')

            self._destinations.append(kwargs['dest'])

    def parse_args(self, args):
        namespace = super().parse_args(args)
        struct = vars(namespace)
        ret_struct = {}
        for dest in sorted(list(struct.keys())):
            if struct[dest] is None:
                continue
            dest_array = re.split('[.]', dest)
            pointer = ret_struct
            for dest_array_item in dest_array[:-1]:
                if dest_array_item not in pointer:
                    pointer[dest_array_item] = {}
                pointer = pointer[dest_array_item]
            pointer[dest_array[-1]] = struct[dest]
        return ret_struct


def get_argument_parser(prog_name = None, description = ''):
    if prog_name is None:
        raise ValueError('program name is required for instantiating argument parser instance')
    return ArgumentParser(
        prog            = prog_name,
        description     = description,
    )

