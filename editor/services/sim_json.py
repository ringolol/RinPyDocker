import json

try:
    # works for django
    from .simulator import BLOCK_TYPES, Block
except ImportError:
    # works outside of django
    from simulator import BLOCK_TYPES, Block

blocks_json = {}
for block in BLOCK_TYPES:
    d = BLOCK_TYPES[block]._asdict()
    blocks_json[block] = {key:d[key] for key in d if key not in ["inert", "source"]}

s = json.dumps(blocks_json)

print(s)
