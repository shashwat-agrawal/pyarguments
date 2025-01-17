import arguments
import unittest

class TestCase(unittest.TestCase):
    def test_all(self):
        self.assertTrue(callable(arguments.get_argument_parser))

        arg_parser = arguments.get_argument_parser(prog_name='sample')
        self.assertTrue(callable(arg_parser.parse_args))

        with self.assertRaisesRegex(Exception, 'callbacks is not dictionary for option .--scalar.'):
            arg_parser.add_argument( '--scalar',
                action      = arguments.Store,
                dest        = 'scalar',
                help        = 'scalar help',
                callbacks   = '',
            )

        scalar_callback_called = False
        def scalar_check(option_strings, values):
            nonlocal scalar_callback_called
            scalar_callback_called = True

        arg_parser.add_argument( '--scalar',
            action      = arguments.Store,
            dest        = 'scalar.dest',
            help        = 'scalar help',
            callbacks   = {
                'scalar_check': scalar_check
            },
        )

        args = arg_parser.parse_args(['--scalar', 'foo'])
        self.assertTrue(scalar_callback_called)
        self.assertEqual(args, {"scalar": {"dest": "foo"}})

        with self.assertRaisesRegex(Exception, 'destination not found while adding argument with args: .--scalar.'):
            arg_parser = arguments.get_argument_parser(prog_name='sample')
            arg_parser.add_argument( '--scalar',
                action      = arguments.Store,
                help        = 'scalar help',
            )

        with self.assertRaisesRegex(Exception, 'Unable to handle conflicting destination values .scalar.nest. and .scalar.'):
            arg_parser = arguments.get_argument_parser(prog_name='sample')
            arg_parser.add_argument( '--scalar',
                action      = arguments.Store,
                dest        = 'scalar',
                help        = 'scalar help',
            )
            arg_parser.add_argument( '--scalar_nest',
                action      = arguments.Store,
                dest        = 'scalar.nest',
                help        = 'scalar nest help',
            )

        arg_parser = arguments.get_argument_parser(prog_name='sample')
        arg_parser.add_argument( '--list',
            action      = arguments.StoreList,
            dest        = 'list',
            help        = 'list help',
        )
        self.assertEqual(arg_parser.parse_args([]), {})
        with self.assertRaisesRegex(Exception, 'option: --list provided without value'):
            arg_parser.parse_args(['--list'])

        self.assertEqual(arg_parser.parse_args(['--list', 'a']), {'list': ['a']})
        self.assertEqual(arg_parser.parse_args(['--list', 'a', '--list', 'b']), {'list': ['a', 'b']})
        self.assertEqual(arg_parser.parse_args(['--list', 'a', 'b']), {'list': ['a', 'b']})

        list_callback_called = False
        def list_check(option_strings, values):
            nonlocal list_callback_called
            list_callback_called = True

        arg_parser = arguments.get_argument_parser(prog_name='sample')
        arg_parser.add_argument( '--list',
            action      = arguments.StoreList,
            dest        = 'list',
            help        = 'list help',
            callbacks   = {
                'list check': list_check
            }
        )
        self.assertEqual(arg_parser.parse_args(['--list', 'a']), {'list': ['a']})
        self.assertTrue(list_callback_called)

        arg_parser = arguments.get_argument_parser(prog_name='sample')
        arg_parser.add_argument( '--list',
            action      = arguments.StoreList,
            dest        = 'list.nest',
            help        = 'list help',
            default     = ['a'],
        )
        self.assertEqual(arg_parser.parse_args([]), {'list': { 'nest': ['a']}})

        arg_parser = arguments.get_argument_parser(prog_name='sample')
        arg_parser.add_argument( '--dict',
            action      = arguments.StoreDict,
            dest        = 'dict',
            help        = 'dict help',
        )
        self.assertEqual(arg_parser.parse_args([]), {})
        with self.assertRaisesRegex(Exception, 'option .--dict. value .a. not in form key=.value.'):
            arg_parser.parse_args(['--dict', 'a'])

        self.assertEqual(arg_parser.parse_args(['--dict', 'a=']), {'dict': {'a': ''}})

        dict_callback_called = False
        def dict_check(option_strings, values):
            nonlocal dict_callback_called
            dict_callback_called = True

        arg_parser = arguments.get_argument_parser(prog_name='sample')
        arg_parser.add_argument( '--dict',
            action      = arguments.StoreDict,
            dest        = 'dict',
            help        = 'dict help',
            callbacks   = {
                'dict check': dict_check
            }
        )
        self.assertEqual(arg_parser.parse_args(['--dict', 'a=']), {'dict': {'a': ''}})
        self.assertTrue(dict_callback_called)

        with self.assertRaises(SystemExit):
            arg_parser = arguments.get_argument_parser(prog_name='sample')
            arg_parser.add_argument( '--dict',
                action      = arguments.StoreDict,
                dest        = 'dict',
                help        = 'dict help',
                required    = True
            )
            arg_parser.parse_args([])

        arg_parser = arguments.get_argument_parser(prog_name='sample')
        arg_parser.add_argument( '--dict_one',
            action      = arguments.StoreDict,
            dest        = 'dict.one',
            help        = 'dict one help',
        )
        arg_parser.add_argument( '--dict_two',
            action      = arguments.StoreDict,
            dest        = 'dict.two',
            help        = 'dict two help',
        )
        self.assertEqual(arg_parser.parse_args(['--dict_one', '1=1', '--dict_two', '2=2']), {'dict': {'one': {'1': '1'}, 'two': {'2': '2'}}})

        arg_parser = arguments.get_argument_parser(prog_name='sample')
        arg_parser.add_argument( '--dict',
            action      = arguments.StoreDict,
            dest        = 'dict',
            help        = 'dict help',
        )
        arg_parser.parse_args(['--dict', 'a=', 'b='])

if __name__ == '__main__':
    unittest.main()