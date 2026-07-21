import random

from qiskit import QuantumCircuit


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

def circuititialization(numqubits, input):
    qc = QuantumCircuit(numqubits)
    x = 0
    for bit in input:
        if bit == '1':
            qc.x(x)
        x = x + 1

    return qc
def createInputs(num_qubits, input_types, num_inputs):
    inputs = {}

    if 'C' in input_types and 'Q' in input_types:
        c_inputs = {}
        if num_inputs/2 >= 2 ** num_qubits:
            c_input_ints = range(0, 2 ** num_qubits)
        else:
            c_input_ints = random.sample(range(0, 2 ** num_qubits), k=num_inputs/2)

        inputs_bin = create_binary(num_qubits, c_input_ints)

        for i, bin in enumerate(inputs_bin):
            new_qc = circuititialization(num_qubits, bin)
            inputs["ClassicInput_"+str(i)] = bin
            c_inputs["ClassicInput_"+str(i)]=new_qc

        # q_inputs = []
        # mutator = UCNOTMutator()
        # circuit = Circuit(num_qubits)
        # for i in range(num_inputs / 2):
        #     q_input = mutator.generate_circuit(circuit)
        #     q_input_qasm = q_input.code.qasm()
        #     q_input_circ = QuantumCircuit.from_qasm_str(q_input_qasm)
        #     q_inputs.append(q_input_circ)

    else:
        if 'C' in input_types:
            c_inputs = {}
            if num_inputs >= 2**num_qubits:
                c_input_ints = range(0, 2 ** num_qubits)
            else:
                c_input_ints = random.sample(range(0, 2 ** num_qubits), k=num_inputs)

            inputs_bin = create_binary(num_qubits, c_input_ints)

            for i, bin in enumerate(inputs_bin):
                new_qc = circuititialization(num_qubits, bin)
                inputs["ClassicInput_" + str(i)] = bin
                c_inputs["ClassicInput_"+str(i)] = new_qc

        # else:
        #     q_inputs = []
        #     mutator = UCNOTMutator()
        #     circuit = Circuit(num_qubits)
        #     for i in range(num_inputs):
        #         q_input = mutator.generate_circuit(circuit)
        #         q_input_qasm = q_input.code.qasm()
        #         q_input_circ = QuantumCircuit.from_qasm_str(q_input_qasm)
        #         q_inputs.append(q_input_circ)


    input_circuits = c_inputs # | q_inputs

    return input_circuits, inputs

def addMeasurements(qc, base, output_type):
    new_qc = QuantumCircuit(qc.num_qubits)
    new_qc.compose(qc.copy())

    if base == 'X':
        # qc.barrier()
        for qubit in new_qc.qubits:
            new_qc.h(qubit)
    elif base == 'Y':
        # qc.barrier()
        for qubit in new_qc.qubits:
            new_qc.sdg(qubit)
            new_qc.h(qubit)

    if output_type == "State":
        new_qc.save_statevector()
    else:
        new_qc.measure_all()

    return new_qc

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
            tests["TestCase_" + str(test_count)] = inputs[input_name] + base
            test_count = test_count + 1


    return circuits, tests
