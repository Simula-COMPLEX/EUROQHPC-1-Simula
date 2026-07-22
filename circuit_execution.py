from qaas.client import QProvider, QBackend, QJob
from iqm.qiskit_iqm import  transpile_to_IQM


from qiskit import transpile

from qiskit_aer import AerSimulator
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator

def execute_circuits(circuits, shots, environment, output_type, token, project, resource):
    if environment == 'Sim':
        if output_type == 'Exp':
            results = {}
            estimator = StatevectorEstimator()

            for tc_name, circuit in circuits.items():
                obs = SparsePauliOp("Z"* circuit.num_qubits)

                # Run the job
                job = estimator.run([(circuit, obs)])
                result = job.result()[0].data.evs

                results[tc_name] = float(result)
        else:
            backend = AerSimulator(method='statevector')
            transpiled_circuits = transpile(list(circuits.values()), backend)
            results = backend.run(transpiled_circuits, shots=shots, seed_simulator=42).result()

    elif environment == 'VLQ':
        results = {}
        provider = QProvider(token, project)
        backend: QBackend = provider.get_backend(resource)
        # Transpile circuit
        for name, circuit in circuits.items():
            transpiled_circuit = transpile_to_IQM(circuit, backend)
            results[name] = backend.run(transpiled_circuit, shots=shots).result().get_counts()

    return results

def get_outputs(circuits, outputs, output_type):
    results = {}
    if output_type == 'State':
        for key, value in circuits.items():
            results[key] = outputs.get_statevector(value).data
    elif output_type == 'Exp':
        results = outputs

    else:
        for key, value in circuits.items():
            results[key] = outputs.get_counts(value)

    return results