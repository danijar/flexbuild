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
            print(f"DEBUG: Adding to wheel: {f'{proj.scope}/{relative}'}")
            whl.add(f'{proj.scope}/{relative}', path.read_bytes())
    return whl.name
