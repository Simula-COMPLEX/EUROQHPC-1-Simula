
from qiskit import transpile

# from quantum_input_generator.line import Circuit
# from quantum_input_generator.mutators import UCNOTMutator
from qiskit_aer import AerSimulator

def execute_circuits(circuits, shots, environment):
    if environment == 'Sim':
        backend = AerSimulator(method='statevector')
        new_circuits = transpile(list(circuits.values()), backend)
        results = backend.run(new_circuits, shots=shots, seed_simulator=42).result()

    elif environment == 'VLQ':
        pass

    return results

def get_outputs(circuits, outputs, output_type):
    results = {}
    if output_type == 'Prob':
        for key, value in circuits.items():
            results[key] = outputs.get_counts(value)
    else:
        for key, value in circuits.items():
            results[key] = outputs.get_statevector(value)

    return results