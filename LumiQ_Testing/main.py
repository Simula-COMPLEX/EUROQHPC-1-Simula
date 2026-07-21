import pandas as pd
import pathlib

from qiskit import QuantumCircuit

from circuit_preparation import prepare_circuits
from circuit_execution import execute_circuits, get_outputs


def run(origin_qc, input_types,num_inputs, measurements, output_type, shots, environment):
    
    circuits, tests = prepare_circuits(origin_qc, input_types, num_inputs, measurements, output_type)
    outputs = execute_circuits(circuits, shots, environment)
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
    tests = list(tests.values())

    # Create a DataFrame with one column for keys and one for values
    df_tests = pd.DataFrame({
        "TestName": test_names,
        "Test": tests
    })

    # Save to CSV
    path = pathlib.Path(origin_file)
    origin_file_name = path.stem
    pathlib.Path(f'{results_path}{path_char}{origin_file_name}').mkdir(parents=True, exist_ok=True)
    df_results.to_csv(f"{results_path}{path_char}{origin_file_name}{path_char}execution_results.csv", index=False)
    df_tests.to_csv(f"{results_path}{path_char}{origin_file_name}{path_char}tests_used.csv", index=False)


def start():
    origin_file = r"data\example_qc\ghz_indep_qiskit_2.qasm"
    origin_qc = QuantumCircuit.from_qasm_file(origin_file)

    input_types = ['C', 'Q'] #['C', 'Q']
    num_inputs = 4 #Number of possible inputs
    measurements = ['X', 'Y', 'Z'] #['X','Y','Z']

    output_type = 'Prob' #['Prob', 'Exp', 'State']
    shots = 1024
    environment = 'Sim' #['Sim', 'Real']

    save = False
    verbose = True
    results_path = r"data\results"

    if verbose:
        print("--------------------------------------------------------------------")
        print(f"Executing {origin_file}")
        print("--------------------------------------------------------------------")
    results, tests = run(origin_qc, input_types, num_inputs, measurements, output_type, shots, environment)

    if verbose:
        print("--------------------------------------------------------------------")
        print(f"TC used in execution:")
        print(tests)
        print("--------------------------------------------------------------------")
        print(f"Results obtained from execution:")
        print(results)
        print("--------------------------------------------------------------------")

    if save:
        save_results(results, tests, results_path, origin_file)



if __name__ == '__main__':
    path_char = '\\'

    start()

