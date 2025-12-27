from . import include
from . import project
from . import wheel


def build_wheel(
    wheel_directory,
    config_settings=None,
    metadata_directory=None,
):
    proj = project.Project('.')
    with wheel.Wheel(wheel_directory, proj) as whl:
        for path in proj.src.rglob('*.py'):
            relative = path.relative_to(proj.src)
            if include.should_exclude(relative):
                continue
            whl.add(f'{proj.fullname}/{relative}', path.read_bytes())
    return whl.name
