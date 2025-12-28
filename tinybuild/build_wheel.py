from . import project
from . import select
from . import wheel


def build_wheel(
    wheel_directory,
    config_settings=None,
    metadata_directory=None,
):
    proj = project.Project('.')
    selector = select.Selector()
    with wheel.Wheel(wheel_directory, proj) as whl:
        for path in proj.module_folder.rglob('*.py'):
            relative = path.relative_to(proj.module_folder)
            if not selector.should_include(relative):
                continue
            whl.add(f'{proj.scope}/{relative}', path.read_bytes())
    return whl.name
