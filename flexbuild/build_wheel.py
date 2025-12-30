from . import project
from . import helpers
from . import wheel


def build_wheel(
    wheel_directory,
    config_settings=None,
    metadata_directory=None,
):
    proj = project.Project('.')
    filenames = helpers.find_files(
        proj.module_folder, proj.include, proj.exclude
    )
    with wheel.Wheel(wheel_directory, proj) as whl:
        for path in filenames:
            relative = path.relative_to(proj.module_folder)
            whl.add(f'{proj.scope}/{relative}', path.read_bytes())
    return whl.name
