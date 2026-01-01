[![PyPI](https://img.shields.io/pypi/v/flexbuild.svg)](https://pypi.python.org/pypi/flexbuild/#history)

# 🧱 Flexbuild

Simple Python build backend for large codebases.

Add to your `pyproject.toml`:

```toml
[build-system]
requires = ["flexbuild"]
build-backend = "flexbuild"
```

## Features

- 🤸 **Flexible source layouts:** Place code directly alongside
  `pyproject.toml` or in a subfolder like `src/module`.
- 🏷️ **Virtual namespaces:** Define namespace modules like
  `org.department.package` without nested folders.
- 🏗️ **Monorepo support:** Handle hierarchies of hundreds of packages
  with minimal boilerplate.
- 📝 **Rich metadata:** Entry points, optional dependencies, author and
  maintainer list, license, and more.
- 🤝 **Ecosystem integration:** Integrates seamlessly with packaging tools like
  `uv` and `pip`.
- 🐣 **Hackable:** Under 500 lines of easy-to-read Python code with extensive
  test coverage.

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
        pypackage.toml  # project.name = "org.department1.package2"
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

Consider using this layout together with [uv path dependencies][path]. Unlike
[uv workspace dependencies][workspace], it allows teams to update their version
locks independently, so they can move faster and more predictably.

[path]: https://docs.astral.sh/uv/concepts/projects/dependencies/#path
[workspace]: https://docs.astral.sh/uv/concepts/projects/workspaces/

## Background

Expand the sections below to to learn details of how Flexbuild solves problems
of other Python build backends.

<details>

<summary><h3>Flexible source layouts</h3></summary>

Many Python build backends require a separate module folder inside the package:

```
package
  pyproject.toml
  src
    module
      __init__.py
```

Flexbuild looks for the module code at `build-system.module-folder = "."` from
`pyproject.toml`, which defaults to the package folder but can also be set to a
nested folder like `src/module`.

</details>

<details>

<summary><h3>Virtual namespaces</h3></summary>

To define namespace packages that can be imported as `import
org.department1.package1`, many Python build backends require creating nested
folders inside the package:

```
package
  pyproject.toml  # project.name = "org-department1-package1"
  src
    org
      department1
        package1
          __init__.py
```

Flexbuild allows specifying namespace packages without the nested folders,
simply by setting `project.name = "org.department1.package1"` in the
`pyproject.toml`. This allows simpler folder structures, for example:

```
package
  pyproject.toml  # project.name = "org.department1.package1"
  __init__.py
```

</details>

<details>

<summary><h3>Monorepos</h3></summary>

To manage a repository with many namespace packages, most Python build backends
would require duplicating the same nested folder structure inside of each
package:

```
repo
  org-department1-package1
    pyproject.toml
    README.md
    src
      org
        department1
          package1
            __init__.py
            code.py
  org-department1-package2
    pyproject.toml
    README.md
    src
      org
        department1
          package2
            __init__.py
            code.py
  org-department1-package2
    pyproject.toml
    README.md
    src
      org
        department1
          package3
            __init__.py
            code.py
  org-department2-package1
    ...
  org-department2-package2
    ...
  org-department2-package3
    ...
```

Through virtual namespaces, Flexbuild allows using a directory structure for
namespace packages that can still import each other as `import
org.department1.package1`:

```
repo
  org-department1-package1
    pyproject.toml
    README.md
    __init__.py
    code.py
  org-department1-package2
    pyproject.toml
    README.md
    __init__.py
    code.py
  org-department1-package2
    pyproject.toml
    README.md
    __init__.py
    code.py
  org-department2-package1
    ...
  org-department2-package2
    ...
  org-department2-package3
    ...
```

Moreover, it allows placing the packages as leaves of a folder structure. Note
that the `pyproject.toml` files are inside the leaf folders now. This enables
organizing packages in a shared folder structure (instead of duplicating the
folder structure inside of each package):

```
repo
  org
    department1
      package1
        pyproject.toml
        README.md
        __init__.py
        code.py
      package2
        pyproject.toml
        README.md
        __init__.py
        code.py
      package3
        pyproject.toml
        README.md
        __init__.py
        code.py
    ...
```

</details>

## Questions

Please open a separate [GitHub issue](https://github.com/danijar/flexbuild/issues)
for each question.
