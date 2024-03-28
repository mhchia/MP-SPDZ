import json
import os
from pathlib import Path


CIRCUIT_NAME = 'arith_circuit_interpreter'
CIRCUIT_INTERPRETER_PATH = Path(f'Programs/Source/{CIRCUIT_NAME}.mpc')
CIRCUIT_INTERPRETER_PATH.parent.mkdir(parents=True, exist_ok=True)
CMD_RUN_INTERPRETER = f'Scripts/compile-run.py -E semi {CIRCUIT_NAME}'

# Actual arithmetic circuit to be executed by the MP-SPDZ interpreter above
# ARITH_CIRCUIT_NAME = 'arith_circuit_example'
# ARITH_CIRCUIT_NAME = 'circ'
ARITH_CIRCUIT_NAME = 'nn_circuit_small'
# ARITH_CIRCUIT_NAME = 'two_outputs'
ARITH_CIRCUIT_PATH = f"{ARITH_CIRCUIT_NAME}.txt"
# Config file defining a input is either a constant or should be read from which party
INPUT_CONFIG_PATH = f'Configs/{ARITH_CIRCUIT_NAME}.json'
CIRCUIT_INFO_PATH = f"{ARITH_CIRCUIT_NAME}.circuit_info.json"
WIRE_ID_FOR_INPUT_PATH = f"{ARITH_CIRCUIT_NAME}.wire_id_for_inputs.json"


def main():
    # Generate MP-SPDZ circuit to interpret the  and write to file
    # TODO: INPUT_CONFIG_PATH should be an argument to the script
    interpreter_code = generate_arith_circuit_interpreter(ARITH_CIRCUIT_PATH, CIRCUIT_INFO_PATH, INPUT_CONFIG_PATH)
    with open(CIRCUIT_INTERPRETER_PATH, 'w') as f:
        f.write(interpreter_code)
    # Run the MP-SPDZ interpreter to interpret the arithmetic circuit
    os.system(CMD_RUN_INTERPRETER)


def generate_arith_circuit_interpreter(
    arith_circuit_path: str,
    circuit_info_path: str,
    input_config_path: str,
):
    # {
    #   "input_name_to_wire_index": { "a": 1, "b": 0, "c": 2, "d": 3},
    #   "constant_values": {"d": 50},
    #   "output_name_to_wire_index": { "a_add_b": 4, "a_mul_c": 5 }
    # }
    with open(circuit_info_path, 'r') as f:
        raw = json.load(f)

    input_name_to_wire_index = {k: int(v) for k, v in raw['input_name_to_wire_index'].items()}
    constants = {k: int(v) for k, v in raw['constant_values'].items()}
    output_name_to_wire_index = {k: int(v) for k, v in raw['output_name_to_wire_index'].items()}
    # {
    #     "inputs_from": {
    #         "0": ["a", "b"],
    #         "1": ["c"]
    #     }
    # }
    with open(input_config_path, 'r') as f:
        input_config = json.load(f)
    inputs_from: dict[str, list[str]] = input_config['inputs_from']

    # Make inputs to circuit (not wires!!) from the user config
    # The inputs order will be [constant1, constant2, ..., party_0_input1, party_0_input2, ..., party_1_input1, ...]
    inputs_name_list = []
    inputs_str_list = []
    for name, value in constants.items():
        inputs_name_list.append(name)
        inputs_str_list.append(f'cint({value})')
    for party, inputs in inputs_from.items():
        for name in inputs:
            inputs_name_list.append(name)
            inputs_str_list.append(f'sint.get_input_from({party})')
    inputs_str = '[' + ', '.join(inputs_str_list) + ']'

    # For outputs, should print the actual output names, and
    # lines are ordered by actual output wire index since it's guaranteed the order
    # E.g.
    # print_ln('Outputs[0]: a_add_b=%s', outputs[4].reveal())
    # print_ln('Outputs[1]: a_mul_c=%s', outputs[5].reveal())
    len_output_name_to_wire_index = len(output_name_to_wire_index)
    print_outputs_str_list = [
        f"print_ln('outputs[{i}]: {output_name}=%s', outputs[{i}].reveal())"
        for i, output_name in enumerate(output_name_to_wire_index)
    ]
    print_outputs_str = '\n'.join(print_outputs_str_list)

    # Write the wire index for inputs to a file, for the interpreter to use
    wire_index_for_input = [input_name_to_wire_index[name] for name in inputs_name_list]
    with open(WIRE_ID_FOR_INPUT_PATH, 'w') as f:
        json.dump(wire_index_for_input, f)

    # Generate the circuit code
    circuit = f"""from circuit_arith import Circuit
circuit = Circuit('{arith_circuit_path}', '{WIRE_ID_FOR_INPUT_PATH}')
inputs = {inputs_str}
outputs = circuit(inputs)
# Print outputs
{print_outputs_str}
"""
    return circuit


if __name__ == '__main__':
    main()
