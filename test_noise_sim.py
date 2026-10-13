from pathlib import Path

from NoiseModels import qiskit_noise_models

from qiskit import QuantumCircuit, qasm2
from qiskit.transpiler import generate_preset_pass_manager
from qiskit.primitives import StatevectorEstimator, BackendEstimatorV2
from qiskit.quantum_info import Pauli, SparsePauliOp

from qiskit_aer import AerSimulator
from qiskit_aer.primitives import EstimatorV2
from qiskit_ibm_runtime.fake_provider import FakeVigoV2, FakeGuadalupeV2

from qiskit.circuit.library import efficient_su2

from qiskit_aer.noise import NoiseModel, QuantumError, ReadoutError, depolarizing_error, pauli_error, thermal_relaxation_error

global_qc = qasm2.load("data/example_qc/bell.qasm")


def ideal_simulation(qc:QuantumCircuit):
    #calculate the expectation value using an ideal simulator
    num_qubits = qc.num_qubits
    observable = SparsePauliOp("Z"*num_qubits)
    params = [0.1]*qc.num_parameters

    estimator = StatevectorEstimator()

    pub = (qc, observable, params)
    job = estimator.run([pub])
    result = job.result()
    pub_result = result[0]
    ideal_value = float(pub_result.data.evs)

    return ideal_value

def test_noise_model_fake_backend(qc:QuantumCircuit):
    #calculate the expectation value using a noise model imported from a fake backend

    num_qubits = qc.num_qubits

    observable = SparsePauliOp("Z"*num_qubits)
    params = [0.1]*qc.num_parameters

    backend = FakeGuadalupeV2()
    noise_sim = AerSimulator.from_backend(backend)
    
    pm = generate_preset_pass_manager(3, backend)
    isa_qc = pm.run(qc)
    isa_observable = observable.apply_layout(isa_qc.layout)

    estimator = BackendEstimatorV2(backend=noise_sim)
    pub = (isa_qc, isa_observable, params)
    job = estimator.run([pub])

    result = job.result()
    pub_result = result[0]
    noisy_value = float(pub_result.data.evs)

    return noisy_value

def test_noise_model(qc:QuantumCircuit):
    #calculate the expectation value using a noise model defined by us
    #using Noise example 1 from https://quantum.cloud.ibm.com/docs/en/guides/build-noise-models

    #--START: noise model definition--
    #Error probabilities
    p_reset = 0.03
    p_meas = 0.1
    p_gate1 = 0.05

    #QuantumError objects
    error_reset = pauli_error([("X", p_reset), ("I", 1 - p_reset)])
    error_meas = pauli_error([("X", p_meas), ("I", 1 - p_meas)])
    error_gate1 = pauli_error([("X", p_gate1), ("I", 1 - p_gate1)])
    error_gate2 = error_gate1.tensor(error_gate1)

    #Add errors to noise model
    noise_bit_flip = NoiseModel()
    noise_bit_flip.add_all_qubit_quantum_error(error_reset, "reset")
    noise_bit_flip.add_all_qubit_quantum_error(error_meas, "measure")
    noise_bit_flip.add_all_qubit_quantum_error(error_gate1, ["u1","u2","u3"])
    noise_bit_flip.add_all_qubit_quantum_error(error_gate2, ["cx"])
    #--END: noise model definition--

    num_qubits = qc.num_qubits

    #Specification of the observables
    observable = SparsePauliOp("Z"*num_qubits)
    #Definition of the parameters of the quantum circuit (if the quantum circuit has parameters)
    params = [0.1]*qc.num_parameters

    #create noisy simulator backend
    noise_sim = AerSimulator(noise_model=noise_bit_flip)
    
    #Transpile circuit for noise basis gate
    pm = generate_preset_pass_manager(optimization_level=0, backend=noise_sim)
    isa_qc = pm.run(qc)
    isa_observable = observable.apply_layout(isa_qc.layout)

    #create an estimator
    estimator = BackendEstimatorV2(backend=noise_sim)

    # run and get the results
    pub = (isa_qc, isa_observable, params)
    job = estimator.run([pub])

    result = job.result()
    pub_result = result[0]
    noisy_value = float(pub_result.data.evs)

    return noisy_value


if __name__ == "__main__":
    a=ideal_simulation(global_qc)
    b=test_noise_model_fake_backend(global_qc)
    c=test_noise_model(global_qc)
    # a=ideal_simulation(efficient_su2(num_qubits=8))
    # b=test_noise_model_fake_backend(efficient_su2(num_qubits=8))
    # c=test_noise_model(efficient_su2(num_qubits=8))

    print(f"Ideal result: {a}")
    print(f"Noisy result (fake backend): {b}")
    print(f"Noisy result: {c}")


    
