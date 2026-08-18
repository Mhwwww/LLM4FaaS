import os
import subprocess
import time

TIMEOUT = 30
INTERVAL = 40

OPEN_INTERPRETER_PYTHON_VENV = '/Users/minghe/llm4faas/eva/scripts/open-interpreter/openinterpreter/bin/python3'
ROOT_DIR = '/Users/minghe/llm4faas/eva_open_interpreter/'


def run_script(script_path, log_file_path):
    script_dir = os.path.dirname(script_path)
    print(f"Move to DIR: {script_dir}")
    os.chdir(script_dir) 

    start_time = time.time_ns()
    with open(log_file_path, "w") as log_file:
        log_file.write(f"[{start_time}] Start Time - {script_path}\n")

    try:
        process = subprocess.Popen(
            [OPEN_INTERPRETER_PYTHON_VENV, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=TIMEOUT) 

        with open(log_file_path, "a") as log_file:
            log_file.write(f"\n[{end_time}] Standard Output:\n{stdout}\n")
            log_file.write(f"\n[{end_time}] Standard Error:\n{stderr}\n")
            log_file.write(f"\n[{end_time}] Return code: {process.returncode}\n\n")

        print(f"Finish running: {script_path}; Save logs to: {log_file_path}")

    except subprocess.TimeoutExpired:
        timeout_end_time = time.time_ns()

        stdout, stderr = process.communicate()

        with open(log_file_path, "a") as log_file:
            log_file.write(f"[{timeout_end_time}] Execution timed out - {script_path}\n")
            log_file.write(f"[{timeout_end_time}] Timeout Standard Output:\n{stdout}\n")
            log_file.write(f"\n[{timeout_end_time}] Timeout Standard Error:\n{stderr}\n\n")

    except Exception as e:
        error_end_time = time.time_ns()
        with open(log_file_path, "a") as log_file:
            log_file.write(f"[{error_end_time}] Other error in {script_path}: {str(e)}\n\n")


def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        if 'open-interpreter-test.py' in files:
            script_path = os.path.join(root, 'open-interpreter-test.py')
            log_file_path = os.path.join(root, 'logfile.txt')
            run_script(script_path, log_file_path)

        time.sleep(INTERVAL)


if __name__ == '__main__':
    main()
