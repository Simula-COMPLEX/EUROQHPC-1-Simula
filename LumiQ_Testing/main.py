from types import SimpleNamespace

import pandas as pd
import pathlib
import json

from qiskit import QuantumCircuit
from tqdm import tqdm

from circuit_preparation import prepare_circuits
from circuit_execution import execute_circuits, get_outputs


def run(origin_qc, input_types,num_inputs, measurements, output_type, shots, environment):
    
    circuits, tests = prepare_circuits(origin_qc, input_types, num_inputs, measurements, output_type)
    outputs = execute_circuits(circuits, shots, environment, output_type)
    results = get_outputs(circuits, outputs, output_type)


    return results, tests


def save_results(results, tests, results_path, origin_file):
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
    pathlib.Path(f'{results_path}{path_char}{origin_file_name}').mkdir(parents=True, exist_ok=True)
    df_results.to_csv(f"{results_path}{path_char}{origin_file_name}{path_char}execution_results.csv", index=False)
    df_tests.to_csv(f"{results_path}{path_char}{origin_file_name}{path_char}tests_used.csv", index=False)



def start():
    with open("config.json", "r") as f:
        config = json.load(f, object_hook=lambda d: SimpleNamespace(**d))


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
        results, tests = run(origin_qc, config.input_types, config.num_inputs, config.measurements, config.output_type, config.shots, config.environment)

        if config.verbose:
            print("--------------------------------------------------------------------")
            print(f"TC used in execution:")
            print(tests)
            print("--------------------------------------------------------------------")
            print(f"Results obtained from execution:")
            print(results)
            print("--------------------------------------------------------------------")

        if config.save:
            save_results(results, tests, config.results_path, origin_file)



if __name__ == '__main__':
    path_char = '\\'

    start()

