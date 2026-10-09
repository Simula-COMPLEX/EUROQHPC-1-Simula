from Languages.abstract_lang import Language

from gen_random_input import Gen_Random_Input

from qrisp import QuantumCircuit


class qrisp_lang(Language):
    def __init__(
            self,
            qasm_file: str, #path to the qasm file
            input_types: list[str], #the type of inputs: U ⊆ ['C','Q']
            num_inputs: int, #number of total inputs
            meas_basis:list[str]=[], #measurement basis for testing: U ⊆ ["X", "Y", "Z"]
            environment:str="Sim", #Sim or VLQ
            output_type:str="Prob", #indicates the type of output: x ∊ {"Prob", "State", "Exp"}
            shots:int=1024, #number of shots
            token:str=None, #token associated with VLQ
            project:str=None, #project associated with VLQ
            resource:str=None #resource id associated with VLQ
            ):
        self.qasm_file=qasm_file
        self.input_types=input_types
        self.num_inputs=num_inputs
        self.meas_basis=meas_basis
        self.environment=environment
        self.output_type=output_type
        self.shots=shots
        self.token=token
        self.project=project
        self.resource=resource

    #---Prepare circuits---
    def prepare_circuits(self):
        circ_qrisp = {}
        tests = {}

        #prepare the input random circuits to the quantum circuit without measurements
        #input_circuits are Qiskit circuits (it is necessary to map them to Qrisp quantum circuits)
        input_circuits_qiskit, inputs_str = Gen_Random_Input(self.qasm_file, self.num_inputs, self.input_types).createInputs()

        #this should give a Qrisp quantum circuit
        input_circuits = QuantumCircuit.from_qiskit(input_circuits_qiskit)

        return super().prepare_circuits()

    #---Execute circuits---
    def execute_circuits(self, circuits):
        return super().execute_circuits(circuits)

    #---Get outputs---
    def get_outputs(self, circuits, outputs):
        return super().get_outputs(circuits, outputs)