from types import SimpleNamespace

import pandas as pd
import pathlib
import json

import argparse

import qiskit
from qiskit import QuantumCircuit, qasm3
from qiskit.quantum_info import Statevector, DensityMatrix
from tqdm import tqdm

from circuit_preparation import prepare_circuits
from circuit_execution import execute_circuits, get_outputs

from py4lexis.session import LexisSession

from QOPS.Tester import Circuit_Tester
from QOPS.QiskitExecutor import Qiskit_Executor

#pretty printing of quantum states
def from_state_vector_to_dirac(statevector):
    tol = 1e-10
    sv = Statevector(statevector)
    vector = sv.data
    
    num_qubits = sv.num_qubits
    terms = []
    
    for i in range(2**num_qubits):
            coefficient = vector[i]
    
            if abs(coefficient) < tol:
                continue
    
            ket = format(i, f"0{num_qubits}b")
    
            terms.append(
                f" ({coefficient:.4g})|{ket}⟩"
            )
    
    print(" + ".join(terms) if terms else "0")


#QuantumCircuit -> [Str] -> Int -> [Measurement_Basis] -> Str -> Int -> Str -> Str -> Str -> Str -> (Dict_Results, Dict_OpenQASM2)
def run(origin_qc, input_types,num_inputs, measurements, output_type, shots, environment, token, project, resource):

    circuits, tests = prepare_circuits(origin_qc, input_types, num_inputs, measurements, output_type, environment)
    outputs = execute_circuits(circuits, shots, environment, output_type, token, project, resource)
    if environment == 'Sim' or environment == 'Noisy':
        results = get_outputs(circuits, outputs, output_type)
    else:
        results = outputs

    return results, tests

#Dict_Results -> Dict_OpenQASM2 -> Str -> Str -> Str -> IO()
def save_results(results, tests, results_path, environment, origin_file):
    test_names = list(results.keys())
    result = list(results.values())

    # Create a DataFrame with one column for keys and one for values
    df_results = pd.DataFrame({
        "TestCase": test_names,
        "Result": result
    })

    test_names = list(tests.keys())
    test_content = list(tests.values())

    # Create a DataFrame with one column for keys and one for values
    df_tests = pd.DataFrame({
        "TestName": test_names,
        "Test": test_content
    })

    # Split Test column into two columns
    df_tests[["Input", "Measurement_Base"]] = df_tests["Test"].str.split("_Base_", expand=True)
    df_tests["Input"] = df_tests["Input"].str.replace("\n", "\\n")

    # Remove original column if no longer needed
    df_tests = df_tests.drop(columns=["Test"])

    # Save to CSV
    path = pathlib.Path(origin_file)
    origin_file_name = path.stem
    results_path = results_path + "_" + environment
    pathlib.Path(f"{results_path}{path_char}{origin_file_name}").mkdir(parents=True, exist_ok=True)
    df_results.to_csv(f"{results_path}{path_char}{origin_file_name}{path_char}execution_results.csv", index=False)
    df_tests.to_csv(f"{results_path}{path_char}{origin_file_name}{path_char}tests_used.csv", index=False)     


def start(args_qops):
    if args_qops.qops:
        config_qops_path = pathlib.Path("./tools/QOPS/config_QOPS.json")
        
        with open(config_qops_path, "r") as f:
            config_qops = json.load(f)

        cut = qasm3.load(config_qops["qasmfile"])
        with open(config_qops["cpsfile"], "r") as f:
            cps = json.load(f)

        executor = Qiskit_Executor()
        ct = Circuit_Tester(
            CUT=cut,
            CPS=cps,
            executor=executor,
            threshold=0.05,
            budget=50,
            mode='single',
            output=config_qops["output"]
        )

        result = ct.run_randomsearch()
        print(result["Max Diff"], result["Max Diff. Test Case"])
        
    else:  
        with open("config.json", "r") as f:
            config = json.load(f, object_hook=lambda d: SimpleNamespace(**d))

        if config.environment == 'VLQ':
            config.output_type = 'Prob'
            # Authentication
            lexis_session = LexisSession()
            token = lexis_session.get_access_token()
        else:
            token = None


        path = pathlib.Path(config.origin_path)


        files = []
        if path.is_file():
            # Process the single file
            if path.suffix == ".qasm":
                files.append(path)

        elif path.is_dir():
            # Iterate over all .qasm files in the folder
            for file in path.glob("*.qasm"):
                files.append(file)

        else:
            print("ERROR: Path does not exist or no .qasm file was found.")

        for origin_file in tqdm(files, desc="Executing .qasm files...."):
            origin_qc = QuantumCircuit.from_qasm_file(origin_file)
            if config.verbose:
                print("--------------------------------------------------------------------")
                print(f"Executing {origin_file}")
                print("--------------------------------------------------------------------")
            results, tests = run(origin_qc, config.input_types, config.num_inputs, config.measurements, config.output_type, config.shots, config.environment, token, config.PROJECT, config.RESOURCE)

            if config.verbose:
                print("--------------------------------------------------------------------")
                print(f"TC used in execution:")
                if config.output_type=="State":
                    for k,v in tests.items():
                        #what is printed here are the initial states and the measurement bases; the quantum
                        #circuit sent to evaluation is not printed
                        r = results[k]
                        print(f"\n{k}:")
                        print(v)
                        print("\n")
                        print(f"Results obtained from execution:")
                        print(from_state_vector_to_dirac(r))
                        print("--------------------------------------------------------------------")
                else:   
                    for k,v in tests.items():
                        #what is printed here are the initial states and the measurement bases; the quantum
                        #circuit sent to evaluation is not printed
                        r = results[k]
                        print(f"\n{k}:")
                        print(v)
                        print("\n")
                        print(f"Results obtained from execution:")
                        print(r)
                        print("--------------------------------------------------------------------")
            
            # if config.verbose:
            #     print("--------------------------------------------------------------------")
            #     print(f"TC used in execution:")
            #     print(tests)
            #     print("--------------------------------------------------------------------")
            #     print(f"Results obtained from execution:")
            #     print(results)
            #     print("--------------------------------------------------------------------")

            if config.save:
                save_results(results, tests, config.results_path, config.environment, origin_file)



if __name__ == '__main__':
    path_char = '/'

    parser = argparse.ArgumentParser(
        description=(
            "Test\n"
            "Run Random input circuits (Enaut): python main.py\n"
            "Run QOPS (Asmar): python main.py --qops\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    #CLI arguments
    parser.add_argument(
        "--qops",
        action="store_true",
        help="If enabled, QOPS is executed"
    )

    args_qops = parser.parse_args()
    
    start(args_qops)

