from QOPS.abstract_classes import Executor

from qiskit import generate_preset_pass_manager, QuantumCircuit
from qiskit.primitives import BackendEstimatorV2
from qiskit_ibm_runtime.estimator import EstimatorV2 as Estimator
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import Session, EstimatorOptions
from qiskit_ibm_runtime.fake_provider import FakePerth

from noise.depolarizing import depolarizing_model

class FakePerth_Executor(Executor):
    def __init__(self):
        self.backend = FakePerth()
        self.aer_sim = AerSimulator.from_backend(backend=self.backend)
        self.pass_manager = generate_preset_pass_manager(backend=self.backend, optimization_level=3)
        self.shots = 10000

    def execute_test_cases(self, CUT:QuantumCircuit, test_cases:list[dict]):
        pubs = []
        for test_case in test_cases:
            cut = CUT.copy()
            isa_qc = self.pass_manager.run(cut)
            sp = [(k, v) for k, v in test_case.items()]
            M1 = SparsePauliOp.from_list(sp)
            isa_observables = M1.apply_layout(isa_qc.layout)
            pubs.append((isa_qc, isa_observables))

        with Session(backend=self.aer_sim) as session:
            estimator = Estimator(mode=session, options=EstimatorOptions(default_shots=self.shots))
            results = estimator.run(pubs).result()

        return [x.data.evs for x in results]


class depolarizing_Executor(Executor):
    def __init__(self):
        self.noise_sim = AerSimulator(noise_model=depolarizing_model().noise_settings())
        self.pm = generate_preset_pass_manager(optimization_level=3, backend=self.noise_sim)
        self.shots=10000

    def execute_test_cases(self, CUT:QuantumCircuit, test_cases:list[dict]):
        pubs = []
        for test_case in test_cases:
            cut = CUT.copy()
            isa_qc = self.pm.run(cut)
            sp = [(k, v) for k, v in test_case.items()]
            M1 = SparsePauliOp.from_list(sp)
            isa_observables = M1.apply_layout(isa_qc.layout)
            pubs.append((isa_qc, isa_observables))

        with Session(backend=self.noise_sim) as session:
            estimator = Estimator(mode=session, options=EstimatorOptions(default_shots=self.shots))
            results = estimator.run(pubs).result()

        return [x.data.evs for x in results]