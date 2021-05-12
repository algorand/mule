from pydoc import locate

from mule.ci.archetype.node import Npm
from mule.ci.archetype.docker import Docker

archetypes = {
    'npm': Npm,
    'docker': Docker,
}


def get_archetypes():
    return archetypes.keys()


def get_archetype(archetype, application_name):
    archetype_clazz = archetypes[archetype]
    return archetype_clazz(application_name)


def get_attr(archetype, method):
    archetype_clazz = locate(archetypes[archetype])
    return getattr(archetype_clazz, method)
