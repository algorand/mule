import os
import yaml

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
