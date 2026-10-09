from Languages.qiskit_lang import qiskit_lang

def get_language(language, config, qasm_file):
    language = language.strip().lower()

    if language=="qiskit":
        return qiskit_lang(
            qasm_file=qasm_file,
            input_types=config.input_types,
            num_inputs=config.num_inputs,
            meas_basis=config.measurements,
            environment=config.environment,
            output_type=config.output_type,
            shots=config.shots,
            project=config.PROJECT,
            resource=config.RESOURCE
        )

    raise ValueError(f"Unsupported language: {language}")