import copy
import json


class JobContext:
    def __init__(self, job_config):
        self.job_context = copy.deepcopy(job_config)

    def add_field(self, index, value):
        keys = index.split('.')
        current = self.job_context
        for key_index, key in enumerate(keys):
            if key_index == len(keys) - 1:
                current[key] = value
            if key not in current.keys():
                current[key] = {}
            current = current[key]

    def get_fields(self):
        return(self.job_context)

    def get_field(self, index):
        keys = index.split('.')
        return get_dict_value(self.job_context, keys)


# Gets value for dict key provided as list ordered list of keys
def get_dict_value(dictionary, keys):
    for key_index, key in enumerate(keys):
        if key not in dictionary.keys():
            return None
        if key_index == len(keys) - 1:
            return dictionary[key]
        dictionary = dictionary[key]


def prettify_json(raw_json):
    return json.dumps(raw_json, indent=4, sort_keys=False)


def update_dict(current, new, overwrite_lists=True):
    levels = [(current, new)]
    while len(levels) > 0:
        level = levels.pop(0)
        for level_key in level[1].keys():
            if level_key not in level[0].keys():
                level[0][level_key] = level[1][level_key]
            elif not type(level[0][level_key]) == dict or not type(level[1][level_key]) == dict:
                _update_level(level, level_key, overwrite_lists=overwrite_lists)
            else:
                levels.append((level[0][level_key], level[1][level_key]))
    return current


def _update_level(level, level_key, overwrite_lists=True):
    if not overwrite_lists and type(level[0][level_key]) == list and type(level[1][level_key]) == list:
        for item in level[1][level_key]:
            if item not in level[0][level_key]:
                level[0][level_key].append(item)
    else:
        level[0][level_key] = level[1][level_key]
