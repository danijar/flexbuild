import pathlib

from flexbuild import project


ROOT = pathlib.Path(__file__).parent


class TestMetadata:

    def test_fields(self):
        project_folder = ROOT / 'example_metadata'
        metadata = project.Project(project_folder).metadata.decode('utf-8')
        metadata = metadata.split('\n\n', 1)[0]
        lines = [x.rstrip('\n') for x in metadata.splitlines()]
        assert 'Metadata-Version: 2.1' in lines
        assert 'Name: project' in lines
        assert 'Version: 0.1.0' in lines
        assert 'Summary: A test project with metadata' in lines
        assert 'Requires-Python: >=3.11' in lines
        assert 'License-Expression: MIT' in lines
        assert 'Keyword: test' in lines
        assert 'Keyword: example' in lines
        assert 'Classifier: Development Status :: 3 - Alpha' in lines
        assert 'Author-email: "Author" <author@example.com>' in lines
        assert 'Project-URL: Homepage, https://example.com' in lines

    def test_readme(self):
        project_folder = ROOT / 'example_metadata'
        metadata = project.Project(project_folder).metadata.decode('utf-8')
        lines = [x.rstrip('\n') for x in metadata.splitlines()]
        assert 'Description-Content-Type: text/markdown' in lines
        readme = metadata.split('\n\n', 1)[1]
        assert readme == '# Example Readme\n'
