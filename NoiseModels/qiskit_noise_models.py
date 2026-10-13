from NoiseModels.abstract_noise_models import AbsNoiseModel

from qiskit_aer import AerSimulator
#from qiskit_noise_models import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeTorino

class FakeTorinoNoiseModel(AbsNoiseModel):
    def noise_model(self):
        #choose the backend
        self.backend = FakeTorino()
        #set the backend as a simulator (it has included noise)
        self.backend_simulator = AerSimulator.from_backend(self.backend)

        return self.backend, self.backend_simulator
    