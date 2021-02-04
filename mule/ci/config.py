import os

BIN_DIR = os.getenv('BIN_DIR', '/usr/local/bin/')
EKS_CLUSTER_NAME = os.getenv('EKS_CLUSTER_NAME', None)
AWS_REGION = os.getenv('AWS_REGION', 'us-east-2')
MULE_FILE_PATH = os.getenv('MULE_FILE_PATH', '.muleci.yml')
