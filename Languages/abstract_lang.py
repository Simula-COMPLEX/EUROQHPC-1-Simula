from abc import ABC, abstractmethod

class Language(ABC):
    @abstractmethod
    def prepare_circuits(self):
        """
        Abstract method to prepare circuits
        Subclasses must provide an implementation
        """
        pass

    @abstractmethod
    def execute_circuits(self, circuits):
        """
        Abstract method to execute circuits
        Subclasses must provide an implementation
        """
        pass

    @abstractmethod
    def get_outputs(self, circuits, outputs):
        """
        Abstract method to get outputs
        Subclasses must provide an implementation
        """
        pass    
