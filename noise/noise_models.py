from abc import ABC, abstractmethod

class Noise_model(ABC):
    @abstractmethod
    def noise_settings(self):
        """
        Abstract method to implement noise models.
        Subclasses must provide an implementation.
        """
        pass