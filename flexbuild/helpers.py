import fnmatch
import os
import pathlib
import re
import shlex
import subprocess


def format_key_value(data):
    content = ''.join(f'{k}: {v}\n' for k, v in data)
    content = content.encode('utf-8')
    return content


def merge_dicts(first, second):
    if not isinstance(first, dict):
        return first
    if not isinstance(second, dict):
        return merge_dicts(first, {})
    merged = {}
    keys = sorted(set(first.keys()) | set(second.keys()))
    for key in keys:
        if key in first and key in second:
            merged[key] = merge_dicts(first[key], second[key])
        elif key in first:
            merged[key] = merge_dicts(first[key], {})
        else:
            merged[key] = merge_dicts(second[key], {})
    return merged


def find_files(folder, includes=['*'], excludes=['.*', '*/.*']):
    include = re.compile('|'.join(fnmatch.translate(x) for x in includes))
    exclude = re.compile('|'.join(fnmatch.translate(x) for x in excludes))
    filenames = scan_folder(folder, include, exclude)
    filenames = [pathlib.Path(x) for x in filenames]
    filenames = sorted(list(filenames))
    return filenames


def scan_folder(folder, include, exclude):
    filenames = []
    with os.scandir(folder) as entries:
        for entry in entries:
            if entry.is_file() and not include.match(entry.name):
                continue
            if exclude.match(entry.name):
                continue
            if entry.is_dir():
                filenames += scan_folder(entry.path, include, exclude)
            else:
                filenames.append(entry.path)
    return filenames


def run_command(command, cwd='.', env=None):
    args = shlex.split(command)
    result = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=cwd,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f'Command failed with return code {result.returncode}.\n'
            f'--- COMMAND ---\n{command}\n'
            f'--- OUTPUT ---\n{result.stdout}'
        )
    return result.stdout
