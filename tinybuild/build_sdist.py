import io
import pathlib
import tarfile

from . import project
from . import helpers


def build_sdist(sdist_directory, config_settings=None):
    proj = project.Project('.')
    outdir = pathlib.Path(sdist_directory).resolve()
    outfile = outdir / f'{proj.stem}.tar.gz'
    filenames = helpers.find_files(
        proj.project_folder, proj.include, proj.exclude
    )
    with tarfile.open(outfile, 'w:gz') as f:
        for path in filenames:
            relative = path.relative_to(proj.project_folder)
            f.add(path, f'{proj.stem}/{relative}')
        pkginfo = tarfile.TarInfo(f'{proj.stem}/PKG-INFO')
        pkginfo.size = len(proj.metadata)
        f.addfile(pkginfo, io.BytesIO(proj.metadata))
    return outfile.name
