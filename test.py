from gen_random_input import Gen_Random_Input
from Languages.qiskit_lang import qiskit_lang
from Languages.qrisp_lang import qrisp_lang
import pathlib
import json


from circuit_preparation import *

def test_gen_random_input(qasm_file, num_inputs, input_types):
    rand_circ = Gen_Random_Input(qasm_file, num_inputs, input_types)
    init_circ_qiskit, init_circ_str = rand_circ.createInputs()

    for k,v in init_circ_qiskit.items():
        print(k)
        print(init_circ_str[k])
        print()
        print(v)
        print()
        print("----------------------------------------------")  


def test_prefix_rand_inputs(qasm_file, num_inputs, input_types):
    circ_qiskit = qiskit_lang(qasm_file=qasm_file, num_inputs=num_inputs, input_types=input_types)
    qc=circ_qiskit.prefix_rand_inputs()

    for k,v in qc.items():
        print(k)
        print()
        print(v)
        print("----------------------------------------------")  

def test_append_meas(qasm_file, num_inputs, input_types, meas_basis, output_type):
    circ_qiskit = qiskit_lang(qasm_file=qasm_file, num_inputs=num_inputs, input_types=input_types, meas_basis=meas_basis, output_type=output_type)
    qc=circ_qiskit.prefix_rand_inputs() #dict
    dict_meas_circ = {}
    for k,v in qc.items():
        dict_meas_circ[k] = circ_qiskit.append_meas(v)

    for k,v in dict_meas_circ.items():
        print(k)
        print(v)

def test_prepare_circuits(qasm_file, num_inputs, input_types, meas_basis, output_type):
    # qisk = qiskit_lang(qasm_file=qasm_file, num_inputs=num_inputs, input_types=input_types, meas_basis=meas_basis, output_type=output_type)
    # circ_qiskit, tests = qisk.prepare_circuits()

    qrisp = qrisp_lang(qasm_file=qasm_file, num_inputs=num_inputs, input_types=input_types, meas_basis=meas_basis, output_type=output_type)
    circ_qrisp, tests = qrisp.prepare_circuits()

    for k,v in circ_qrisp.items():
        print(k)
        print(tests[k])
        print()
        print(v)
        print()
        print("----------------------------------------------")

def test_execute_circuits(qasm_file, num_inputs, input_types, meas_basis, output_type, shots, environment):
    qisk = qiskit_lang(qasm_file=qasm_file, num_inputs=num_inputs, input_types=input_types, meas_basis=meas_basis, output_type=output_type, environment=environment, shots=shots)
    
    circ_qiskit, _ = qisk.prepare_circuits()

    outputs = qisk.execute_circuits(circ_qiskit)

    print(outputs)

def test_get_outputs(qasm_file, num_inputs, input_types, meas_basis, output_type, shots, environment):
    qisk = qiskit_lang(qasm_file=qasm_file, num_inputs=num_inputs, input_types=input_types, meas_basis=meas_basis, environment=environment, output_type=output_type, shots=shots)
    
    circ_qiskit, _ = qisk.prepare_circuits()
    outputs = qisk.execute_circuits(circ_qiskit)
    results = qisk.get_outputs(circ_qiskit, outputs)

    for k,v in results.items():
        print(k)
        print(v)
        print("--------------------------------------")   
        

if __name__ == "__main__":
    qasm_file = pathlib.Path("./data/example_qc/vitor.qasm")
    config_file = pathlib.Path("./config.json")
    with open(config_file, "r") as f:
        config = json.load(f)
    num_inputs = config["num_inputs"]
    input_types = config["input_types"]
    meas_basis = config["measurements"]
    output_type = config["output_type"]
    shots = config["shots"]
    environment = config["environment"]
    project = config["PROJECT"]
    resoruce = config["RESOURCE"]

    #test_gen_random_input(qasm_file, num_inputs, input_types) #check
    #test_prefix_rand_inputs(qasm_file, num_inputs, input_types) #check
    #test_append_meas(qasm_file, num_inputs, input_types, meas_basis, output_type)
    # print("==========Vitor=============")
    test_prepare_circuits(qasm_file, num_inputs, input_types, meas_basis, output_type)
    # print("==========Vitor=============")

    # test_execute_circuits_sim(qasm_file, num_inputs, input_types, meas_basis, output_type, shots)
    #test_get_outputs(qasm_file, num_inputs, input_types, meas_basis, output_type, shots, environment)
    
    
    #qc=qasm2.load(qasm_file).remove_final_measurements(inplace=False)
    #input_circuits, inputs = createInputs(qc.num_qubits, input_types, num_inputs)
    
    # for k,v in input_circuits.items():
    #         print(k)
    #         print(inputs[k])
    #         print()
    #         print(v)
    #         print()
    #         print("----------------------------------------------")

    # initialized_qcs = initCircuits(qc, input_circuits)
    # for k,v in initialized_qcs.items():
    #         print(k)
    #         print()
    #         print(v)
    #         print("----------------------------------------------") 


    # circuits, tests = prepare_circuits(qc, input_types, num_inputs, meas_basis, output_type)
    # print("==========Enaut=============")
    # for k,v in circuits.items():
    #     print(k)
    #     print()
    #     print(tests[k])
    #     print()
    #     print(v)
    #     print("----------------------------------------------")
    # print("==========Enaut=============")
