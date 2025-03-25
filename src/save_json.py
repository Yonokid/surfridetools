import json
import re
from _ctypes import PyObj_FromPtr


class NoIndent(object):
    """ Value wrapper. """
    def __init__(self, value):
        if not isinstance(value, (list, tuple)):
            raise TypeError('Only lists and tuples can be wrapped')
        self.value = value
    def __repr__(self):
        return str(self.value)

class MyEncoder(json.JSONEncoder):
    FORMAT_SPEC = '@@{}@@'  # Unique string pattern of NoIndent object ids.
    regex = re.compile(FORMAT_SPEC.format(r'(\d+)'))  # compile(r'@@(\d+)@@')

    def __init__(self, **kwargs):
        # Keyword arguments to ignore when encoding NoIndent wrapped values.
        ignore = {'cls', 'indent'}

        # Save copy of any keyword argument values needed for use here.
        self._kwargs = {k: v for k, v in kwargs.items() if k not in ignore}
        super(MyEncoder, self).__init__(**kwargs)

    def default(self, o):
        return (self.FORMAT_SPEC.format(id(o)) if isinstance(o, NoIndent)
                    else super(MyEncoder, self).default(o))

    def iterencode(self, o, _one_shot=False):
        format_spec = self.FORMAT_SPEC  # Local var to expedite access.

        # Replace any marked-up NoIndent wrapped values in the JSON repr
        # with the json.dumps() of the corresponding wrapped Python object.
        for encoded in super(MyEncoder, self).iterencode(o, _one_shot=_one_shot):
            match = self.regex.search(encoded)
            if match:
                id = int(match.group(1))
                no_indent = PyObj_FromPtr(id)
                json_repr = json.dumps(no_indent.value, **self._kwargs)
                # Replace the matched id string with json formatted representation
                # of the corresponding Python object.
                encoded = encoded.replace(
                            '"{}"'.format(format_spec.format(id)), json_repr)

            yield encoded

def save_json(json_dict: dict, input_file: str) -> None:
    try:
        with open(f"{input_file[:-4]}.json", "w") as f:
            json.dump(json_dict, f, indent=2, cls=MyEncoder)
        print(f"JSON saved to {input_file[:-4]}.json")
    except Exception as e:
        print(f"Error saving JSON: {e}")
