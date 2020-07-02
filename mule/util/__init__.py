import time

class JobContext:

    job_context = {}

    def __init__(self, agent_configs):
        self.job_context['agents'] = agent_configs

    def add_field(self, index, value):
        keys = index.split('.')
        current = self.job_context
        for key_index, key in enumerate(keys):
            if key_index == len(keys) - 1:
                current[key] = value
            if not key in current.keys():
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
        if not key in dictionary.keys():
            return None
        if key_index == len(keys) - 1:
            return dictionary[key]
        dictionary = dictionary[key]

def update_dict(current, new):
    levels = [(current, new)]
    while len(levels) > 0:
        level = levels.pop(0)
        for level_key in level[1].keys():
            if not level_key in level[0].keys():
                level[0][level_key] = level[1][level_key]
            elif not type(level[1][level_key]) == dict:
                level[0][level_key] = level[1][level_key]
            elif not type(level[0][level_key]) == dict:
                level[0][level_key] = level[1][level_key]
            else:
                levels.append((level[0][level_key], level[1][level_key]))
    return current
