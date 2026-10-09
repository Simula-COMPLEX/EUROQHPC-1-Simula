from gen_random_input import Gen_Random_Input

from qiskit import QuantumCircuit, qasm2, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator

#imports to run in VLQ
from qaas.client import QProvider, QBackend, QJob
from iqm.qiskit_iqm import  transpile_to_IQM
from py4lexis.session import LexisSession

from Languages.abstract_lang import Language

class qiskit_lang(Language):
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

        self.qc=qasm2.load(qasm_file).remove_final_measurements(inplace=False) #maps a qasm file into a qiskit QuantumCircuit 
        self.num_qubits=self.qc.num_qubits #number of qubits in the quantum circuit

    #load and prefix the randomly generated inputs
    def prefix_rand_inputs(self, input_circuits:dict)->dict:
        input_plus_circ = {}

        for k, v in input_circuits.items():
            input_plus_circ[k] = v.compose(self.qc)

        return input_plus_circ

    #---Prepare circuits---
    #append the measurements
    def append_meas(self, qc:QuantumCircuit, base:str)->QuantumCircuit:
        aux_qc = QuantumCircuit(qc.num_qubits)
        meas_qc = aux_qc.compose(qc)

        if base=='X':
            for q in meas_qc.qubits:
                meas_qc.h(q)
        elif base=='Y':
            for q in meas_qc.qubits:
                meas_qc.sdg(q)
                meas_qc.h(q)

        if self.output_type=="State":
            meas_qc.save_statevector()
        if self.output_type=="Prob":
            meas_qc.measure_all()

        return meas_qc

    #prepare the circuits for test
    def prepare_circuits(self)->tuple[dict,dict]:
        circ_qiskit = {}
        tests = {}

        #prepare the input random circuits
        input_circuits, inputs_str = Gen_Random_Input(self.qasm_file, self.num_inputs, self.input_types).createInputs()

        #prefix the input random circuits to the quantum circuit without measurements
        input_plus_circ = self.prefix_rand_inputs(input_circuits)

        #append measurements
        test_count=0
        for input_name, circ in input_plus_circ.items():
            for base in self.meas_basis:
                circ_qiskit["TestCase_" + str(test_count)] = self.append_meas(circ, base)
                tests["TestCase_" + str(test_count)] = inputs_str[input_name] + "_Base_" + base
                test_count+=1

        return circ_qiskit, tests

    #---Execute circuits---
    #Dict_QuantumCircuit -> Int -> Str -> Str -> Str -> Str -> Str -> Dict_Results
    def execute_circuits(self, circuits):
        if self.environment == 'Sim':
            if self.output_type == 'Exp':
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
                results = backend.run(transpiled_circuits, shots=self.shots, seed_simulator=42).result()

        elif self.environment == 'VLQ':
            results = {}

            #set output_type to "Prob"
            self.output_type="Prob"
            
            #set token
            lexis_session = LexisSession()
            self.token = lexis_session.get_access_token()
            
            provider = QProvider(self.token, self.project)
            backend: QBackend = provider.get_backend(self.resource)
            # Transpile circuit
            for name, circuit in circuits.items():
                transpiled_circuit = transpile_to_IQM(circuit, backend)
                results[name] = backend.run(transpiled_circuit, shots=self.shots).result().get_counts()

        return results

    #---Get outputs---
    #Dict_QuantumCircuit -> Dict_Results -> Str -> Dict_Results
    def get_outputs(self, circuits, outputs):
        results = {}
        if self.output_type == 'State':
            for key, value in circuits.items():
                results[key] = outputs.get_statevector(value).data
        elif self.output_type == 'Exp':
            results = outputs

        else:
            for key, value in circuits.items():
                results[key] = outputs.get_counts(value)

        return results
    



# class qiskit_prep:
#     """
#     Support for qiskit
#     Here we will do the following:
#     0. receive a qasm file and map it to a qiskit quantum circuit
#     1. prefix the generated random inputs to the quantum circuits to be evaluated
#     2. suffix the measurements to the quantum circuits created in the previous point 
#     3. execute the completed quantum circuits using either a qiskit simulator or VLQ (for the latter, think there are things to do yet)
#     """

#     def __init__(
#             self,
#             qasm_file: str, #path to the qasm file
#             input_types: list[str], #the type of inputs: U ⊆ ['C','Q']
#             num_inputs: int, #number of total inputs
#             meas_basis:list[str]=[], #measurement basis for testing: U ⊆ ["X", "Y", "Z"]
#             output_type:str="Prob", #indicates the type of output: x ∊ {"Prob", "State", "Exp"}
            
