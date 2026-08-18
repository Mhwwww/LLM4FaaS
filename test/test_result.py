import os
import re
import csv
import logging
import colorlog

from test.function_directory import FOLDER_PATH

# task name
# TASK_NAME = 'auto_adapt'
# TASK_NAME = 'plan'
# TASK_NAME = 'energy_control'
# TASK_NAME = 'remote_control'

TASK_NAMES = ['auto_adapt', 'plan', 'energy_control', 'remote_control']

# log path of standard output AND generated functions
# STANDARD_LOG_PATH = f'/Users/minghe/llm4faas/test/standard_log/{TASK_NAME}'
# log path of
ACTUAL_LOG_PATH = FOLDER_PATH

# logging
LOGGING_LEVEL = logging.INFO

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)

log_format = "%(log_color)s%(asctime)s - %(levelname)s - %(message)s"

console_handler = colorlog.StreamHandler()
console_handler.setLevel(LOGGING_LEVEL)

formatter = colorlog.ColoredFormatter(log_format)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)


# Parse log file into Standard Output, Standard Error, and Return Code.
def parse_log_file(log_file_path):
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


# Update the function to handle multi-condition matching
def multi_condition_match(standard_line, actual_lines):
    # Split standard_line by '||' to handle multiple possible matches
    conditions = [cond.strip() for cond in standard_line.split('||')]
    return any(any(cond in actual_line for actual_line in actual_lines) for cond in conditions)


# Check actual log output against standard log and record the result.
def check_logs_with_standard(actual_log_path, standard_log_path, results):
    # todo: check if the prompt is valid before check the logs
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
    elif actual_return_code is None:#python
        status = "Timeout"
    else:
        status = f"Unexpected return code {actual_return_code}"
        logger.warning(f"{actual_log_path}: Unexpected return code {actual_return_code}")

    match_percentage = 0
    if status in {"No Error & Warning", "Warning Exists", "Timeout"}:
        actual_output_lines = actual_stdout.strip().splitlines()
        standard_output_lines = standard_stdout.strip().splitlines()

        matched_lines = [line for line in standard_output_lines if multi_condition_match(line, actual_output_lines)]
        unmatched_lines = [line for line in standard_output_lines if
                           not multi_condition_match(line, actual_output_lines)]

        matched_count = len(matched_lines)
        total_standard_lines = len(standard_output_lines)
        match_percentage = matched_count / total_standard_lines if total_standard_lines > 0 else 0

        if unmatched_lines:
            if any("Manual Check Required" in line for line in unmatched_lines):
                status = "Manual Check Required"
                unmatched_lines = None
                logger.info(f"{actual_log_path}: Manual Check Required")
            elif any("Invalid prompt" in line for line in unmatched_lines):
                status = "Invalid Prompt"
                unmatched_lines = None
                logger.info(f"{actual_log_path}: Invalid Prompt")
            else:
                match_percentage = matched_count / total_standard_lines if total_standard_lines > 0 else 0
                if status == "No Error & Warning":
                    logger.info(
                        f"{actual_log_path}: Matched {matched_count}/{total_standard_lines} lines ({match_percentage * 100:.2f}% match).")
                else:
                    logger.warning(
                        f"{actual_log_path}: status: {status}, Matched {matched_count}/{total_standard_lines} lines ({match_percentage * 100:.2f}% match).")
                for line in unmatched_lines:
                    logger.debug(line)
        else:
            # match_percentage = 1  # All lines matched
            logger.info(
                f"{actual_log_path}: Output contains all expected lines! Matched {matched_count}/{total_standard_lines} lines ({match_percentage * 100:.2f}% match).")

    results.append((actual_log_path, match_percentage, status, unmatched_lines))


# Write the analysis results to a CSV file.
def write_results_to_csv(results, output_csv_path):
    # sort the result based on task and index?
    with open(output_csv_path, 'w', newline='') as csvfile:
        fieldnames = ['Timestamp', 'Model Name', 'Task Name', 'User Answer Index', 'Success Rate (%)', 'Error Status',
                      'Unmatched Lines', 'Log File Path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for log_file_path, success_rate, status, unmatched_lines in results:
            filename = os.path.basename(log_file_path)
            model_name, user_answer_index, timestamp = extract_filename_details(filename, TASK_NAME)
            success_rate_str = f"{success_rate:.4f}" if success_rate is not None else "N/A"
            writer.writerow({
                'Timestamp': timestamp,
                'Model Name': model_name,
                'Task Name': TASK_NAME,
                'User Answer Index': user_answer_index,
                'Success Rate (%)': success_rate_str,
                'Error Status': status,
                'Log File Path': log_file_path,
                'Unmatched Lines': unmatched_lines
            })


def extract_filename_details(filename, basename):
    parts = re.split(basename, filename)
    # print(filename)
    # print(parts.__len__())
    metadata = re.split('[._]', parts[1])

    model_name = parts[0].rstrip('_')
    user_answer_index = metadata[1]
    timestamp = re.split('[._]', parts[1])[2]

    if timestamp == 'log':
        timestamp = None

    logger.debug(model_name, user_answer_index, timestamp, TASK_NAME)
    return model_name, user_answer_index, timestamp


if __name__ == '__main__':
    for TASK_NAME in TASK_NAMES:
        STANDARD_LOG_PATH = f'/Users/minghe/llm4faas/test/standard_log/{TASK_NAME}'

        actual_logs_path = ACTUAL_LOG_PATH
        standard_logs_path = STANDARD_LOG_PATH
        results = []

        for filename in os.listdir(actual_logs_path):
            if filename.__contains__(TASK_NAME) & filename.endswith('.log'):
                actual_log_path = os.path.join(actual_logs_path, filename)

                model_name, user_answer_index, timestamp = extract_filename_details(filename, TASK_NAME)

                core_filename = TASK_NAME + '_' + user_answer_index + '.log'
                standard_log_path = os.path.join(standard_logs_path, core_filename)

                if os.path.exists(standard_log_path):
                    check_logs_with_standard(actual_log_path, standard_log_path, results)
                else:
                    logger.debug(f"{actual_log_path}: Standard log file not found")  # for {filename}")
                    results.append((actual_log_path, None, "Standard log file not found", None))

        output_csv_path = os.path.join(actual_logs_path, TASK_NAME + '.csv')
        # output_csv_path = os.path.join(actual_logs_path, 'new_' + TASK_NAME + '.csv')
        write_results_to_csv(results, output_csv_path)
