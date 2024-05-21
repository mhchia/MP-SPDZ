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

# CIRCUIT_NAME = "nn_circuit_small"
# CIRCUIT_NAME = "strange"
CIRCUIT_NAME = "two_outputs"
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
    input_names = list(input_name_to_wire_index.keys())
    output_names = list(raw['output_name_to_wire_index'].keys())
    assert NUM_INPUTS_PER_PARTY > len(input_names)

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
    # party 0 is alice, having input a, and output a_add_b, a_mul_c are revealed to
    # party 1 is bob, having input b, and output a_add_b, a_mul_c are revealed to
    # [
    #     {
    #         "name": "alice",
    #         "inputs": ["a"],
    #         "outputs": ["a_add_b", "a_mul_c"]
    #     },
    #     {
    #         "name": "bob",
    #         "inputs": ["b"],
    #         "outputs": ["a_add_b", "a_mul_c"]
    #     }
    # ]
    with open(MPC_SETTINGS_PATH, 'w') as f:
        json.dump([
            {
                "name": "alice",
                "inputs": input_names,  # All inputs are from party 0
                "outputs": output_names,  # Party 0 can see all outputs
            },
            {
                "name": "bob",
                "inputs": [],  # No input is from party 1
                "outputs": output_names,  # Party 1 can see all outputs
            }
        ], f, indent=4)

    num_inputs = len(input_names)
    # Generate inputs:
    input_values = iter(range(1, num_inputs + 1))

    def get_input_json_path(party):
        return f"{CIRCUIT_NAME}_party_{party}.inputs.json"

    # Party 0 provides all inputs
    with open(get_input_json_path(0), 'w') as f:
        json.dump({
            input_name: next(input_values)
            for input_name in input_names
        }, f, indent=4)

    # Party 1 provides no inputs
    with open(get_input_json_path(1), 'w') as f:
        json.dump({}, f, indent=4)



if __name__ == "__main__":
    main()

