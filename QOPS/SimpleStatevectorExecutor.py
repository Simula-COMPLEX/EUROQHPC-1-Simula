from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import SparsePauliOp, Statevector

from QOPS.abstract_classes import Executor


class SimpleStatevectorExecutor(Executor):
    def execute_test_cases(self, CUT: QuantumCircuit, test_cases: list[dict]) -> list[float]:
        # Transpile once per batch to match the simulator target.
        transpiled = transpile(CUT, optimization_level=1)
        statevec = Statevector.from_instruction(transpiled)

        results = []
        for pauli_dict in test_cases:
            pauli_op = SparsePauliOp.from_list(list(pauli_dict.items()))
            expectation = statevec.expectation_value(pauli_op).real
            results.append(expectation)
        return results