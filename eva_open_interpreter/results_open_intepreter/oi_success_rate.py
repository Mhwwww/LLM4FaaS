import csv
import logging
import os

LOGGING_LEVEL = logging.INFO

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)

log_format = "%(log_color)s%(asctime)s - %(levelname)s - %(message)s"

SUCCESS_RATE_CSV = 'oi_success_rate.csv'
# todo: check if the success rate of local running is the same as that from json response.
JSON_SUCCESS_RATE_CSV = 'oi_json_success_rate.csv'

invalid_tasks = {
    'energy_control': {'5', '14', '15', '16', '19'},
    'plan': {'6', '8', '14', '15'},
    'remote_control': {'5', '15', '16'}
}

STANDARD_LOG_PATH = f'/Users/minghe/llm4faas/test/standard_log/'


def parse_log_file(log_file_path):
    """parse the real_oi log file"""
    stdout, stderr, return_code = [], [], None
    current_section = None

    with open(log_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line == 'Standard Output:':
                current_section = 'stdout'
            elif line == 'Standard Error:':
                current_section = 'stderr'
            elif line.startswith('Return code:'):
                try:
                    return_code = int(line.split('Return code:')[1].strip())
                except ValueError:
                    return_code = None
            elif current_section == 'stdout':
                stdout.append(line)
            elif current_section == 'stderr':
                stderr.append(line)

    return '\n'.join(stdout), '\n'.join(stderr), return_code


def multi_condition_match(standard_line, actual_lines):
    """Split standard_line by '||' to handle multiple possible matches"""
    conditions = [cond.strip() for cond in standard_line.split('||')]
    return any(any(cond in actual_line for actual_line in actual_lines) for cond in conditions)


def check_logs_with_standard(task_path, task_name, index):
    """compare the experiment log file with the standard one."""

    match_percentage = 0.0000
    standard_log_path = os.path.join(STANDARD_LOG_PATH, task_name, f"{task_name}_{index}.log")

    #  check if the prompt is valid before check the logs
    if task_name in invalid_tasks and index in invalid_tasks[task_name]:
        status = "Invalid Prompt"
        return status, f"{match_percentage:.4f}", []

    if not any(f.endswith('.log') for f in os.listdir(task_path)):
        # print(f"Log file does not exist under {task_path}.")
        return 'Error', f"{match_percentage:.4f}", []
    else:
        for f in os.listdir(task_path):
            if f.startswith('real_'):
            # if f.startswith('oi_'):
                actual_log_path = os.path.join(task_path, f)
                break

    actual_stdout, actual_stderr, actual_return_code = parse_log_file(actual_log_path)

    standard_stdout, _, _ = parse_log_file(standard_log_path)
    status = ''
    unmatched_lines = None

    if actual_return_code == 1:
        status = "Error"
        logger.error(f"{actual_log_path}: Error detected with return code 1")
        logger.debug(f"Standard Error:\n{actual_stderr}")
    elif actual_stderr:
        status = "Warning Exists"
    elif actual_return_code == 0:
        status = "No Error & Warning"
    elif actual_return_code is None:
        status = "Timeout"
    else:
        status = f"Unexpected return code {actual_return_code}"
        logger.warning(f"{actual_log_path}: Unexpected return code {actual_return_code}")

    if status in {"No Error & Warning", "Warning Exists", "Timeout"}:
        actual_output_lines = actual_stdout.strip().splitlines()
        standard_output_lines = standard_stdout.strip().splitlines()

        matched_lines = [line for line in standard_output_lines if multi_condition_match(line, actual_output_lines)]
        unmatched_lines = [line for line in standard_output_lines if
                           not multi_condition_match(line, actual_output_lines)]

        matched_count = len(matched_lines)
        total_standard_lines = len(standard_output_lines)
        match_percentage = matched_count / total_standard_lines if total_standard_lines > 0 else f"{match_percentage:.4f}"

        if unmatched_lines:
            if any("Manual Check Required" in line for line in unmatched_lines):
                status = "Manual Check Required"
                unmatched_lines = []
                logger.info(f"{actual_log_path}: Manual Check Required")
            else:
                match_percentage = matched_count / total_standard_lines if total_standard_lines > 0 else 0
                if status == "No Error & Warning":
                    logger.info(
                        f"{actual_log_path}: Matched {matched_count}/{total_standard_lines} lines ({match_percentage * 100:.4f}% match).")
                else:
                    logger.warning(
                        f"{actual_log_path}: status: {status}, Matched {matched_count}/{total_standard_lines} lines ({match_percentage * 100:.4f}% match).")
                for line in unmatched_lines:
                    logger.debug(line)
        else:
            # match_percentage = 1  # All lines matched
            logger.info(
                f"{actual_log_path}: Output contains all expected lines! Matched {matched_count}/{total_standard_lines} lines ({match_percentage * 100:.4f}% match).")
    match_percentage = f"{match_percentage:.4f}"

    return status, match_percentage, unmatched_lines


def main():
    ROOT_DIR = "."

    if not os.path.exists(ROOT_DIR):
        print(f"Directory '{ROOT_DIR}' does not exist.")
        return

    data = []

    for task_folder in os.listdir(ROOT_DIR):
        if os.path.basename(task_folder) != 'temp':
            task_path = os.path.join(ROOT_DIR, task_folder)
            if os.path.isdir(task_path):
                task_name = os.path.basename(task_folder)
                print(f"Task Name: {task_name}")
                for sub_folder in os.listdir(task_path):
                    sub_folder_path = os.path.join(task_path, sub_folder)
                    if os.path.isdir(sub_folder_path):
                        index = os.path.basename(sub_folder).strip(task_name + "_")
                        print(index)
                        error_status, success_rate, unmatched_lines = check_logs_with_standard(sub_folder_path,
                                                                                               task_name, index)

                        data.append([task_name, index, error_status, success_rate, unmatched_lines])

    with open(SUCCESS_RATE_CSV, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["TASK_NAME", "INDEX", "ERROR_STATUS", "SUCCESS RATE(%)", "UNMATCHED_LINES"])
        writer.writerows(data)

    print(f"Results saved to {SUCCESS_RATE_CSV}")


if __name__ == '__main__':
    main()
