from types import SimpleNamespace

import pandas as pd
import pathlib
import json

from qiskit import QuantumCircuit, qasm2
from tqdm import tqdm

from circuit_preparation import prepare_circuits
from circuit_execution import execute_circuits, get_outputs

from py4lexis.session import LexisSession

import argparse
from QOPS.Tester import Circuit_Tester
from QOPS.QiskitExecutor import Qiskit_Executor
from QOPS.SimpleStatevectorExecutor import SimpleStatevectorExecutor
#from QOPS.VLQExecutor import VLQ_Executor #to do 

from Languages.select_lang import get_language

#QuantumCircuit -> [Str] -> Int -> [Measurement_Basis] -> Str -> Int -> Str -> Str -> Str -> Str -> (Dict_Results, Dict_OpenQASM2)
def run(origin_qc, input_types,num_inputs, measurements, output_type, shots, environment, token, project, resource):

    circuits, tests = prepare_circuits(origin_qc, input_types, num_inputs, measurements, output_type)
    outputs = execute_circuits(circuits, shots, environment, output_type, token, project, resource)
    if environment == 'Sim':
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


def start(exec_qops):
    with open("config.json", "r") as f:
        config = json.load(f, object_hook=lambda d: SimpleNamespace(**d))

    if exec_qops:
            if config.environment == "VLQ":
                print("Not supported yet")

            else:
                path = pathlib.Path(config.origin_path) #path of the examples
                path_cps = pathlib.Path(config.QOPS.cps_path) #path for the cps files

                files_examples = []
                files_cps = []
                if path.is_file():
                    if path.file_extension == ".qasm":
                        files_examples.append(path)
                elif path.is_dir():
                    for file in path.glob("*.qasm"):
                        files_examples.append(file)
                else:
                    print("ERROR: Path does not exist or no .qasm file was found.")

                if path_cps.is_file():
                    if path_cps.file_extension == ".json":
                        files_cps.append(path_cps)
                elif path_cps.is_dir():
                    for file in path_cps.glob("*.json"):
                        files_cps.append(file)

                else:
                    print("ERROR: Path does not exist or no .json file was found.")

                for f_ex in files_examples:
                    for f_cps in files_cps:
                        if f_ex.stem == f_cps.stem:
                            print(f"({f_ex.name}, {f_cps.name})")
                            cut = qasm2.load(f_ex) #circuit without measurements
                            with open(str(f_cps), "r") as f:
                                cps = json.load(f) 
                            executor = Qiskit_Executor() #if config.environment=="Sim" else VLQ_Executor()
                            path_folder_result = pathlib.Path(config.results_path + "_QOPS")
                            path_folder_result.mkdir(parents=True, exist_ok=True)
                            path_result = pathlib.Path(path_folder_result,str(f_ex.stem)+".json")
                            print(path_result)
                            ct = Circuit_Tester(
                                CUT=cut,
                                CPS=cps,
                                executor=executor,
                                threshold=config.QOPS.threshold,
                                budget=config.QOPS.budget,
                                mode=config.QOPS.mode,
                                batch=config.QOPS.batch,
                                output=str(path_result)
                            )
                            result = ct.run_randomsearch()
                            print(result["Max Diff"])
                            print(result["Max Diff. Test Case"])
                            break
                            
    else:    
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
                if path.file_extension == ".qasm":
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
                    for k,v in tests.items():
                        #what is printed here are the initial states and the measurement bases; the quantum
                        #circuit sent to evaluation is not printed
                        r = results[k]
                        print(f"\n{k}:")
                        print(v)
                        print(f"Results obtained from execution:")
                        print(r)
                        print("--------------------------------------------------------------------")
                        print("\n")
            
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


def get_files(origin_path, file_extension):
    path = pathlib.Path(origin_path) #path of the examples
    files=[]
    if path.is_file():
        if path.file_extension == file_extension:
            files.append(path)
    elif path.is_dir():
        for file in path.glob("*"+file_extension):
            files.append(file)
    else:
        raise ValueError (f"ERROR: Path does not exist or no {file_extension} file was found.")

    return files

def start3(flag_qops):
    with open("config.json", "r") as f:
        config = json.load(f, object_hook=lambda d: SimpleNamespace(**d))

    qasm_files = get_files(config.origin_path, ".qasm")

    if flag_qops:
        cps_files = get_files(config.QOPS.cps_path, ".json")
        for f_ex in qasm_files:
            for f_cps in cps_files:
                if f_ex.stem == f_cps.stem:
                    print(f"({f_ex.name}, {f_cps.name})")
                    cut = qasm2.load(f_ex) #circuit without measurements
                    if 'measure' in cut.count_ops():
                        raise ValueError (f"ERROR: The circuit {f_ex} has measurements; Please remove the measurements from the circuit")
                    with open(str(f_cps), "r") as f:
                        cps = json.load(f) 
                    executor = Qiskit_Executor() #alter this line to choose a different executor
                    path_folder_result = pathlib.Path(config.results_path + "_QOPS")
                    path_folder_result.mkdir(parents=True, exist_ok=True)
                    path_result = pathlib.Path(path_folder_result,str(f_ex.stem)+".json")
                    ct = Circuit_Tester(
                        CUT=cut,
                        CPS=cps,
                        executor=executor,
                        threshold=config.QOPS.threshold,
                        budget=config.QOPS.budget,
                        mode=config.QOPS.mode,
                        batch=config.QOPS.batch,
                        output=str(path_result)
                    )
                    result = ct.run_randomsearch()
                    print(result["Max Diff"])
                    print(result["Max Diff. Test Case"])
                    print()
                    break
    else:
        for qasm_file in tqdm(qasm_files, desc="Executing .qasm files...."):
            lang = get_language(config.language, config, qasm_file)
            circuits, tests = lang.prepare_circuits()
            outputs = lang.execute_circuits(circuits)
            results = lang.get_outputs(circuits, outputs)

            if config.verbose:
                print("--------------------------------------------------------------------")
                print(f"TC used in execution:")
                for k,v in tests.items():
                    #what is printed here are the initial states and the measurement bases; the quantum
                    #circuit sent to evaluation is not printed
                    print(f"\n{k}:")
                    print(v)
                    print("\n")
                    print(f"Results obtained from execution:")
                    print(results[k])
                    print("--------------------------------------------------------------------")

            if config.save:
                save_results(results, tests, config.results_path, config.environment, qasm_file)    



if __name__ == '__main__':
    path_char = '/'

    parser = argparse.ArgumentParser(
        description=(
            "Test\n"
            "Run Enaut framework: python main.py"
            "Run QOPS: python main.py -q"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    #CLI arguments
    parser.add_argument(
        "--qops", "-q",
        action="store_true",
        help="If enabled, QOPS is executed"
    )

    args = parser.parse_args()
    flag_qops = args.qops
    
    #start(flag_qops)
    start3(flag_qops)

