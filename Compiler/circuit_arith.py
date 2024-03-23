"""
This module contains functionality using circuits in the so-called
`Bristol Fashion`_ format. You can download a few examples including
the ones used below into ``Programs/Circuits`` as follows::

    make Programs/Circuits

.. _`Bristol Fashion`: https://homes.esat.kuleuven.be/~nsmart/MPC

"""
import math

from Compiler.GC.types import *
from Compiler.library import function_block, get_tape
from Compiler import util
import itertools
import struct

from enum import Enum


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


TWO_OPERANDS_GATES = (
    AGateType.ADD,
    AGateType.DIV,
    AGateType.EQ,
    AGateType.GT,
    AGateType.GEQ,
    AGateType.LT,
    AGateType.LEQ,
    AGateType.MUL,
    AGateType.NEQ,
    AGateType.SUB,
)



class Circuit:
    """
    Use a Bristol Fashion circuit in a high-level program. The
    following example adds signed 64-bit inputs from two different
    parties and prints the result::

        from circuit import Circuit
        sb64 = sbits.get_type(64)
        adder = Circuit('adder64')
        a, b = [sbitvec(sb64.get_input_from(i)) for i in (0, 1)]
        print_ln('%s', adder(a, b).elements()[0].reveal())

    Circuits can also be executed in parallel as the following example
    shows::

        from circuit import Circuit
        sb128 = sbits.get_type(128)
        key = sb128(0x2b7e151628aed2a6abf7158809cf4f3c)
        plaintext = sb128(0x6bc1bee22e409f96e93d7e117393172a)
        n = 1000
        aes128 = Circuit('aes_128')
        ciphertexts = aes128(sbitvec([key] * n), sbitvec([plaintext] * n))
        ciphertexts.elements()[n - 1].reveal().print_reg()

    This executes AES-128 1000 times in parallel and then outputs the
    last result, which should be ``0x3ad77bb40d7a3660a89ecaf32466ef97``,
    one of the test vectors for AES-128.

    """

    def __init__(self, name):
        self.filename = 'Programs/Circuits/%s.txt' % name
        f = open(self.filename)
        self.functions = {}

    def __call__(self, *inputs):
        return self.run(*inputs)

    def run(self, *inputs):
        print("!@# run: inputs=", inputs)
        # FIXME: originally it should be (# of bits, id)
        # we're getting inputs in integers and just set it as 0 to avoid error
        n = 0, get_tape()
        if n not in self.functions:
            self.functions[n] = function_block(lambda *args:
                                               self.compile(*args))
        combined_inputs = itertools.chain(*inputs)
        flat_res = self.functions[n](*combined_inputs)
        print("!@# run: flat_res       =", flat_res)
        # return all outputs in bits
        # for l in self.n_output_wires:
        #     v = []
        #     for j in range(l):
        #         v.append(flat_res[i])
        #         i += 1
        #     res.append(sbitvec.from_vec(v))

        res = list(flat_res)
        return util.untuplify(res)

    def compile(self, *all_inputs):
        f = open(self.filename)
        lines = iter(f)
        next_line = lambda: next(lines).split()
        # First line: # gates in total and # wires in total
        n_gates, n_wires = (int(x) for x in next_line())
        self.n_wires = n_wires
        input_line = [int(x) for x in next_line()]
        # Second line: # outer inputs and # bits they occupy
        # since we're parsing with sint, no need to specify bits.
        # just pass some random ints, e.g. "4 1 1 1 1" for 4 inputs
        n_inputs = input_line[0]
        n_input_wires = input_line[1:]
        assert(n_inputs == len(n_input_wires))

        #
        output_line = [int(x) for x in next_line()]
        n_outputs = output_line[0]
        self.n_output_wires = output_line[1:]
        assert(n_outputs == len(self.n_output_wires))
        next(lines)

        wires = [None] * n_wires
        self.wires = wires
        i_wire = 0
        # inputs        = (s2, s3)
        # n_input_wires = [64, 64]  # useless for arithc

        # s = 0
        # print("!@# all_inputs=", all_inputs)
        # for n in n_input_wires:
        #     # _in = all_inputs[s:s + n]
        #     _in = all_inputs[n]
        #     inputs.append(_in)
        #     # Note: it is too troublesome.
        #     print(f"!@# {_in=}, {s=}, {s+n=}")
        #     s += n

        # actual input values passed
        inputs = all_inputs[:n_inputs]
        print("!@# compile: actual inputs=", inputs)
        print("!@# compile: n_input_wires=", n_input_wires)
        # link wires to actual inputs
        for input, input_wires in zip(inputs, n_input_wires):
            # No need to check bits
            # assert(len(input) == input_wires)
            # # this for go through all bits, assign bit0 of input0 to wire0, etc.
            # for i, reg in enumerate(input):
            #     # wires[0] = input_bit[0]
            #     wires[i_wire] = reg
            #     i_wire += 1
            wires[i_wire] = input
            i_wire += 1

        # TODO: check n_gates == number of lines for gates
        for i in range(n_gates):
            line = next_line()
            t = line[-1]
            gate_type = AGateType(t)
            print("!@# compile: gate line=", line)
            if gate_type in TWO_OPERANDS_GATES:
                # 2 inputs 1 output
                assert line[0] == '2'
                assert line[1] == '1'
                assert len(line) == 6
                # inputs = [wires[line[2]], wires[line[3]]]
                ins = [wires[int(line[2 + i])] for i in range(2)]
                if gate_type == AGateType.ADD:
                    # I.e. output = input0 + input1
                    wires[int(line[4])] = ins[0] + ins[1]
                elif gate_type == AGateType.MUL:
                    wires[int(line[4])] = ins[0] * ins[1]
                elif gate_type == AGateType.LT:
                    wires[int(line[4])] = ins[0] < ins[1]
                elif gate_type == AGateType.SUB:
                    wires[int(line[4])] = ins[0] - ins[1]
                elif gate_type == AGateType.EQ:
                    wires[int(line[4])] = ins[0] == ins[1]
                elif gate_type == AGateType.NEQ:
                    wires[int(line[4])] = ins[0] != ins[1]
                elif gate_type == AGateType.GT:
                    wires[int(line[4])] = ins[0] > ins[1]
                elif gate_type == AGateType.GEQ:
                    wires[int(line[4])] = ins[0] >= ins[1]
                elif gate_type == AGateType.LEQ:
                    wires[int(line[4])] = ins[0] <= ins[1]
                # sanity check
                else:
                    raise Exception('should never be here')
            # elif gate_type == 'INV':
            #     # 1 input 1 output
            #     assert line[0] == '1'
            #     assert line[1] == '1'
            #     assert len(line) == 5
            #     wires[int(line[3])] = ~wires[int(line[2])]
        print("!@# wires=", wires)
        # E.g. n_output_wires=[64], sum=64
        # return self.wires[-64:]
        # this means to return the last elements (outputs) in `wires`
        # return self.wires[-sum(self.n_output_wires):]
        outputs = self.wires[-n_outputs:]
        print("!@# compile: outputs=", outputs)
        return outputs
