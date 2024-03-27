# Generate an input config file at `OUTPUT_CONFIG_PATH` with content like this:
# [
#     {
#         "wire_id": 339827882353457231733281877774418513,
#         "wire_name": "a",
#         "is_const": false,
#         "const_value": 0,
#         "from_party": 1
#     },
#     ...
# ]

# Using `NODE_ID_TO_WIRE_INDEX_PATH` with content like this:
# {"339827882353457231733281877774418513": 1, "261273425065800872138523378011643318856": 0, "224358152556191904480812644829082501076": 2}



import json

CIRCUIT_NAME = "nn_circuit_small"
NODE_ID_TO_WIRE_INDEX_PATH = f"{CIRCUIT_NAME}.node_id_to_wire_index.json"
OUTPUT_CONFIG_PATH = f'Configs/{CIRCUIT_NAME}.json'
NUM_PARTIES = 2
NUM_INPUTS_PER_PARTY = 1000


def main():
    # Load the node_id_to_wire_index
    with open(NODE_ID_TO_WIRE_INDEX_PATH, 'r') as f:
        raw = json.load(f)
        node_id_to_wire_index = {
            int(k): int(v)
            for k, v in raw.items()
        }

    len_inputs_required = len(node_id_to_wire_index)
    assert NUM_INPUTS_PER_PARTY > len_inputs_required

    # Generate the output config file
    with open(OUTPUT_CONFIG_PATH, 'w') as f:
        json.dump([
            {
                "wire_id": node_id,
                "wire_name": f"{node_id} at wire {wire_id}",
                "is_const": False,
                "const_value": 0,
                "from_party": 1
            }
            for node_id, wire_id in node_id_to_wire_index.items()
        ], f, indent=4)

    # Generate real inputs for the circuit
    #     input_file_for_party_i = "Player-Data/Input-P0-0"
    for i in range(NUM_PARTIES):
        input_file_path_for_party = f"Player-Data/Input-P{i}-0"
        actual_inputs = range(i * NUM_INPUTS_PER_PARTY, (i + 1) * NUM_INPUTS_PER_PARTY)
        with open(input_file_path_for_party, 'w') as f:
            f.write(" ".join(map(str, actual_inputs)))


if __name__ == "__main__":
    main()