#     ):
#         self.qasm_file=qasm_file
#         self.input_types=input_types
#         self.num_inputs=num_inputs
#         self.meas_basis=meas_basis
#         self.output_type=output_type

#         self.qc=qasm2.load(qasm_file).remove_final_measurements(inplace=False) #maps a qasm file into a qiskit QuantumCircuit 
#         self.num_qubits=self.qc.num_qubits #number of qubits in the quantum circuit
       
#     #load and prefix the randomly generated inputs
#     def prefix_rand_inputs(self, input_circuits:dict)->dict:
#         input_plus_circ = {}

#         for k, v in input_circuits.items():
#             input_plus_circ[k] = v.compose(self.qc)

#         return input_plus_circ

#     #append the measurements
#     def append_meas(self, qc:QuantumCircuit, base:str)->QuantumCircuit:
#         aux_qc = QuantumCircuit(qc.num_qubits)
#         meas_qc = aux_qc.compose(qc)

#         if base=='X':
#             for q in meas_qc.qubits:
#                 meas_qc.h(q)
#         elif base=='Y':
#             for q in meas_qc.qubits:
#                 meas_qc.sdg(q)
#                 meas_qc.h(q)

#         if self.output_type=="State":
#             meas_qc.save_statevector()
#         if self.output_type=="Prob":
#             meas_qc.measure_all()

#         return meas_qc

#     #prepare the circuits for test
#     def prepare_circuits(self)->tuple[dict,dict]:
#         circ_qiskit = {}
#         tests = {}

#         #prepare the input random circuits
#         input_circuits, inputs_str = Gen_Random_Input(self.qasm_file, self.num_inputs, self.input_types).createInputs()

#         #prefix the input random circuits to the quantum circuit without measurements
#         input_plus_circ = self.prefix_rand_inputs(input_circuits)

#         #append measurements
#         test_count=0
#         for input_name, circ in input_plus_circ.items():
#             for base in self.meas_basis:
#                 circ_qiskit["TestCase_" + str(test_count)] = self.append_meas(circ, base)
#                 tests["TestCase_" + str(test_count)] = inputs_str[input_name] + "_Base_" + base
#                 test_count+=1

#         return circ_qiskit, tests



# class qiskit_exec:
#     """
#     A class for executing circuits
#     """
#     def __init__(
#             self,
#             environment:str, #Sim or VLQ
#             output_type:str="Prob", #indicates the type of output: x ∊ {"Prob", "State", "Exp"}
#             shots:int=1024, #number of shots
#             token:str=None, #token associated with VLQ
#             project:str=None, #project associated with VLQ
#             resource:str=None #resource id associated with VLQ
#     ):
#         self.environment=environment
#         self.output_type=output_type
#         self.shots=shots
#         self.token=token
#         self.project=project
#         self.resource=resource        

#     #Dict_QuantumCircuit -> Int -> Str -> Str -> Str -> Str -> Str -> Dict_Results
#     def execute_circuits(self, circuits):
#         if self.environment == 'Sim':
#             if self.output_type == 'Exp':
#                 results = {}
#                 estimator = StatevectorEstimator()

#                 for tc_name, circuit in circuits.items():
#                     obs = SparsePauliOp("Z"* circuit.num_qubits)

#                     # Run the job
#                     job = estimator.run([(circuit, obs)])
#                     result = job.result()[0].data.evs

#                     results[tc_name] = float(result)
#             else:
#                 backend = AerSimulator(method='statevector')
#                 transpiled_circuits = transpile(list(circuits.values()), backend)
#                 results = backend.run(transpiled_circuits, shots=self.shots, seed_simulator=42).result()

#         elif self.environment == 'VLQ':
#             results = {}

#             #set output_type to "Prob"
#             self.output_type="Prob"
            
#             #set token
#             lexis_session = LexisSession()
#             self.token = lexis_session.get_access_token()
            
#             provider = QProvider(self.token, self.project)
#             backend: QBackend = provider.get_backend(self.resource)
#             # Transpile circuit
#             for name, circuit in circuits.items():
#                 transpiled_circuit = transpile_to_IQM(circuit, backend)
#                 results[name] = backend.run(transpiled_circuit, shots=self.shots).result().get_counts()

#         return results

#     #Dict_QuantumCircuit -> Dict_Results -> Str -> Dict_Results
#     def get_outputs(self, circuits, outputs):
#         results = {}
#         if self.output_type == 'State':
#             for key, value in circuits.items():
#                 results[key] = outputs.get_statevector(value).data
#         elif self.output_type == 'Exp':
#             results = outputs

#         else:
#             for key, value in circuits.items():
#                 results[key] = outputs.get_counts(value)

#         return results    