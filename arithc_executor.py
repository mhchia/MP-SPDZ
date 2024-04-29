from dataclasses import dataclass
from enum import Enum
import json
import os
from pathlib import Path

class AGateType(Enum):
    ADD = 'AAdd'
    DIV = 'ADiv'
    EQ = 'AEq'
    GT = 'AGt'
    GEQ = 'AGEq'
    LT = 'ALt'
    LEQ = 'ALEq'
    MUL = 'AMul'
    NEQ = 'ANeq'
    SUB = 'ASub'


# Each gate line looks like this: '2 1 26 25 35 AAdd'
@dataclass(frozen=True)
class Gate:
    num_inputs: int
    num_outputs: int
    gate_type: AGateType
    inputs_wires: list[int]
    output_wire: int


MAP_GATE_TYPE_TO_OPERATOR_STR = {
    AGateType.ADD: '+',
    AGateType.MUL: '*',
    AGateType.DIV: '/',
    AGateType.LT: '<',
    AGateType.SUB: '-',
    AGateType.EQ: '==',
    AGateType.NEQ: '!=',
    AGateType.GT: '>',
    AGateType.GEQ: '>=',
    AGateType.LEQ: '<=',
}


# ARITH_CIRCUIT_NAME = 'nn_circuit_small'

# ARITH_CIRCUIT_NAME = 'arith_circuit_example'
# ARITH_CIRCUIT_NAME = 'circ'
# ARITH_CIRCUIT_NAME = 'strange'
ARITH_CIRCUIT_NAME = 'two_outputs'
CIRCUIT_INTERPRETER_PATH = Path(f'Programs/Source/{ARITH_CIRCUIT_NAME}.mpc')
CIRCUIT_INTERPRETER_PATH.parent.mkdir(parents=True, exist_ok=True)
CMD_RUN_INTERPRETER = f'Scripts/compile-run.py -E semi {ARITH_CIRCUIT_NAME} -M'

# Actual arithmetic circuit to be executed by the MP-SPDZ interpreter above
ARITH_CIRCUIT_PATH = f"{ARITH_CIRCUIT_NAME}.txt"
# Config file defining a input is either a constant or should be read from which party
MPC_SETTINGS_PATH = f'{ARITH_CIRCUIT_NAME}.mpc_settings.json'
CIRCUIT_INFO_PATH = f"{ARITH_CIRCUIT_NAME}.circuit_info.json"
WIRE_ID_FOR_INPUT_PATH = f"{ARITH_CIRCUIT_NAME}.wire_id_for_inputs.json"
ARITHC_INPUTS_JSON_DIR = Path("Player-Data") / "arithc"


def main():
    # Generate MP-SPDZ circuit to interpret the  and write to file
    # TODO: MPC_SETTINGS_PATH should be an argument to the script
    interpreter_code = generate_arith_circuit_interpreter(ARITH_CIRCUIT_PATH, CIRCUIT_INFO_PATH, MPC_SETTINGS_PATH)
    with open(CIRCUIT_INTERPRETER_PATH, 'w') as f:
        f.write(interpreter_code)

    generate_mpspdz_inputs(CIRCUIT_INFO_PATH, MPC_SETTINGS_PATH)

    # Run the MP-SPDZ interpreter to interpret the arithmetic circuit
    os.system(CMD_RUN_INTERPRETER)


