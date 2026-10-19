# Import from Qiskit Aer noise module
from qiskit_aer.noise import (
    NoiseModel,
    QuantumError,
    ReadoutError,
    depolarizing_error,
    pauli_error,
    thermal_relaxation_error,
)

#---Create a depolarizing noise model, which is applied to all qubits, under the abstract class Noise_model
#---this was taken from https://quantum.cloud.ibm.com/docs/en/guides/build-noise-models
class depolarizing_model():
    def noise_settings(self):
        #create an empty noise model
        self.noise_model = NoiseModel()

        #add depolarizing error to all single qubit u1, u2, u3 gates
        self.error = depolarizing_error(0.05, 1) 
        self.noise_model.add_all_qubit_quantum_error(self.error, ["u1", "u2", "u3"])

        #prints the informations of the noise model
        #print(self.noise_model)
        
        return self.noise_model
