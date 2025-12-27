from . import include
from . import project
from . import wheel


def build_wheel(
    wheel_directory,
    config_settings=None,
    metadata_directory=None,
):
    proj = project.Project(root='.')
    with wheel.Wheel(wheel_directory, proj) as whl:
        for path in proj.root.rglob('*.py'):
            relative = path.relative_to(proj.root)
            if include.should_exclude(relative):
                continue
            whl.add(f'{proj.scope}/{relative}', path.read_bytes())
    return whl.name
