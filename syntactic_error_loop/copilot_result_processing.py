import json
import os
from syntactic_error_loop.error_loop_existing_results import execute_python_file, log_result_to_csv

LANGUAGE = 'zh'
# LANGUAGE = 'en'
OUTPUT_CSV_PATH = f'./{LANGUAGE}/copilot_existing_results_duration.csv'


def copilot_result_checking(filename):
    name, ext = os.path.splitext(filename)
    if not name.startswith("copilot_"):
        return None

    name_body = name[len("copilot_"):]
    parts = name_body.split('_')

    # find the number from right to left
    nums = [i for i, part in enumerate(reversed(parts)) if part.isdigit()]

    if not nums:
        return None  # No task_id

    if len(nums) == 1:
        # only task_id
        task_id = parts[-1]
        iteration_id = 1
        task_name = '_'.join(parts[:-1])
    else:
        # both task_id and iteration_id
        task_id = parts[-2]
        iteration_id = int(parts[-1])
        task_name = '_'.join(parts[:-2])

    task_name = task_name.replace('-', '_') #change
    base_name = f"{task_name}_{task_id}"

    # print(f"{filename}, Task Name: {task_name}, Task ID: {task_id}, Iteration ID: {iteration_id}")

    file_path = os.path.join(copilot_zh_dir, filename) if LANGUAGE == 'zh' else os.path.join(copilot_en_dir, filename)
    error = execute_python_file(file_path)
    if error:
        error_status = "error"
        print(f"******* Error found:\n{error} *******")

        log_result_to_csv(OUTPUT_CSV_PATH, 'copilot', base_name, iteration_id, 0, 0, None,
                          error_status, json.dumps(error))

    else:
        error_status = "fixed"
        log_result_to_csv(OUTPUT_CSV_PATH, 'copilot', base_name, iteration_id, 0, 0, None,
                          error_status)
        print(f"{filename}: Error fixed at the {iteration_id} iteration.")


if __name__ == '__main__':
    copilot_zh_dir = '/Users/minghe/llm4faas/syntactic_error_loop/test_output/zh/copilot'
    copilot_en_dir = '/Users/minghe/llm4faas/syntactic_error_loop/test_output/en/copilot'

    copilot_dir = copilot_zh_dir if LANGUAGE == 'zh' else copilot_en_dir


    for filename in os.listdir(copilot_dir):
        copilot_result_checking(filename)