def generate_arith_circuit_interpreter(
    arith_circuit_path: str,
    circuit_info_path: str,
    mpc_settings_path: str,
):
    '''
    Generate the MP-SPDZ code to interpret the arithmetic circuit

    Steps:
    1. Read the arithmetic circuit file to get the gates
    2. Read the circuit info file to get the input/output wire mapping
    3. Read the input config file to get which party inputs should be read from
    4. Generate the MP-SPDZ from the inputs above. The code should:
        4.1. Initialize a `wires` list with input wires filled in: if a wire is a constant, fill it in directly. if a wire is an input, fill in which party this input comes from
        4.2. Translate the gates into corresponding operations in MP-SPDZ
        4.3. Print the outputs
    '''
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
    #   "inputs_from": {
    #     "a": 0,
    #     "b": 1,
    #   }
    # }
    with open(mpc_settings_path, 'r') as f:
        input_config = json.load(f)
    inputs_from: dict[str, int] = input_config['inputs_from']

    # Read number of wires from the bristol circuit file
    with open(arith_circuit_path, 'r') as f:
        first_line = next(f)
        num_gates, num_wires = map(int, first_line.split())
        second_line = next(f)
        num_inputs = int(second_line.split()[0])
        third_line = next(f)
        num_outputs = int(third_line.split()[0])
        # Skip the next line
        next(f)

        # Read the gate lines
        gates: list[Gate] = []
        for line in f:
            line = line.split()
            num_inputs = int(line[0])
            num_outputs = int(line[1])
            inputs_wires = [int(x) for x in line[2:2+num_inputs]]
            # Support 2 inputs only for now
            assert num_inputs == 2 and num_inputs == len(inputs_wires)
            output_wires = list(map(int, line[2+num_inputs:2+num_inputs+num_outputs]))
            output_wire = output_wires[0]
            # Support 1 output only for now
            assert num_outputs == 1 and num_outputs == len(output_wires)
            gate_type = AGateType(line[2+num_inputs+num_outputs])
            gates.append(Gate(num_inputs, num_outputs, gate_type, inputs_wires, output_wire))
    assert len(gates) == num_gates

    # Make inputs to circuit (not wires!!) from the user config
    # Initialize a list `inputs` with `num_wires` with value=None
    inputs_str_list = [None] * num_wires
    # Fill in the constants
    for name, o in constants.items():
        value = int(o['value'])
        wire_index = int(o['wire_index'])
        # Sanity check
        if inputs_str_list[wire_index] is not None:
            raise ValueError(f"Wire index {wire_index} is already filled in: {inputs_str_list[wire_index]=}")
        inputs_str_list[wire_index] = f'cint({value})'
    # Fill in the inputs from the parties
    for name, party in inputs_from.items():
        wire_index = int(input_name_to_wire_index[name])
        # Sanity check
        if inputs_str_list[wire_index] is not None:
            raise ValueError(f"Wire index {wire_index} is already filled in: {inputs_str_list[wire_index]=}")
        inputs_str_list[wire_index] = f'sint.get_input_from({party})'

    # Replace all `None` with str `'None'`
    inputs_str_list = [x if x is not None else 'None' for x in inputs_str_list]

    #
    # Generate the circuit code
    #
    inputs_str = '[' + ', '.join(inputs_str_list) + ']'

    # Translate bristol gates to MP-SPDZ operations
    # E.g.
    # '2 1 1 0 2 AAdd' in bristol
    #   is translated to
    # 'wires[2] = wires[1] + wires[0]' in MP-SPDZ
    gates_str_list = []
    for gate in gates:
        gate_str = ''
        if gate.gate_type not in MAP_GATE_TYPE_TO_OPERATOR_STR:
            raise ValueError(f"Gate type {gate.gate_type} is not supported")
        else:
            operator_str = MAP_GATE_TYPE_TO_OPERATOR_STR[gate.gate_type]
            gate_str = f'wires[{gate.output_wire}] = wires[{gate.inputs_wires[0]}] {operator_str} wires[{gate.inputs_wires[1]}]'
        gates_str_list.append(gate_str)
    gates_str = '\n'.join(gates_str_list)

    # For outputs, should print the actual output names, and
    # lines are ordered by actual output wire index since it's guaranteed the order
    # E.g.
    # print_ln('outputs[0]: a_add_b=%s', outputs[0].reveal())
    # print_ln('outputs[1]: a_mul_c=%s', outputs[1].reveal())
    print_outputs_str_list = [
        f"print_ln('outputs[{i}]: {output_name}=%s', wires[{output_name_to_wire_index[output_name]}].reveal())"
        for i, output_name in enumerate(output_name_to_wire_index.keys())
    ]
    print_outputs_str = '\n'.join(print_outputs_str_list)

    circuit = f"""wires = {inputs_str}
{gates_str}
# Print outputs
{print_outputs_str}
"""
    return circuit


def generate_mpspdz_inputs_for_party(
    party: int,
    circuit_info_path: str,
    mpc_settings_path: str,
):
    '''
    Generate inputs for MP-SPDZ circuit

    - The input file for circom mpc is defined as `{"input_name_0": input_value_0, "input_name_1": input_value_1, ... "input_name_N": input_value_N}`
    - The actual wire list in the MP-SPDZ looks like
      `[cint(123), sint.read_from_party(0), sint.read_from_party(1), cint(456), sint.read_from_party(0)]`
    - In MP-SPDZ, input file is a text file in the format of `input0 input1 input2 ... inputN`, each separated with a space
    - For a party, we need to generate an input file for MP-SPDZ according to the wire order of their inputs
      - Continued with the example above, for party 0, its MP-SPDZ input file should be `input1 input4`
      - This order can be obtained by sorting the `input_name_to_wire_index` by the wire index
    '''

    # Read inputs value from user provided input files
    input_json_for_party_path = f"{ARITH_CIRCUIT_NAME}_party_{party}.inputs.json"
    with open(input_json_for_party_path) as f:
        input_values_for_party_json = json.load(f)

    with open(mpc_settings_path, 'r') as f:
        input_config = json.load(f)
    inputs_from: dict[str, int] = input_config['inputs_from']
    with open(circuit_info_path, 'r') as f:
        circuit_info = json.load(f)
        input_name_to_wire_index = circuit_info['input_name_to_wire_index']

    wire_to_name_sorted = sorted(input_name_to_wire_index.items(), key=lambda x: x[1])
    wire_value_in_order_for_mpsdz = []
    for wire_name, wire_index in wire_to_name_sorted:
        wire_from_party = int(inputs_from[wire_name])
        # For the current party, we only care about the inputs from itself
        if wire_from_party == party:
            wire_value = input_values_for_party_json[wire_name]
            wire_value_in_order_for_mpsdz.append(wire_value)
    # Write these ordered wire inputs for mp-spdz usage
    input_file_for_party_mpspdz = f"Player-Data/Input-P{party}-0"
    with open(input_file_for_party_mpspdz, 'w') as f:
        f.write(" ".join(map(str, wire_value_in_order_for_mpsdz)))


def generate_mpspdz_inputs(circuit_info_path: str, mpc_settings_path: str):
    """
    Generate inputs for MP-SPDZ circuit for all parties. This is a helper function
    to generate inputs for all parties locally for testing.
    In a real-world scenario, each party should generate their own input file with
    `generate_mpspdz_inputs_for_party` function.
    """
    with open(mpc_settings_path, 'r') as f:
        input_config = json.load(f)
    num_parties = int(input_config['num_parties'])
    for party in range(num_parties):
        generate_mpspdz_inputs_for_party(party, circuit_info_path, mpc_settings_path)


if __name__ == '__main__':
    main()
