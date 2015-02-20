from __future__ import absolute_import, unicode_literals

import pkgutil


def import_submodules(context, root_module, path):
    """
    Import all submodules and register them in the ``context`` namespace.

    >>> import_submodules(locals(), __name__, __path__)
    """
    for loader, name, _ in pkgutil.walk_packages(path, root_module + '.'):
        module = loader.find_module(name).load_module(name)
        pkg_names = getattr(module, '__all__', None)
        for k, v in vars(module).iteritems():
            if not k.startswith('_') and (pkg_names is None or k in pkg_names):
                context[k] = v
        context[name] = module
