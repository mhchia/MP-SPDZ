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
# CIRCUIT_NAME = "strange"
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

    with open(OUTPUT_CONFIG_PATH, 'w') as f:
        json.dump({'inputs_from': inputs_from}, f, indent=4)

    # inputs_value = {'w0[0][0]': 0, 'in[0]': 1, 'w0[0][1]': 2, 'in[1]': 3, 'w0[1][0]': 4, 'w0[1][1]': 5, 'w0[2][0]': 6, 'w0[2][1]': 7, 'b0[0]': 8, 'b0[1]': 9, 'w0[3][0]': 10, 'w0[3][1]': 11, 'b0[2]': 12, 'w0[4][0]': 13, 'w0[4][1]': 14, 'b0[3]': 15, 'b0[4]': 16, 'w1[0][0]': 17, 'w1[0][1]': 18, 'w1[1][0]': 19, 'w1[1][1]': 20, 'w1[0][2]': 21, 'w1[1][2]': 22, 'w1[2][0]': 23, 'w1[2][1]': 24, 'w1[0][3]': 25, 'w1[1][3]': 26, 'w1[2][2]': 27, 'w1[3][0]': 28, 'w1[3][1]': 29, 'w1[0][4]': 30, 'w1[1][4]': 31, 'w1[2][3]': 32, 'w1[3][2]': 33, 'w1[4][0]': 34, 'w1[4][1]': 35, 'w1[2][4]': 36, 'w1[3][3]': 37, 'w1[4][2]': 38, 'w1[5][0]': 39, 'w1[5][1]': 40, 'b1[0]': 41, 'b1[1]': 42, 'w1[3][4]': 43, 'w1[4][3]': 44, 'w1[5][2]': 45, 'w1[6][0]': 46, 'w1[6][1]': 47, 'b1[2]': 48, 'w1[4][4]': 49, 'w1[5][3]': 50, 'w1[6][2]': 51, 'b1[3]': 52, 'w1[5][4]': 53, 'w1[6][3]': 54, 'b1[4]': 55, 'w1[6][4]': 56, 'w2[0][0]': 57, 'w2[0][1]': 58, 'b1[5]': 59, 'w2[1][0]': 60, 'w2[1][1]': 61, 'w2[0][2]': 62, 'b1[6]': 63, 'w2[1][2]': 64, 'w2[2][0]': 65, 'w2[2][1]': 66, 'w2[0][3]': 67, 'w2[1][3]': 68, 'w2[2][2]': 69, 'w2[3][0]': 70, 'w2[3][1]': 71, 'w2[0][4]': 72, 'w2[1][4]': 73, 'w2[2][3]': 74, 'w2[3][2]': 75, 'w2[4][0]': 76, 'w2[4][1]': 77, 'w2[0][5]': 78, 'w2[1][5]': 79, 'w2[2][4]': 80, 'w2[3][3]': 81, 'w2[4][2]': 82, 'w2[5][0]': 83, 'w2[5][1]': 84, 'w2[0][6]': 85, 'w2[1][6]': 86, 'w2[2][5]': 87, 'w2[3][4]': 88, 'w2[4][3]': 89, 'w2[5][2]': 90, 'w2[6][0]': 91, 'w2[6][1]': 92, 'w2[2][6]': 93, 'w2[3][5]': 94, 'w2[4][4]': 95, 'w2[5][3]': 96, 'w2[6][2]': 97, 'w2[7][0]': 98, 'w2[7][1]': 99, 'b2[0]': 100, 'b2[1]': 101, 'w2[3][6]': 102, 'w2[4][5]': 103, 'w2[5][4]': 104, 'w2[6][3]': 105, 'w2[7][2]': 106, 'w2[8][0]': 107, 'w2[8][1]': 108, 'b2[2]': 109, 'w2[4][6]': 110, 'w2[5][5]': 111, 'w2[6][4]': 112, 'w2[7][3]': 113, 'w2[8][2]': 114, 'w2[9][0]': 115, 'w2[9][1]': 116, 'b2[3]': 117, 'w2[5][6]': 118, 'w2[6][5]': 119, 'w2[7][4]': 120, 'w2[8][3]': 121, 'w2[9][2]': 122, 'w2[10][0]': 123, 'w2[10][1]': 124, 'b2[4]': 125, 'w2[6][6]': 126, 'w2[7][5]': 127, 'w2[8][4]': 128, 'w2[9][3]': 129, 'w2[10][2]': 130, 'w3[0][0]': 131, 'w3[0][1]': 132, 'b2[5]': 133, 'w2[7][6]': 134, 'w2[8][5]': 135, 'w2[9][4]': 136, 'w2[10][3]': 137, 'w3[1][0]': 138, 'w3[1][1]': 139, 'w3[2][0]': 140, 'w3[2][1]': 141, 'w3[3][0]': 142, 'w3[3][1]': 143, 'w3[0][2]': 144, 'b2[6]': 145, 'w2[8][6]': 146, 'w2[9][5]': 147, 'w2[10][4]': 148, 'w3[1][2]': 149, 'w3[2][2]': 150, 'w3[3][2]': 151, 'w3[0][3]': 152, 'b2[7]': 153, 'w2[9][6]': 154, 'w2[10][5]': 155, 'w3[1][3]': 156, 'w3[2][3]': 157, 'w3[3][3]': 158, 'w3[0][4]': 159, 'b2[8]': 160, 'w2[10][6]': 161, 'w3[1][4]': 162, 'w3[2][4]': 163, 'w3[3][4]': 164, 'w3[0][5]': 165, 'b2[9]': 166, 'w3[1][5]': 167, 'w3[2][5]': 168, 'w3[3][5]': 169, 'w3[0][6]': 170, 'b2[10]': 171, 'w3[1][6]': 172, 'w3[2][6]': 173, 'w3[3][6]': 174, 'w3[0][7]': 175, 'w3[1][7]': 176, 'w3[2][7]': 177, 'w3[3][7]': 178, 'w3[0][8]': 179, 'w3[1][8]': 180, 'w3[2][8]': 181, 'w3[3][8]': 182, 'w3[0][9]': 183, 'w3[1][9]': 184, 'w3[2][9]': 185, 'w3[3][9]': 186, 'w3[0][10]': 187, 'w3[1][10]': 188, 'w3[2][10]': 189, 'w3[3][10]': 190, 'b3[0]': 191, 'b3[1]': 192, 'b3[2]': 193, 'b3[3]': 194}
    inputs_value = {'in[0]': 0, 'w0[0][0]': 1, 'in[1]': 2, 'w0[0][1]': 3, 'b0[0]': 4, 'w0[1][0]': 5, 'w0[1][1]': 6, 'b0[1]': 7, 'w0[2][0]': 8, 'w0[2][1]': 9, 'b0[2]': 10, 'w0[3][0]': 11, 'w0[3][1]': 12, 'b0[3]': 13, 'w0[4][0]': 14, 'w0[4][1]': 15, 'b0[4]': 16, 'w1[0][0]': 17, 'w1[0][1]': 18, 'w1[0][2]': 19, 'w1[0][3]': 20, 'w1[0][4]': 21, 'b1[0]': 22, 'w1[1][0]': 23, 'w1[1][1]': 24, 'w1[1][2]': 25, 'w1[1][3]': 26, 'w1[1][4]': 27, 'b1[1]': 28, 'w1[2][0]': 29, 'w1[2][1]': 30, 'w1[2][2]': 31, 'w1[2][3]': 32, 'w1[2][4]': 33, 'b1[2]': 34, 'w1[3][0]': 35, 'w1[3][1]': 36, 'w1[3][2]': 37, 'w1[3][3]': 38, 'w1[3][4]': 39, 'b1[3]': 40, 'w1[4][0]': 41, 'w1[4][1]': 42, 'w1[4][2]': 43, 'w1[4][3]': 44, 'w1[4][4]': 45, 'b1[4]': 46, 'w1[5][0]': 47, 'w1[5][1]': 48, 'w1[5][2]': 49, 'w1[5][3]': 50, 'w1[5][4]': 51, 'b1[5]': 52, 'w1[6][0]': 53, 'w1[6][1]': 54, 'w1[6][2]': 55, 'w1[6][3]': 56, 'w1[6][4]': 57, 'b1[6]': 58, 'w2[0][0]': 59, 'w2[0][1]': 60, 'w2[0][2]': 61, 'w2[0][3]': 62, 'w2[0][4]': 63, 'w2[0][5]': 64, 'w2[0][6]': 65, 'b2[0]': 66, 'w2[1][0]': 67, 'w2[1][1]': 68, 'w2[1][2]': 69, 'w2[1][3]': 70, 'w2[1][4]': 71, 'w2[1][5]': 72, 'w2[1][6]': 73, 'b2[1]': 74, 'w2[2][0]': 75, 'w2[2][1]': 76, 'w2[2][2]': 77, 'w2[2][3]': 78, 'w2[2][4]': 79, 'w2[2][5]': 80, 'w2[2][6]': 81, 'b2[2]': 82, 'w2[3][0]': 83, 'w2[3][1]': 84, 'w2[3][2]': 85, 'w2[3][3]': 86, 'w2[3][4]': 87, 'w2[3][5]': 88, 'w2[3][6]': 89, 'b2[3]': 90, 'w2[4][0]': 91, 'w2[4][1]': 92, 'w2[4][2]': 93, 'w2[4][3]': 94, 'w2[4][4]': 95, 'w2[4][5]': 96, 'w2[4][6]': 97, 'b2[4]': 98, 'w2[5][0]': 99, 'w2[5][1]': 100, 'w2[5][2]': 101, 'w2[5][3]': 102, 'w2[5][4]': 103, 'w2[5][5]': 104, 'w2[5][6]': 105, 'b2[5]': 106, 'w2[6][0]': 107, 'w2[6][1]': 108, 'w2[6][2]': 109, 'w2[6][3]': 110, 'w2[6][4]': 111, 'w2[6][5]': 112, 'w2[6][6]': 113, 'b2[6]': 114, 'w2[7][0]': 115, 'w2[7][1]': 116, 'w2[7][2]': 117, 'w2[7][3]': 118, 'w2[7][4]': 119, 'w2[7][5]': 120, 'w2[7][6]': 121, 'b2[7]': 122, 'w2[8][0]': 123, 'w2[8][1]': 124, 'w2[8][2]': 125, 'w2[8][3]': 126, 'w2[8][4]': 127, 'w2[8][5]': 128, 'w2[8][6]': 129, 'b2[8]': 130, 'w2[9][0]': 131, 'w2[9][1]': 132, 'w2[9][2]': 133, 'w2[9][3]': 134, 'w2[9][4]': 135, 'w2[9][5]': 136, 'w2[9][6]': 137, 'b2[9]': 138, 'w2[10][0]': 139, 'w2[10][1]': 140, 'w2[10][2]': 141, 'w2[10][3]': 142, 'w2[10][4]': 143, 'w2[10][5]': 144, 'w2[10][6]': 145, 'b2[10]': 146, 'w3[0][0]': 147, 'w3[0][1]': 148, 'w3[0][2]': 149, 'w3[0][3]': 150, 'w3[0][4]': 151, 'w3[0][5]': 152, 'w3[0][6]': 153, 'w3[0][7]': 154, 'w3[0][8]': 155, 'w3[0][9]': 156, 'w3[0][10]': 157, 'b3[0]': 158, 'w3[1][0]': 159, 'w3[1][1]': 160, 'w3[1][2]': 161, 'w3[1][3]': 162, 'w3[1][4]': 163, 'w3[1][5]': 164, 'w3[1][6]': 165, 'w3[1][7]': 166, 'w3[1][8]': 167, 'w3[1][9]': 168, 'w3[1][10]': 169, 'b3[1]': 170, 'w3[2][0]': 171, 'w3[2][1]': 172, 'w3[2][2]': 173, 'w3[2][3]': 174, 'w3[2][4]': 175, 'w3[2][5]': 176, 'w3[2][6]': 177, 'w3[2][7]': 178, 'w3[2][8]': 179, 'w3[2][9]': 180, 'w3[2][10]': 181, 'b3[2]': 182, 'w3[3][0]': 183, 'w3[3][1]': 184, 'w3[3][2]': 185, 'w3[3][3]': 186, 'w3[3][4]': 187, 'w3[3][5]': 188, 'w3[3][6]': 189, 'w3[3][7]': 190, 'w3[3][8]': 191, 'w3[3][9]': 192, 'w3[3][10]': 193, 'b3[3]': 194}
    from pathlib import Path
    arithc_inputs = Path("Player-Data") / "arithc"
    arithc_inputs.mkdir(parents=True, exist_ok=True)
    with open(arithc_inputs / f"Input-P0-0", 'w') as f:
        json.dump(inputs_value, f, indent=4)
    with open(arithc_inputs / f"Input-P1-0", 'w') as f:
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

