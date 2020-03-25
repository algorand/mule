class JobContext:

    job_context = {}

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
