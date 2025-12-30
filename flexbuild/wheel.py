import base64
import hashlib
import pathlib
import zipfile

from . import helpers


class Wheel:
    """Write a Python wheel by adding files to it."""

    def __init__(self, outdir, project):
        outdir = pathlib.Path(outdir).resolve()
        self.stem = project.stem
        self.meta = project.metadata
        self.path = outdir / f'{self.stem}-py3-none-any.whl'
        self.records = []
        self.f = None

    @property
    def name(self):
        return self.path.name

    def __enter__(self):
        assert not self.f
        self.f = zipfile.ZipFile(self.path, 'w')
        self.f.__enter__()
        return self

    def __exit__(self, typ, val, tb):
        self._finish()
        self.records = []
        self.f.__exit__(typ, val, tb)
        self.f = None

    def add(self, name, content):
        assert isinstance(content, bytes), (name, content)
        name = str(name)
        digest = self._get_digest(content)
        self.records.append(f'{name},{digest},{len(content)}\n')
        self.f.writestr(name, content)

    def _finish(self):
        distinfo = f'{self.stem}.dist-info'
        self.add(f'{distinfo}/METADATA', self.meta)
        wheelinfo = [
            ('Wheel-Version', '1.0'),
            ('Generator', 'flexbuild 0.1.0'),
            ('Root-Is-Purelib', 'true'),
            ('Tag', 'py3-none-any'),
        ]
        self.add(f'{distinfo}/WHEEL', helpers.format_key_value(wheelinfo))
        self.records.append('RECORD,,\n')
        self.f.writestr(f'{distinfo}/RECORD', ''.join(self.records))

    def _get_digest(self, data):
        digest = hashlib.sha256(data).digest()
        digest = base64.urlsafe_b64encode(digest)
        digest = 'sha256=' + digest.decode('latin1').rstrip('=')
        return digest
