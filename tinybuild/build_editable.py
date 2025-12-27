from . import project
from . import wheel


def build_editable(
    wheel_directory,
    config_settings=None,
    metadata_directory=None,
):
    proj = project.Project('.')
    path = str((proj.src / '__init__.py').as_posix())
    finder = make_finder(proj.fullname, path)
    with wheel.Wheel(wheel_directory, proj) as whl:
        ident = proj.fullname.replace('.', '_')
        whl.add(f'_editable_impl_{ident}.pth', finder)
    return whl.name


def make_finder(fullname, path):
    finder = repr(EDITABLE_FINDER.format(fullname=fullname, path=path))
    finder = f'import sys; exec({finder})'
    finder = finder.encode('utf-8')
    return finder


EDITABLE_FINDER = """
import importlib.abc
import sys

class EditableFinder(importlib.abc.MetaPathFinder):

    def find_spec(self, fullname, path, target=None):
        if fullname == '{fullname}':
            import os, importlib.util
            locations = [os.path.dirname('{path}')]
            return importlib.util.spec_from_file_location(
                fullname, '{path}', submodule_search_locations=locations)
        if '{fullname}'.startswith(fullname + '.'):  # Namespace
            import importlib.machinery
            spec = importlib.machinery.ModuleSpec(fullname, None)
            spec.submodule_search_locations = []
            return spec
        return None

sys.meta_path.insert(0, EditableFinder())
"""
