
from mule.logger import logger


class IArchetype:

    def __init__(self, application_name):
        self.application_name = application_name

    def deps(self):
        logger.info(f"Not implemented for archetype {self.__class__.__name__}")

    def build(self):
        logger.info(f"Not implemented for archetype {self.__class__.__name__}")

    def publish(self, environment: str):
        logger.info(f"Not implemented for archetype {self.__class__.__name__}")

    def deploy(self, environment: str):
        logger.info(f"Not implemented for archetype {self.__class__.__name__}")

    def undeploy(self, environment: str):
        logger.info(f"Not implemented for archetype {self.__class__.__name__}")

    def smoke_test(self, environment: str):
        logger.info(f"Not implemented for archetype {self.__class__.__name__}")
