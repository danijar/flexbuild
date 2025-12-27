import io
import pathlib
import tarfile

from . import helpers
from . import include
from . import project


def build_sdist(sdist_directory, config_settings=None):
    proj = project.Project(root='.')
    outdir = pathlib.Path(sdist_directory).resolve()
    outfile = outdir / f'{proj.stem}.tar.gz'
    with tarfile.open(outfile, 'w:gz') as f:
        for path in proj.src.rglob('*.py'):
            if path.is_dir():
                continue
            relative = path.relative_to(proj.src)
            if include.should_exclude(relative):
                continue
            f.add(path, f'{proj.fullname}/{relative}')
        metadata = helpers.format_key_value(proj.metadata)
        pkginfo = tarfile.TarInfo(f'{proj.stem}/PKG-INFO')
        pkginfo.size = len(metadata)
        f.addfile(pkginfo, io.BytesIO(metadata))
    return outfile.name
