from __future__ import absolute_import

import pkgutil


def import_submodules(context, root_module, path):
    """
    Import all submodules and register them in the ``context`` namespace.

    >>> import_submodules(locals(), __name__, __path__)
    """
    for loader, name, _ in pkgutil.walk_packages(path, root_module + '.'):
        module = loader.find_module(name).load_module(name)
        for k, v in vars(module).iteritems():
            if not k.startswith('_'):
                context[k] = v
        context[name] = module
