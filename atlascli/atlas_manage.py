#!/usr/bin/env python
import sys


def main():
    """
    Main script that runs the specified module or gives existent modules.
    """

    try:
        module = sys.argv.pop(1)
        m = __import__('commands.' + module, globals(), locals(), [module], -1)
        class_object = m.Command(sys.argv[1:])
    except (IndexError, ImportError) as e:
        if e.__class__.__name__ == 'ImportError':
            print "No such command."
        m = __import__('commands', globals(), locals(), [], -1)
        class_object = m.AtlasCommand(sys.argv[1:])

    if not class_object.parser_options.help_text and class_object.safe_options:
        class_object.run()


if __name__ == '__main__':
    sys.exit(main())
