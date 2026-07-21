from qiskit import QuantumCircuit

from circuit_preparation import prepare_circuits
from circuit_execution import execute_circuits, get_outputs


def run(origin_qc, input_types,num_inputs, measurements, output_type, shots, environment):
    
    circuits, tests = prepare_circuits(origin_qc, input_types, num_inputs, measurements, output_type)
    outputs = execute_circuits(circuits, shots, environment)
    results = get_outputs(circuits, outputs, output_type)


    print(results)
    print(tests)

def start():
    origin_file = r"data\example_qc\ae_indep_qiskit_2.qasm"
    origin_qc = QuantumCircuit.from_qasm_file(origin_file)

    input_types = ['C',] #['C', 'Q']
    num_inputs = 2 #Number of possible inputs
    measurements = ['X', 'Y', 'Z'] #['X','Y','Z']

    output_type = 'State' #['Prob', 'Exp', 'State']
    shots = 1024
    environment = 'Sim' #['Sim', 'Real']


    run(origin_qc, input_types, num_inputs, measurements, output_type, shots, environment)


if __name__ == '__main__':
    start()

