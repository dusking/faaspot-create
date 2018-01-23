import logging
import inspect

logger = logging.getLogger(__name__)


class Command(object):
    def __init__(self, *args, **kwargs):
        self._action = args[0] if len(args) else ''
        self._argument = kwargs
        self._name = self.__class__.__name__.lower()
        self._actions = dict()
        self._register_instance_functions()

    @property
    def name(self):
        return self._name.title()

    @classmethod
    def register_class(cls):
        commands.register(cls.__name__.lower(), cls)

    def run_function(self):
        function = self._actions.get(self._action)
        if not function:
            raise Exception('Missing function `{0}`'.format(self._action))
        return function(**self._argument)

    def _register_instance_functions(self):
        all_methods = inspect.getmembers(self)
        for method_line in all_methods:
            method_name, method = method_line
            if inspect.isroutine(method):
                if method_name and not method_name.startswith('_'):
                    self._actions[method_name] = method


class Commands(object):
    def __init__(self):
        self._commands = {}

    def register(self, name, command):
        self._commands[name] = command

    def get(self, name):
        return self._commands.get(name)


commands = Commands()
