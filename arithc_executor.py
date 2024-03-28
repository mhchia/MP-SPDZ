import json
import os
from pathlib import Path


CIRCUIT_NAME = 'arith_circuit_interpreter'
CIRCUIT_INTERPRETER_PATH = Path(f'Programs/Source/{CIRCUIT_NAME}.mpc')
CIRCUIT_INTERPRETER_PATH.parent.mkdir(parents=True, exist_ok=True)
CMD_RUN_INTERPRETER = f'Scripts/compile-run.py -E semi {CIRCUIT_NAME} -M'

# Actual arithmetic circuit to be executed by the MP-SPDZ interpreter above
# ARITH_CIRCUIT_NAME = 'arith_circuit_example'
# ARITH_CIRCUIT_NAME = 'circ'
ARITH_CIRCUIT_NAME = 'nn_circuit_small'
# ARITH_CIRCUIT_NAME = 'strange'
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
    #   "input_name_to_wire_index": { "a": 1, "b": 0, "c": 2},
    #   "constants": {"d": {"value": 50, "wire_index": 3}},
    #   "output_name_to_wire_index": { "a_add_b": 4, "a_mul_c": 5 }
    # }
    with open(circuit_info_path, 'r') as f:
        raw = json.load(f)

    input_name_to_wire_index = {k: int(v) for k, v in raw['input_name_to_wire_index'].items()}
    constants: dict[str, dict[str, int]] = raw['constants']
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
    inputs_str_list = []
    wire_index_for_input = []
    for name, o in constants.items():
        value = o['value']
        wire_index = o['wire_index']
        wire_index_for_input.append(wire_index)
        inputs_str_list.append(f'cint({value})')
    for party, inputs in inputs_from.items():
        for name in inputs:
            wire_index = input_name_to_wire_index[name]
            wire_index_for_input.append(wire_index)
            inputs_str_list.append(f'sint.get_input_from({party})')

    #
    # Generate the circuit code
    #
    inputs_str = '[' + ', '.join(inputs_str_list) + ']'
    # For outputs, should print the actual output names, and
    # lines are ordered by actual output wire index since it's guaranteed the order
    # E.g.
    # print_ln('outputs[0]: a_add_b=%s', outputs[0].reveal())
    # print_ln('outputs[1]: a_mul_c=%s', outputs[1].reveal())
    print_outputs_str_list = [
        f"print_ln('outputs[{i}]: {output_name}=%s', outputs[{output_name_to_wire_index[output_name]}].reveal())"
        for i, output_name in enumerate(output_name_to_wire_index.keys())
    ]
    print_outputs_str = '\n'.join(print_outputs_str_list)
    circuit = f"""from circuit_arith import Circuit
circuit = Circuit('{arith_circuit_path}', {wire_index_for_input})
inputs = {inputs_str}
outputs = circuit(inputs)
# Print outputs
{print_outputs_str}
"""
    return circuit


if __name__ == '__main__':
    main()
