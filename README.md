[![PyPI](https://img.shields.io/pypi/v/flexbuild.svg)](https://pypi.python.org/pypi/flexbuild/#history)

# 🧱 Flexbuild

Flexible Python build backend for large code bases.

Add to your `pyproject.toml`:

```toml
[build-system]
requires = ["flexbuild"]
build-backend = "flexbuild"
```

## Features

- 🐣 **Simple and hackable:** Flexbuild is implemented in under 500 lines of
  easy-to-read Python code.
- 🤸 **Flexible source layouts:** Can place code directly alongside
  `pyproject.toml` or in a subfolder like `src/module`.
- 🏷️ **Virtual namespaces:** Can define namespace modules like
  `org.department.package` without requiring nested folders inside the package
  folder.
- 🏗️ **Monorepo support:** Easily supports large repositories with hundreds of
  packages organized by namespaces.
- 📝 **Rich metadata:** Entry points, optional dependencies, author and
  maintainer list, license, and more.
- 🤝 **Ecosystem integration:** Integrates easily with packaging tools like
  `uv` and `pip`.

## Options

```toml
[build-system]
requires = ["flexbuild"]
build-backend = "flexbuild"
module-folder = "."
include = [
    '*.py',
    'pyproject.toml',
    'README.md',
    'README.rst',
]
exclude = [
    'dist',
    'build',
    '__pycache__',
    '.*',
    '*/.*',
    '*.pyc',
]
```

## Monorepos

Flexbuild supports large repositories that contain hundreds of packages with
minimal boilerplate. For example, packages can be organized into a folder
hierarchy:

```
repo
  org
    department1
      package1
        pypackage.toml  # name = "org.department1.package2"
        __init__.py     # import org.department1.package1
        README.md
        code.py
      package2
        pypackage.toml
        __init__.py
        ...
      package3
    department2
      package1
      package2
      package3
```

Optionally, create a file `repo/pyroot.toml`. This enables checks that package
namespaces match the folder hierarchy. It also allows specifying
`[build-system]` defaults that nested `pyproject.toml` files inherit.

The above layout requires `module-folder = "."` to colocate the project and
module code in the same folder, which is the default. Moreover, it requires
package names containing dots in `pyproject.toml`. Most Python build backends
would require duplicating the nested folder structure **inside** of each
package, which is unwieldy.

Consider using the above layout together with [uv path dependencies][path].

[path]: https://docs.astral.sh/uv/concepts/projects/dependencies/#path

## Questions

Please open a separate [GitHub issue](https://github.com/danijar/flexbuild/issues)
for each question.
