import os
import yaml
from glob import glob
import tarfile
import json

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

def writeJsonFile(file_name, contents):
    with open(file_name, 'w') as json_file:
        json.dump(contents, json_file)
