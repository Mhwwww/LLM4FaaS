import os
import subprocess
from test.function_directory import FOLDER_PATHS

TIMEOUT = 30
# folder path where the generated functions are stored
# folder_path = FOLDER_PATH
# folder_paths = FOLDER_PATHS

# zh
# model_names = ['gpt-4o', 'gpt-4o-mini', 'gemini-1.5-flash', 'deepseek-r1:7b', 'qwen-max', 'copilot']
# tasks = ['auto_adapt', 'energy_control', 'plan', 'remote_control']
# tasks = ['auto-adapt', 'energy', 'plan', 'remote_control'] #copilot

# en
model_names = ['gpt-4o', 'gpt-4o-mini', 'gemini-1.5-flash', 'copilot']
tasks = ['auto_adapt', 'energy_control', 'plan', 'remote_control']
# tasks = ['auto-adapt', 'energy', 'plan', 'remote-control'] #copilot

# def get_function_output():
#     for folder_path in FOLDER_PATHS:
#         print(f'!!!!!Executing functions in {folder_path}!!!')
#         # Iterate through all generated function files in the folder
#         for filename in os.listdir(folder_path):
#             if filename.endswith('.py'):
#                 # full path of the file
#                 file_path = os.path.join(folder_path, filename)
#
#                 # save to .log
#                 log_file_path = os.path.join(folder_path, filename.replace('.py', '.log'))
#
#                 with open(log_file_path, 'w') as log_file:
#                     try:
#                         # start subprocess and catch stdout & stderr
#                         process = subprocess.Popen(
#                             ['python3', file_path],
#                             stdout=subprocess.PIPE,
#                             stderr=subprocess.PIPE,
#                             text=True
#                         )
#
#                         # catch stdout & stderr when timeout
#                         stdout, stderr = process.communicate(timeout=TIMEOUT)
#
#                         # write stdout & stderr to log file
#                         log_file.write("Standard Output:\n")
#                         log_file.write(stdout)
#                         log_file.write("\nStandard Error:\n")
#                         log_file.write(stderr)
#                         log_file.write(f"\nReturn code: {process.returncode}\n")
#
#                     except subprocess.TimeoutExpired:
#                         log_file.write("Error: Execution timed out\n")
#                         process.kill()
#                         outs, errs = process.communicate()  # get the remaining output
#                         log_file.write("Standard Output:\n")
#                         log_file.write(outs)
#                         log_file.write("\nStandard Error:\n")
#                         log_file.write(errs)
#                     except FileNotFoundError:
#                         log_file.write(f"Error: File not found {file_path}\n")
#                     except Exception as e:
#                         log_file.write(f"Unexpected error: {str(e)}\n")
#
#                 print(f'Executed {filename}, output saved to {log_file_path}')


def get_function_output(filename, folder_path):

    if filename.__contains__('auto-adapt'):
        log_file_name = filename.replace('auto-adapt', 'auto_adapt')
    elif filename.__contains__('energy') and not filename.__contains__('energy_control'):
        log_file_name = filename.replace('energy', 'energy_control')
    elif filename.__contains__('remote-control'):
        log_file_name = filename.replace('remote-control', 'remote_control')
    else:
        log_file_name = filename

    # full path of the file
    file_path = os.path.join(folder_path, filename)
    # save to .log
    log_file_path = os.path.join(folder_path, log_file_name.replace('.py', '.log'))

    with open(log_file_path, 'w') as log_file:
        try:
            # start subprocess and catch stdout & stderr
            process = subprocess.Popen(
                ['python3', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # catch stdout & stderr when timeout
            stdout, stderr = process.communicate(timeout=TIMEOUT)

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

    print(f'Executed {filename}, output saved to {log_file_path}')


def syn_error_get_function_output(folder_path):
    print(f'!!!!!Executing functions in {folder_path}!!!')
    # 存储 key: (model_name, task_name, task_id) → value: (iteration_id, filename)
    latest_files = {}

    for filename in os.listdir(folder_path):
        if not filename.endswith('.py'):
            continue

        filename_no_ext = os.path.splitext(filename)[0]
        for task in tasks:
            if task in filename_no_ext:
                try:
                    # 提取各部分
                    task_name = task
                    parts = filename_no_ext.split(task_name)
                    model_name = parts[0].replace("_", "")
                    rest = parts[1].split('_')
                    task_id = rest[1]
                    if len(rest) < 3:
                        iteration_id = 1
                    else:
                        iteration_id = int(rest[2]) 

                    key = (model_name, task_name, task_id)
                    # print(model_name)

                    if key not in latest_files or iteration_id > latest_files[key][0]:
                        latest_files[key] = (iteration_id, filename)

                except Exception as e:
                    print(f"Failed to parse {filename}: {e}")

    print(len(latest_files))

    for key, (iteration_id, filename) in latest_files.items():
        print(f"Executing {filename}")
        # model_name, task_name, task_id = key
        # print(f"Model: {model_name}, Task: {task_name}, Task ID: {task_id}, Iteration ID: {iteration_id}")
        get_function_output(filename, folder_path)

    return latest_files


if __name__ == '__main__':
    # get_function_output()

    for folder_path in FOLDER_PATHS:
        syn_error_get_function_output(folder_path)
