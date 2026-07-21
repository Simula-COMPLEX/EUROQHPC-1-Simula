import random
from math import floor

from qiskit import QuantumCircuit, qasm2
from qiskit.circuit.random import random_circuit


def create_binary(qubitnum, num_array):
    inputs = ("",)
    # x = 0
    # while x < 2 ** qubitnum:
    for x in num_array:
        binariInput = str(bin(x))
        binariInput = binariInput[2:len(binariInput)]
        if len(binariInput) < qubitnum:
            y = len(binariInput)
            tmp = ""
            while y < qubitnum:
                tmp = tmp + str(0)
                y = y + 1
            binariInput = tmp + binariInput
        inputs = inputs + (binariInput,)
        x = x + 1

    return inputs[1:len(inputs)]

def circuitinitialization_classic(numqubits, input):
    qc = QuantumCircuit(numqubits)
    x = 0
    for bit in input:
        if bit == '1':
            qc.x(x)
        x = x + 1

    return qc

def circuitinitialization_quantum(numqubits):
    qc = QuantumCircuit(numqubits)


    return qc

def createInputs(num_qubits, input_types, num_inputs):
    num_inputs = floor(num_inputs / len(input_types))
    inputs = {}

    input_circuits = {}
    if 'C' in input_types:
        if num_inputs >= 2**num_qubits:
            c_input_ints = range(0, 2 ** num_qubits)
        else:
            c_input_ints = random.sample(range(0, 2 ** num_qubits), k=num_inputs)

        inputs_bin = create_binary(num_qubits, c_input_ints)

        for i, bin in enumerate(inputs_bin):
            new_qc = circuitinitialization_classic(num_qubits, bin)
            inputs["ClassicInput_" + str(i)] = bin
            input_circuits["ClassicInput_" + str(i)] = new_qc

    if 'Q' in input_types:
        for i in range(num_inputs):
            new_qc = random_circuit(num_qubits=num_qubits, depth=2, measure=False)
            inputs["QuantumInput_" + str(i)] = qasm2.dumps(new_qc)
            input_circuits["QuantumInput_" + str(i)] = new_qc


    return input_circuits, inputs

def addMeasurements(qc, base, output_type):
    new_qc = QuantumCircuit(qc.num_qubits)
    composed_qc = new_qc.compose(qc.copy())

    if base == 'X':
        # qc.barrier()
        for qubit in composed_qc.qubits:
            composed_qc.h(qubit)
    elif base == 'Y':
        # qc.barrier()
        for qubit in composed_qc.qubits:
            composed_qc.sdg(qubit)
            composed_qc.h(qubit)

    if output_type == "State":
        composed_qc.save_statevector()
    else:
        composed_qc.measure_all()

    return composed_qc

def initCircuits(qc, input_circuits):
    initialized_qcs = {}

    for key, value in input_circuits.items():
        initialized_qcs[key] = value.compose(qc.copy())

    return initialized_qcs
def prepare_circuits(qc, input_types, num_inputs, bases, output_type):
    circuits = {}
    tests = {}
    qc.remove_final_measurements()

    input_circuits, inputs = createInputs(qc.num_qubits, input_types, num_inputs)
    initialized_circuits = initCircuits(qc, input_circuits)

    test_count = 0
    for input_name, circ in initialized_circuits.items():
        for base in bases:
            circuits["TestCase_" + str(test_count)] = addMeasurements(circ, base, output_type)
            tests["TestCase_" + str(test_count)] = inputs[input_name] + '_Base_' + base
            test_count = test_count + 1


    return circuits, tests
