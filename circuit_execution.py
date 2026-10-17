from qaas.client import QProvider, QBackend, QJob
from iqm.qiskit_iqm import  transpile_to_IQM


from qiskit import transpile, generate_preset_pass_manager

from qiskit_aer import AerSimulator
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator

#imports for introducing noisy simulation
from qiskit.primitives import BackendEstimatorV2
from qiskit_ibm_runtime.fake_provider import FakeCasablancaV2 #7qubits



#Dict_QuantumCircuit -> Int -> Str -> Str -> Str -> Str -> Str -> Dict_Results
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

    elif environment == 'Noisy':
        backend = FakeCasablancaV2() #change backend here
        noise_sim = AerSimulator.from_backend(backend=backend)
        pm = generate_preset_pass_manager(
            optimization_level=0,
            backend=backend,
            seed_transpiler=42
        )
        results = {}
        if output_type == 'Exp':
            estimator = BackendEstimatorV2(backend=noise_sim)
            for tc_name, circuit in circuits.items():
                obs = SparsePauliOp("Z"*circuit.num_qubits)
                transpiled_qc = pm.run(circuit)
                transpiled_obs = obs.apply_layout(transpiled_qc.layout)

                pub = (transpiled_qc, transpiled_obs)
                job = estimator.run([pub])
                result = job.result()[0].data.evs

                results[tc_name] = float(result)
        else:
            noise_sim.set_options(method="statevector")
            transpiled_circuits = pm.run(list(circuits.values()))
            for qc in transpiled_circuits:
                qc.save_statevector()
            results = noise_sim.run(transpiled_circuits, shots=shots).result()


    elif environment == 'VLQ':
        results = {}
        provider = QProvider(token, project)
        backend: QBackend = provider.get_backend(resource)
        # Transpile circuit
        for name, circuit in circuits.items():
            transpiled_circuit = transpile_to_IQM(circuit, backend)
            results[name] = backend.run(transpiled_circuit, shots=shots).result().get_counts()

    return results

#Dict_QuantumCircuit -> Dict_Results -> Str -> Dict_Results
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
