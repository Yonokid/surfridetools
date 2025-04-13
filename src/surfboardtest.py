import json
import sys

import save_json
import surfridetools

input_file = sys.argv[1]

chunks = surfridetools.read_vtbf(input_file)
json_dict = surfridetools.unpack_surfboard(chunks)
save_json.save_json(json_dict, input_file[:-4])

with open(f'{input_file[:-8]}.json', 'r') as f:
    json_file = json.load(f)
    surfridetools.repack_surfboard(json_file, f"{input_file}2")
