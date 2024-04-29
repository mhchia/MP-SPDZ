# Generate an input config file at `MPC_SETTINGS_PATH` with content like this:
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
# CIRCUIT_NAME = "strange"
# CIRCUIT_NAME = "two_outputs"
CIRCUIT_INFO_PATH = f"{CIRCUIT_NAME}.circuit_info.json"
MPC_SETTINGS_PATH = f'{CIRCUIT_NAME}.mpc_settings.json'
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
    #     "a": 0,
    #     "b": 1,
    # }
    # inputs_from = {}
    # inputs_from[str(0)] = list(input_name_to_wire_index_without_consts.keys())
    # for i in range(1, NUM_PARTIES):
    #     inputs_from[str(i)] = []
    inputs_from = {
        name: 0
        for name in input_name_to_wire_index_without_consts.keys()
    }

    with open(MPC_SETTINGS_PATH, 'w') as f:
        json.dump({
            'inputs_from': inputs_from,
            "num_parties": NUM_PARTIES,
        }, f, indent=4)

    num_inputs = len(input_name_to_wire_index)

    def get_input_json_path(party):
        return f"{CIRCUIT_NAME}_{party}.input.json"

    with open(get_input_json_path(0), 'w') as f:
        json.dump({
            input_name: value
            for input_name, value in zip(input_name_to_wire_index.keys(), range(num_inputs))
        }, f, indent=4)
    with open(get_input_json_path(1), 'w') as f:
        json.dump({}, f, indent=4)

    # # generate inputs in wire order
    # # sort wire names with its index
    # wire_to_name_sorted = sorted(input_name_to_wire_index.items(), key=lambda x: x[1])
    # print(f"!@# wire_to_name_sorted={wire_to_name_sorted}")
    # wire_value_in_order_for_mpsdz = {
    #     i: [] for i in range(NUM_PARTIES)
    # }
    # for wire_name, wire_index in wire_to_name_sorted:
    #     wire_from_party = inputs_from[wire_name]
    #     wire_value = inputs_value[wire_name]
    #     wire_value_in_order_for_mpsdz[wire_from_party].append(wire_value)

    # for i in range(NUM_PARTIES):
    #     input_file_path_for_party = f"Player-Data/Input-P{i}-0"
    #     with open(input_file_path_for_party, 'w') as f:
    #         f.write(" ".join(map(str, wire_value_in_order_for_mpsdz[i])))

    # # Generate real inputs for the circuit
    # #   input_file_for_party_i = "Player-Data/Input-P0-0"
    # actual_inputs = {}
    # for i in range(NUM_PARTIES):
    #     input_file_path_for_party = f"Player-Data/Input-P{i}-0"
    #     actual_inputs[i] = list(range(i * NUM_INPUTS_PER_PARTY, (i + 1) * NUM_INPUTS_PER_PARTY))
    #     with open(input_file_path_for_party, 'w') as f:
    #         f.write(" ".join(map(str, actual_inputs[i])))

    # print("!@# actual_inputs=", actual_inputs)
    # print("!@# input_from=", inputs_from)

    # # Order:
    # #   - "w0[0][0]",
    # #   - "in[0]",
    # #   - "w0[0][1]",
    # #   - "in[1]",
    # # Assign values to each inputs
    # # inputs_from: {"0": ["a", "b"], "1": c}
    # wire_to_name_sorted = sorted(input_name_to_wire_index.items(), key=lambda x: x[1])
    # # wire_value_in_order_for_mpsdz = {
    # #     i: [] for i in range(NUM_PARTIES)
    # # }


if __name__ == "__main__":
    main()

