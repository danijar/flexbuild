import io
import pathlib
import tarfile

from . import project
from . import select


def build_sdist(sdist_directory, config_settings=None):
    proj = project.Project('.')
    outdir = pathlib.Path(sdist_directory).resolve()
    outfile = outdir / f'{proj.stem}.tar.gz'
    selector = select.Selector()
    with tarfile.open(outfile, 'w:gz') as f:
        for path in proj.project_folder.rglob('*'):
            if path.is_dir():
                continue
            relative = path.relative_to(proj.project_folder)
            if not selector.should_include(relative):
                continue
            f.add(path, f'{proj.stem}/{relative}')
        pkginfo = tarfile.TarInfo(f'{proj.stem}/PKG-INFO')
        pkginfo.size = len(proj.metadata)
        f.addfile(pkginfo, io.BytesIO(proj.metadata))
    return outfile.name
