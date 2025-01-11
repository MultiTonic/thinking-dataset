# @file thinking_dataset/dataset/operations/__init__.py
# @description Initialization file to import all operation classes dynamically.
# @version 1.0.9
# @license MIT

import os
import importlib


def _get_operations_dir():
    return os.path.dirname(__file__)


def _get_operations_files(operations_dir):
    return [
        f for f in os.listdir(operations_dir)
        if f.endswith('.py') and not f.startswith('__')
    ]


def _get_module_name(operation_file, operations_dir):
    base_package = __name__.rsplit('.', 1)[0]
    module_name = f'{base_package}.operations.{operation_file[:-3]}'
    return module_name


def _import_operation_module(module_name):
    return importlib.import_module(module_name)


def _get_class_name(operation_file):
    return ''.join(
        [part.capitalize() for part in operation_file[:-3].split('_')])


operations_path = _get_operations_dir()
operations_files = _get_operations_files(operations_path)

__all__ = []

for operation_file in operations_files:
    module_name = _get_module_name(operation_file, operations_path)
    module = _import_operation_module(module_name)
    class_name = _get_class_name(operation_file)

    if hasattr(module, class_name):
        globals()[class_name] = getattr(module, class_name)
        __all__.append(class_name)
