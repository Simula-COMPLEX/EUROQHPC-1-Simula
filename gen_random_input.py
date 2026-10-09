import random
from math import floor

from qiskit import QuantumCircuit, qasm2
from qiskit.circuit.random import random_circuit


class Gen_Random_Input:
    def __init__(
            self,
            qasm_file: str, #location of the qasm file
            num_inputs: int, #number of total inputs
            input_types: list[str] #the type of inputs: ['C'], ['Q'], or ['C','Q']
    ):
        self.qasm_file=qasm_file
        self.num_inputs=num_inputs
        self.input_types=input_types

        self.num_qubits=qasm2.load(qasm_file).num_qubits

    #Int -> [Int] -> [QuantumState_str]
    #creates a binary string for each int in the array, limited to a maximum number defined by the number of qubits
    def create_binary(self, num_array:list[int])->list[str]:
        inputs = ("",)
        for x in num_array:
            binariInput = str(bin(x)) #bin(5) = "0b101"
            binariInput = binariInput[2:len(binariInput)] # "0b101" -> "101"
            if len(binariInput) < self.num_qubits:
                y = len(binariInput)
                tmp = ""
                while y < self.num_qubits:
                    tmp = tmp + str(0)
                    y = y + 1
                binariInput = tmp + binariInput
            inputs = inputs + (binariInput,)

        return inputs[1:len(inputs)] #drops the empty string created at the start

    #Int -> [QuantumState_str] -> QuantumCircuit
    #Given a number of qubits and a classical array of bits, creates a quantum circuit
    def circuitinitialization_classic(self, input:list[str])->QuantumCircuit:
        qc = QuantumCircuit(self.num_qubits)
        x = 0
        for bit in input:
            if bit == '1':
                qc.x(x)
            x = x + 1

        return qc

    #based on input_types, decides how many inputs are quantum, classical, or quantum and classical and then creates random inputs in qiskit and openqasm2
    def createInputs(self) -> tuple[dict, dict]:
        num_inputs_aux = floor(self.num_inputs / len(self.input_types))
        inputs_str = {}

        input_circuits = {}
        if 'C' in self.input_types:
            if num_inputs_aux >= 2**self.num_qubits:
                c_input_ints = range(0, 2 ** self.num_qubits)
            else:
                c_input_ints = random.sample(range(0, 2 ** self.num_qubits), k=num_inputs_aux)

            inputs_bin = self.create_binary(c_input_ints)

            for i, bin in enumerate(inputs_bin):
                new_qc = self.circuitinitialization_classic(bin)
                inputs_str["ClassicInput_" + str(i)] = bin
                input_circuits["ClassicInput_" + str(i)] = new_qc

        if 'Q' in self.input_types:
            for i in range(num_inputs_aux):
                new_qc = random_circuit(num_qubits=self.num_qubits, depth=2, measure=False)
                inputs_str["QuantumInput_" + str(i)] = str(qasm2.dumps(new_qc))
                input_circuits["QuantumInput_" + str(i)] = new_qc

        return input_circuits, inputs_str

