# Generate an input config file at `OUTPUT_CONFIG_PATH` with content like this:
# {
#     "inputs_from": {
#         "0": ["a", "b"],
#         "1": ["c"]
#     }
# }
# Using `CIRCUIT_INFO_PATH` with content like this:
# {
#     "input_name_to_wire_index": {
#         "a": 1,
#         "b": 0,
#         "c": 2
#     },
#     "constants": {"d": { "value": 50, "wire_index": 3 }},
#     "output_name_to_wire_index": {
#         "a_add_b": 4,
#         "a_mul_c": 5
#     }
# }

import json

CIRCUIT_NAME = "nn_circuit_small"
# CIRCUIT_NAME = "two_outputs"
CIRCUIT_INFO_PATH = f"{CIRCUIT_NAME}.circuit_info.json"
OUTPUT_CONFIG_PATH = f'Configs/{CIRCUIT_NAME}.json'
NUM_PARTIES = 2
NUM_INPUTS_PER_PARTY = 200


def main():
    # Load the node_id_to_wire_index
    # {
    #   "input_name_to_wire_index": { "a": 1, "b": 0, "c": 2 },
    #   "constants": {"d": {"value": 50, "wire_index": 3}},
    #   "output_name_to_wire_index": { "a_add_b": 4, "a_mul_c": 5 }
    # }
    with open(CIRCUIT_INFO_PATH, 'r') as f:
        raw = json.load(f)

    input_name_to_wire_index = {k: int(v) for k, v in raw['input_name_to_wire_index'].items()}
    constants = raw['constants'].items()
    input_name_to_wire_index_without_consts = {
        k: v for k, v in input_name_to_wire_index.items() if k not in constants
    }

    len_inputs_required = len(input_name_to_wire_index_without_consts)
    assert NUM_INPUTS_PER_PARTY > len_inputs_required

    # Generate the output config file
    # E.g.
    # {
    #     "inputs_from": {
    #         "0": ["a", "b"],
    #         "1": ["c"]
    #     }
    # }
    inputs_from = {}
    inputs_from[str(0)] = list(input_name_to_wire_index_without_consts.keys())
    for i in range(1, NUM_PARTIES):
        inputs_from[str(i)] = []

    with open(OUTPUT_CONFIG_PATH, 'w') as f:
        json.dump({'inputs_from': inputs_from}, f, indent=4)

    # Generate real inputs for the circuit
    #     input_file_for_party_i = "Player-Data/Input-P0-0"
    for i in range(NUM_PARTIES):
        input_file_path_for_party = f"Player-Data/Input-P{i}-0"
        actual_inputs = range(i * NUM_INPUTS_PER_PARTY, (i + 1) * NUM_INPUTS_PER_PARTY)
        with open(input_file_path_for_party, 'w') as f:
            f.write(" ".join(map(str, actual_inputs)))


if __name__ == "__main__":
    main()

