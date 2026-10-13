from abc import ABC, abstractmethod

class AbsNoiseModel(ABC):
    @abstractmethod
    def noise_model(self):
        """
        Abstract method to implement/define noise models
        Subclasses must provide an implementation
        """
        pass