import pathlib, json
from qiskit import qasm3 

from QOPS.Tester import Circuit_Tester
from QOPS.QiskitExecutor import Qiskit_Executor
from tools.QOPS.executors import FakePerth_Executor, depolarizing_Executor

def select_tool(cli_args):
    if cli_args.qops:
        config_qops_path = pathlib.Path("./tools/QOPS/config_QOPS.json")
        
        with open(config_qops_path, "r") as f:
            config_qops = json.load(f)
        
        cut = qasm3.load(config_qops["qasmfile"])
        with open(config_qops["cpsfile"], "r") as f:
            cps = json.load(f)
        
        executor = depolarizing_Executor() #FakePerth_Executor() #Qiskit_Executor()
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
        ValueError("At the moment no more tools are integrated")