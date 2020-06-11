import os
import yaml
from glob import glob
import tarfile
import json
import shutil

def deleteFile(path):
    os.remove(path)

def readYamlFile(path):
    with open(path) as configs:
        return yaml.load(configs, Loader=yaml.FullLoader)

def readFileAsString(path):
    with open(path, 'r') as template:
        return template.read()

def getFilesInFolder(path):
    files = []
    for (filepath, _, filenames) in os.walk(path):
        for filename in filenames:
            files.append(f"{filepath}/{filename}")
    return files

def compressFiles(file_name, globspecs):
    files = []
    for globspec in globspecs:
        files.extend(glob(globspec, recursive=True))
    with tarfile.open(file_name, "w:gz") as tar:
        for file in files:
            if os.path.isfile(file):
                tar.add(file)

def decompressTarfile(file_name, target_directory = '.'):
    with tarfile.open(file_name, "r:gz") as tar:
        tar.extractall(target_directory)

def read_json_file(file_name):
    with open(file_name, 'r') as json_file:
        return json.load(json_file)

def write_json_file(file_name, contents):
    with open(file_name, 'w') as json_file:
        json.dump(contents, json_file)

def ensure_file(file_name, contents=None):
    if not os.path.exists(file_name):
        with open(file_name, 'w') as file:
            if contents is None:
                pass
            file.write(contents)

def ensure_folder(folder_name):
    folder_name = folder_name.replace('~', os.path.expanduser('~'))
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

def mv_folder_contents(source, dest, ignore=False):
    files = os.listdir(source)
    for file in files:
        try:
            shutil.move(os.path.join(source, file), os.path.join(dest, file))
        except:
            if not ignore:
                raise

def copy_file(source, dest):
    shutil.copy(source, dest)
