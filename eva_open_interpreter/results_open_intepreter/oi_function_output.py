import os
import subprocess


def save_output(task_path):
    for file in os.listdir(task_path):
        if file.endswith('.py') and file != "open-interpreter-test.py": #file.startswith('oi'):
            file_path = os.path.join(task_path, file)

            log_file_path = task_path + '/real_' + os.path.basename(file).replace('.py', '.log')
            with open(log_file_path, 'w') as log_file:
                try:
                    process = subprocess.Popen(
                        ['python3', file_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )

                    # catch stdout & stderr when timeout
                    stdout, stderr = process.communicate(timeout=30)

                    # write stdout & stderr to log file
                    log_file.write("Standard Output:\n")
                    log_file.write(stdout)
                    log_file.write("\nStandard Error:\n")
                    log_file.write(stderr)
                    log_file.write(f"\nReturn code: {process.returncode}\n")
                except subprocess.TimeoutExpired:
                    log_file.write("Error: Execution timed out\n")
                    process.kill()
                    outs, errs = process.communicate()  # get the remaining output
                    log_file.write("Standard Output:\n")
                    log_file.write(outs)
                    log_file.write("\nStandard Error:\n")
                    log_file.write(errs)
                except FileNotFoundError:
                    log_file.write(f"Error: File not found {file_path}\n")
                except Exception as e:
                    log_file.write(f"Unexpected error: {str(e)}\n")

            print(f'Executed {file}, output saved to {log_file_path}')


def main():
    ROOT_DIR = "."

    if not os.path.exists(ROOT_DIR):
        print(f"Directory '{ROOT_DIR}' does not exist.")
        return

    for task_folder in os.listdir(ROOT_DIR):
        if os.path.basename(task_folder) != 'temp':
            task_path = os.path.join(ROOT_DIR, task_folder)

            if os.path.isdir(task_path):
                task_name = os.path.basename(task_folder)
                print(f"Processing task: {task_name}")

                for subfolder in os.listdir(task_path):
                    subfolder_path = os.path.join(task_path, subfolder)

                    if os.path.isdir(subfolder_path):
                        save_output(subfolder_path)


if __name__ == '__main__':
    main()
