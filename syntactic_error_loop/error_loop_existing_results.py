import csv
import json
import os
import re
import subprocess
import time
import uuid

from openai import OpenAI
import openai
import google.generativeai as genai

from eva.scripts.model_setting import MAX_TOKENS, TEMPERATURE, OPENAI_MODEL, SYSTEM_PROMPT, OLLAMA_MODEL, OLLAMA_URL, \
    GEMINI_MODEL
from test.test_result import parse_log_file

genai.configure(api_key='', )
openai.api_key = ''
tongyi_api_key = ''
# qianfan_openai_api_key = ''

ZH_ERROR_CSV_PATH = '../eva/_results_csv/zh_all_model_errors.csv'
EN_ERROR_CSV_PATH = '../eva/_results_csv/en_all_model_errors.csv'

LANGUAGE = 'zh'  # 'zh' or 'en'
# LANGUAGE = 'en'  # 'zh' or 'en'

TASK_NAMES = ['remote_control', 'plan', 'auto_adapt', 'energy_control']

MAX_ITERATIONS = 3
ERROR_PROMPT = "Please fix the code based on the following error messages and provide the updated, complete version:\n"

MODEL = OPENAI_MODEL
# MODEL = OLLAMA_MODEL# deepseek
# MODEL = 'gemini-1.5-flash'
# MODEL = 'qwen-max'
# MODEL = 'copilot' # manual experiments

RESULT_CSV_FILE_PATH = f'./test_output/{LANGUAGE}/{MODEL}_existing_results_duration.csv'


def construct_copilot_error_prompt(log_file_path):
    md_file_path, python_file_path = get_md_python_paths(log_file_path)

    test_output_dir = f'./copilot_prompt/{LANGUAGE}'
    if not os.path.exists(test_output_dir):
        os.makedirs(test_output_dir)

    test_output_path = os.path.join(test_output_dir,
                                    os.path.basename(python_file_path).replace('.py', '_error_prompt.md'))

    print(f"Executing error fix loop for: {md_file_path} <--> {python_file_path}")

    markdown_content = read_markdown(md_file_path)
    prompt = f"{markdown_content}"

    error_msg = get_error_msg(log_file_path)
    print(f" ******* Error detected while running {log_file_path}: {error_msg} *******")
    python_code = read_python_file(python_file_path)

    constructed_prompt = f"""You gave answer based on the md file content:\n{markdown_content}\n\nYour answered is:\n{python_code}\n\nSome errors occured when running the code you provided. {ERROR_PROMPT}{error_msg}\n
                            """
    save_python_code(constructed_prompt, test_output_path)
    #     todo: also create an empty python file with the same name.
    python_file_name = os.path.basename(test_output_path).replace('_error_prompt.md', '.py')
    python_file_path = os.path.join(test_output_dir, python_file_name)
    with open(python_file_path, 'w', encoding='utf-8') as file:
        file.write("")


def call_llm_openai(messages):
    print(f"Calling Model: {MODEL}")
    # save timestamp to CSV
    start_time = time.time_ns()

    response = openai.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )

    end_time = time.time_ns()
    print(f'duration: {(end_time - start_time) / 1e6} ms')

    response_content = response.choices[0].message.content.strip()
    return response_content, response.to_dict(), start_time, end_time


def call_llm_ollama(messages):
    print(f"Calling Model: {MODEL}")
    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='ollama')

    start_time = time.time_ns()
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages
    )
    end_time = time.time_ns()

    print(f'duration: {(end_time - start_time) / 1e6} ms')

    response_content = response.choices[0].message.content.strip()
    return response_content, response.to_dict(), start_time, end_time


def call_llm_qwen(messages):
    print(f"Calling Model: {MODEL}")
    client = OpenAI(
        api_key=tongyi_api_key,
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    )
    start_time = time.time_ns()
    response = client.chat.completions.create(
        model='qwen-max',
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    end_time = time.time_ns()

    print(f'duration: {(end_time - start_time) / 1e6} ms')

    response_content = response.choices[0].message.content.strip()
    return response_content, response.to_dict(), start_time, end_time


def call_llm_qianfan(messages):
    print(f"Calling Model: {MODEL}")

    client = OpenAI(
        api_key=qianfan_openai_api_key,
        base_url="https://qianfan.baidubce.com/v2",
    )

    start_time = time.time_ns()

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )

    end_time = time.time_ns()
    print(f'duration: {(end_time - start_time) / 1e6} ms')

    response_content = response.choices[0].message.content.strip()
    return response_content, response.to_dict(), start_time, end_time


def call_llm_gemini(messages):
    print(f"Calling Model: {GEMINI_MODEL}")

    generation_config = {
        'temperature': TEMPERATURE,
        'max_output_tokens': MAX_TOKENS,
    }

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        generation_config=generation_config,
        system_instruction="You are a helpful assistant."
    )

    start_time = time.time_ns()

    response = model.generate_content(
        contents=messages,
    )

    end_time = time.time_ns()

    full_response = response.to_dict()
    print(f'duration: {(end_time - start_time) / 1e6} ms')

    return response.text, full_response, start_time, end_time


def execute_python_file(file_path):
    """
    Execute a Python file, and return (None if success, error message if failure)
    """
    try:
        result = subprocess.run(
            ["python3", file_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return None
        else:
            return result.stderr
    except Exception as e:
        # return str(e)
        # timeout
        print(f"Exception occurred while executing {file_path}: {e}")
        return None


def code_extration(response_content):
    start_index = response_content.find('```python')
    end_index = response_content.find('```', start_index + len('```python'))

    if start_index != -1 and end_index != -1:
        context = response_content[:start_index].strip()
        code = response_content[start_index + len('```python'):end_index].strip()
        context_as_comment = '\n'.join(f"# {line}" for line in context.split('\n'))
        full_code = f"{context_as_comment}\n\n{code}"
    else:
        full_code = '\n'.join(f"# {line}" for line in response_content.split('\n'))

    return full_code


def save_python_code(code, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(code)


def read_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def read_python_file(file_path):
    if file_path.endswith('.py'):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    return ""


def log_result_to_csv(csv_file_path, model_name, base_name, iteration_id, start_time, end_time, inference_id,
                      error_status, error_msgs=None):
    # convert to milliseconds
    duration = (end_time - start_time) / 1e6
    header = ['model_name', 'task_name', 'iteration_id', 'start_time',
              'end_time', 'duration(ms)', 'inference_id',
              'error_status', 'error_msgs']

    if not os.path.exists(csv_file_path):
        with open(csv_file_path, 'w', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)

    with open(csv_file_path, 'a', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([model_name, base_name, iteration_id, start_time,
                         end_time, duration, inference_id,
                         error_status, error_msgs])


def extract_error_cases(csv_path):
    """
    extract the error cases from csv files
    :param csv_path:
    :return: a list of error cases (log file paths)
    """
    error_cases = []

    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            log_path = row.get('Log File Path')
            if log_path:
                error_cases.append(log_path)

        print(f"Found {len(error_cases)} error cases in {os.path.basename(csv_path)}")

    return error_cases


def get_error_msg(log_file_path):
    """
    # check error case's log file to get the error msg/timeout
    :param log_path:
    :return: error messages
    """
    actual_stdout, actual_stderr, actual_return_code = parse_log_file(log_file_path)

    # return '\n'.join(stdout), '\n'.join(stderr), return_code
    if actual_stderr:
        # print(actual_stderr)
        return actual_stderr
    elif actual_return_code is None:
        print(os.path.basename(log_file_path) + ": Execution timed out")
        return 'Execution timed out'
    elif actual_stderr is not None and actual_stderr.strip() == '':
        # nothing showing in the log file. either no function generated, or the function cannot be triggered.
        print(os.path.basename(log_file_path))
        return 'The generated Python file does not control any smart home devices.'
    else:
        return None


def interactive_error_loop_existing(log_file_path, output_dir):
    md_file_path, python_file_path = get_md_python_paths(log_file_path)

    print(f"Executing error fix loop for: {md_file_path} <--> {python_file_path}")
    markdown_content = read_markdown(md_file_path)
    prompt = f"{markdown_content}"

    error_msg = get_error_msg(log_file_path)

    print(f" ******* Error detected while running {log_file_path}: {error_msg} *******")

    # get generated python file path using md_file_path and model_name
    python_code = read_python_file(python_file_path)

    inference_id = str(uuid.uuid4())
    iteration_id = 1

    # todo: the history is too long for Qianfan model, even only for the first round.
    # append error message to messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": python_code},
        {"role": "user", "content": f"{ERROR_PROMPT}{error_msg}\n"}
    ]

    while iteration_id <= MAX_ITERATIONS:
        print(f"-------------Iteration {iteration_id} starts-------------")
        if MODEL == OPENAI_MODEL:
            response_content, full_response, start_time, end_time = call_llm_openai(messages)
        elif MODEL == 'gemini-1.5-flash':
            response_content, full_response, start_time, end_time = call_llm_ollama(messages)
        elif MODEL == 'qwen-max':
            response_content, full_response, start_time, end_time = call_llm_qwen(messages)
        # elif MODEL == QIANFAN_MODEL:
        #     response_content, full_response, start_time, end_time = call_llm_qianfan(messages)
        else:
            print('Unsupported model. Please check the MODEL variable.')

        python_code = code_extration(response_content)

        base_name = os.path.basename(md_file_path).replace('.md', '')
        python_name = f"{MODEL}_{base_name}_{iteration_id}_{inference_id}.py"
        full_response_name = f"{MODEL}_{base_name}_{iteration_id}_{inference_id}.md"

        python_file = os.path.join(output_dir, python_name)
        full_response_file = os.path.join(output_dir, full_response_name)

        full_response_with_msg = {
            "messages": messages,
            "full_response": full_response
        }

        # save files
        save_python_code(python_code, python_file)
        save_python_code(json.dumps(full_response_with_msg, indent=2, ensure_ascii=False), full_response_file)

        print(f"Saved iteration files: {python_name} / {full_response_name}")

        error = execute_python_file(python_file)

        if error:
            error_status = "error"
            print(f"******* Error found:\n{error} *******")

            # append error message to messages
            messages.append({"role": "assistant", "content": python_code})
            messages.append({"role": "user", "content": f"{ERROR_PROMPT}{error}\n"})

            log_result_to_csv(RESULT_CSV_FILE_PATH, MODEL, base_name, iteration_id, start_time, end_time, inference_id,
                              error_status, json.dumps(error))
            iteration_id += 1

        else:
            error_status = "fixed"
            log_result_to_csv(RESULT_CSV_FILE_PATH, MODEL, base_name, iteration_id, start_time, end_time, inference_id,
                              error_status)
            # print("Code executed without errors reported.")
            print(f"Error fixed at the {iteration_id} iteration.")
            break


def interactive_error_loop_existing_gemini(log_file_path, output_dir):
    md_file_path, python_file_path = get_md_python_paths(log_file_path)

    print(f"Executing error fix loop for: {md_file_path} <--> {python_file_path}")
    markdown_content = read_markdown(md_file_path)
    prompt = f"{markdown_content}"

    error_msg = get_error_msg(log_file_path)

    print(f" ******* Error detected while running {log_file_path}: {error_msg} *******")

    # get generated python file path using md_file_path and model_name
    python_code = read_python_file(python_file_path)

    inference_id = str(uuid.uuid4())
    iteration_id = 1

    # append error message to messages
    messages = [
        {"role": "user", "parts": [prompt]},
        {"role": "model", "parts": [python_code]},
        {"role": "user", "parts": [f"{ERROR_PROMPT}{error_msg}\n"]}
    ]

    while iteration_id <= MAX_ITERATIONS:
        print(f"-------------Iteration {iteration_id} starts-------------")
        # todo: determine method to call according to MODEL
        response_content, full_response, start_time, end_time = call_llm_gemini(messages)
        python_code = code_extration(response_content)

        base_name = os.path.basename(md_file_path).replace('.md', '')
        python_name = f"{MODEL}_{base_name}_{iteration_id}_{inference_id}.py"
        full_response_name = f"{MODEL}_{base_name}_{iteration_id}_{inference_id}.md"

        python_file = os.path.join(output_dir, python_name)
        full_response_file = os.path.join(output_dir, full_response_name)

        full_response_with_msg = {
            "messages": messages,
            "full_response": full_response
        }

        # save files
        save_python_code(python_code, python_file)
        save_python_code(json.dumps(full_response_with_msg, indent=2, ensure_ascii=False), full_response_file)

        print(f"Saved iteration files: {python_name} / {full_response_name}")

        error = execute_python_file(python_file)

        if error:
            error_status = "error"
            print(f"******* Error found:\n{error} *******")

            # append error message to messages
            messages.append({"role": "model", "parts": [python_code]})
            messages.append({"role": "user", "parts": [f"{ERROR_PROMPT}{error_msg}\n"]})

            log_result_to_csv(RESULT_CSV_FILE_PATH, MODEL, base_name, iteration_id, start_time, end_time, inference_id,
                              error_status, json.dumps(error))
            iteration_id += 1

        else:
            error_status = "fixed"
            log_result_to_csv(RESULT_CSV_FILE_PATH, MODEL, base_name, iteration_id, start_time, end_time, inference_id,
                              error_status)
            # print("Code executed without errors reported.")
            print(f"Error fixed at the {iteration_id} iteration.")
            break


def error_case_validation(error_cases):
    error_count = 0
    timeout_count = 0
    nothing_count = 0

    for case in error_cases:
        error_msg = get_error_msg(case)

        if error_msg:
            if error_msg == 'Execution timed out':
                timeout_count += 1
            elif error_msg == 'The generated Python file does not control any smart home devices.':
                nothing_count += 1
            else:
                error_count += 1

    # print(f"Total error cases in Chinese: {len(error_cases)}")
    print(f"Timeout cases: {timeout_count}")
    print(f"Nothing cases: {nothing_count}")
    print(f"Other error cases: {error_count}")
    print(f"In total: {timeout_count + nothing_count + error_count} error cases found.")


def get_md_python_paths(log_file_path):
    # /Users/minghe/llm4faas/experiments_default/functions_zh/deepseek-r1-functions/deepseek-r1:7b_energy_control_24_1738513047477170000.log
    md_file_path = ''
    log_file_name = os.path.basename(log_file_path)
    task_with_id = ''
    task = ''

    python_file_path = log_file_path.replace('.log', '.py')

    if MODEL == 'copilot':
        if 'auto_adapt' in python_file_path:
            python_file_path = python_file_path.replace('auto_adapt', 'auto-adapt')
        elif 'remote_control' in python_file_path:  # comment out this check when Language is ZH
            python_file_path = python_file_path.replace('remote_control', 'remote-control')
        elif 'energy_control' in python_file_path:
            python_file_path = python_file_path.replace('energy_control', 'energy')

    print(python_file_path)

    for task_name in TASK_NAMES:
        if log_file_name.__contains__(task_name):
            task = task_name
            match = re.search(rf'{task_name}_(\d+)', log_file_name)
            if match:
                task_with_id = f"{task_name}_{match.group(1)}.md"
                # print(task_with_id)

    if LANGUAGE == 'zh':
        md_file_path = os.path.join('/Users/minghe/llm4faas/experiments_default/logs_questionnaire_in_Chinese', task,
                                    task_with_id)
        # print(md_file_path)
    elif LANGUAGE == 'en':
        md_file_path = os.path.join('/Users/minghe/llm4faas/experiments_default/logs_questionnaire_in_English', task,
                                    task_with_id)
    else:
        print("Unexpected")

    return md_file_path, python_file_path


def rerun_qwen_energy_2(log_file_path, output_dir):
    md_file_path, python_file_path = get_md_python_paths(log_file_path)

    print(f"Executing error fix loop for: {md_file_path} <--> {python_file_path}")
    markdown_content = read_markdown(md_file_path)
    prompt = f"{markdown_content}"

    error_msg = get_error_msg(log_file_path)

    print(f" ******* Error detected while running {log_file_path}: {error_msg} *******")

    # get generated python file path using md_file_path and model_name
    python_code = read_python_file(python_file_path)

    # todo: 2nd round function and error msgs
    new_error_msg = """/Actuator/AC/LivingRoom/1 is turned on.
/Actuator/Window/LivingRoom/1 is turned off.
/Actuator/Window/LivingRoom/2 is turned off.
Cannot Get Sensor Reading, /Sensor/IndoorTemperature/LivingRoom/1 is Currently OFF. 
2025-07-15 15:52:08,339 - sensor.py - get_reading - WARNING - '/Sensor/IndoorTemperature/LivingRoom/1' is currently OFF. Cannot get reading.
Traceback (most recent call last):
File "/Users/minghe/llm4faas/syntactic_error_loop/test_output/zh/qwen-max/qwen-max_energy_control_2_1_b6df8b17-e3f3-425d-af97-a25e43c495ef.py", line 84, in <module>
	main()
File "/Users/minghe/llm4faas/syntactic_error_loop/test_output/zh/qwen-max/qwen-max_energy_control_2_1_b6df8b17-e3f3-425d-af97-a25e43c495ef.py", line 74, in main
	handle_ac_and_window(room.name)
File "/Users/minghe/llm4faas/syntactic_error_loop/test_output/zh/qwen-max/qwen-max_energy_control_2_1_b6df8b17-e3f3-425d-af97-a25e43c495ef.py", line 41, in handle_ac_and_window
	if temp_sensor.get_reading() < 20:
TypeError: '<' not supported between instances of 'NoneType' and 'int'

Process finished with exit code 1
    """

    new_python_file = '/Users/minghe/llm4faas/syntactic_error_loop/test_output/zh/qwen-max/qwen-max_energy_control_2_1_b6df8b17-e3f3-425d-af97-a25e43c495ef.py'
    new_python_code = read_python_file(new_python_file)

    inference_id = str(uuid.uuid4())
    iteration_id = 2

    # append error message to messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": python_code},
        {"role": "user", "content": f"{ERROR_PROMPT}{error_msg}\n"},
        {"role": "assistant", "content": new_python_code},
        {"role": "user", "content": f"{ERROR_PROMPT}{new_error_msg}\n"}
    ]

    while iteration_id <= MAX_ITERATIONS:
        print(f"-------------Iteration {iteration_id} starts-------------")

        response_content, full_response, start_time, end_time = call_llm_qwen(messages)

        python_code = code_extration(response_content)

        base_name = os.path.basename(md_file_path).replace('.md', '')
        python_name = f"{MODEL}_{base_name}_{iteration_id}_{inference_id}.py"
        full_response_name = f"{MODEL}_{base_name}_{iteration_id}_{inference_id}.md"

        python_file = os.path.join(output_dir, python_name)
        full_response_file = os.path.join(output_dir, full_response_name)

        full_response_with_msg = {
            "messages": messages,
            "full_response": full_response
        }

        # save files
        save_python_code(python_code, python_file)
        save_python_code(json.dumps(full_response_with_msg, indent=2, ensure_ascii=False), full_response_file)

        print(f"Saved iteration files: {python_name} / {full_response_name}")

        error = execute_python_file(python_file)

        if error:
            error_status = "error"
            print(f"******* Error found:\n{error} *******")

            # append error message to messages
            messages.append({"role": "assistant", "content": python_code})
            messages.append({"role": "user", "content": f"{ERROR_PROMPT}{error}\n"})

            log_result_to_csv(RESULT_CSV_FILE_PATH, MODEL, base_name, iteration_id, start_time, end_time, inference_id,
                              error_status, json.dumps(error))
            iteration_id += 1

        else:
            error_status = "fixed"
            log_result_to_csv(RESULT_CSV_FILE_PATH, MODEL, base_name, iteration_id, start_time, end_time, inference_id,
                              error_status)
            # print("Code executed without errors reported.")
            print(f"Error fixed at the {iteration_id} iteration.")
            break


def rerun_gpt4o_rc_9(log_file_path, output_dir):
    md_file_path, python_file_path = get_md_python_paths(log_file_path)

    print(f"Executing error fix loop for: {md_file_path} <--> {python_file_path}")

    # todo: 2nd round function and error msgs
    new_error_msg = 'The generated Python file does not control any smart home devices.'

    new_python_file = '/Users/minghe/llm4faas/syntactic_error_loop/test_output/zh/gpt-4o/gpt-4o_remote_control_9_2_0fecd7b7-67c9-4bd7-ac94-53d47f61bdcc.py'
    new_python_code = read_python_file(new_python_file)

    # todo: the history is too long for Qianfan model, even for the first round.
    # append error message to messages
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "# Preparation\nHi, I want you to provide me a 'function.py' file for my current smart home project based on my given functional description.\n\nFour code files in my project, i.e., sensor.py, actuator.py, home_plan.py and config.py, are in the 'home' folder. \nThe required 'function.py' should locate in the 'functions' folder, function.py should contain main function.\n\nI will first give you the functional description, then give you the 4 python source code.\n\n# Functional Description\n嗨，我想让我的空调温度调高到26度°\n嗨，我想让我的电视音量提高三度\n嗨，我想加温电水壶烧开到100度。\n\n\n# Source Code\n## sensor.py\n```python\nimport random\nfrom home.logger_config import logger\n\nclass Sensor:\n    sensor_count = {}  # Dictionary to keep track of sensor count for each room and sensor type\n\n    def __init__(self, sensor_type, room_name):\n        if room_name not in Sensor.sensor_count:\n            Sensor.sensor_count[room_name] = {}  # Initialize sensor count for the room if not already present\n        if sensor_type not in Sensor.sensor_count[room_name]:\n            Sensor.sensor_count[room_name][\n                sensor_type] = 0  # Initialize sensor count for the sensor type if not already present\n\n        Sensor.sensor_count[room_name][sensor_type] += 1  # Increment sensor count for the sensor type in the room\n\n        self.id = f\"/Sensor/{sensor_type}/{room_name}/{Sensor.sensor_count[room_name][sensor_type]}\"\n        self.sensor_type = sensor_type\n        self.room_name = room_name\n        self.status = \"off\"\n\n    def turn_on(self):\n        self.status = \"on\"\n        print(f\"'{self.id}' is now {self.status.upper()}.\")\n        logger.info(format(\"\\'\" + self.id + \"\\' is turned \" + self.status.upper()))\n\n    def turn_off(self):\n        self.status = \"off\"\n        print(f\"{self.id} is now OFF.\")\n        logger.info(format(\"\\'\" + self.id + \"\\' is turned \" + self.status.upper()))\n\n    def get_reading(self):\n        if self.status == \"off\":\n            print(f\"Cannot Get Sensor Reading, {self.id} is Currently OFF. \")\n            logger.warning(format(\"\\'\" + self.id + \"\\' is currently OFF. Cannot get reading.\"))\n            return None\n        elif self.status == \"on\":\n            reading = self._generate_reading()\n            print(f\"{self.id} reading is: {reading}\")\n            logger.info(format(\"\\'\" + self.id + \"\\' Reading is: \" + str(reading)))\n            return reading\n        else:\n            logger.error(format(\"\\'\" + self.id + \"\\' is in error status.\"))\n            print(f\"Status Error with status: {self.status}\")\n\n    def get_status(self):\n        print(f\"{self.id} current status is: {self.status}\")\n        logger.info(format(\"\\'\" + self.id + \"\\' CURRENT STATUS is: \" + self.status.upper()))\n        return self.status\n\n    def _generate_reading(self):\n        raise NotImplementedError(\"Subclasses must implement _generate_reading method.\")\n\n\nclass IndoorTemperatureSensor(Sensor):\n    def __init__(self, room_name):\n        super().__init__(\"IndoorTemperature\", room_name)\n\n    def _generate_reading(self):\n        return round(random.uniform(10, 40), 2)\n\n\nclass OutdoorTemperatureSensor(Sensor):\n    def __init__(self, room_name):\n        super().__init__(\"OutdoorTemperature\", room_name)\n\n    def _generate_reading(self):\n        return round(random.uniform(-10, 40), 2)\n\n\nclass HumiditySensor(Sensor):\n    def __init__(self, room_name):\n        super().__init__(\"Humidity\", room_name)\n\n    def _generate_reading(self):\n        return round(random.uniform(0, 100), 2)\n\n\nclass LightIntensiveSensor(Sensor):\n    def __init__(self, room_name):\n        super().__init__(\"LightIntensive\", room_name)\n\n    def _generate_reading(self):\n        return round(random.uniform(900, 1000), 2)\n\n\nclass SmokeSensor(Sensor):\n    def __init__(self, room_name):\n        super().__init__(\"Smoke\", room_name)\n\n    def _generate_reading(self):\n        return round(random.uniform(0, 100), 2)\n\n\nif __name__ == \"__main__\":\n    # pass\n\n    uv_sensor = LightIntensiveSensor(\"test\")\n    uv_sensor.turn_on()\n    uv_sensor.get_status()\n    print(uv_sensor.get_reading())\n    uv_sensor.turn_off()\n    print(uv_sensor.get_reading())\n\n    outdoor_temp_sensor = OutdoorTemperatureSensor(\"test\")\n    outdoor_temp_sensor.turn_on()\n    print(outdoor_temp_sensor.get_reading())\n```\n\n## actuator.py\n```python\nimport random\nimport time\nfrom home.logger_config import logger\n\nfrom home.config import DAILY_ROUTINE_DURATION\n\nclass Actuator:\n    actuator_count = {}  # Dictionary to keep track of sensor count for each room and sensor type\n\n    def __init__(self, actuator_type, room_name):\n        if room_name not in Actuator.actuator_count:\n            Actuator.actuator_count[room_name] = {}  # Initialize sensor count for the room if not already present\n        if actuator_type not in Actuator.actuator_count[room_name]:\n            Actuator.actuator_count[room_name][\n                actuator_type] = 0  # Initialize sensor count for the sensor type if not already present\n\n        Actuator.actuator_count[room_name][actuator_type] += 1  # Increment sensor count for the sensor type in the room\n\n        self.id = f\"/Actuator/{actuator_type}/{room_name}/{Actuator.actuator_count[room_name][actuator_type]}\"\n        self.actuator_type = actuator_type\n        self.room_name = room_name\n        self.status = \"off\"\n\n    def turn_on(self):\n        self.status = \"on\"\n        print(f\"{self.id} is now {self.status}.\")\n        logger.info(format(\"\\'\" + self.id + \"\\' is turned \" + self.status.upper()))\n\n    def turn_off(self):\n        self.status = \"off\"\n        print(f\"{self.id} is now {self.status}.\")\n        logger.info(format(\"\\'\" + self.id + \"\\' is turned \" + self.status.upper()))\n\n    def get_status(self):\n        print(f\"{self.id} current status is {self.status}\")\n        logger.info(format(\"\\'\" + self.id + \"\\' CURRENT STATUS is: \" + self.status.upper()))\n        return self.status\n\n\nclass Heater(Actuator):\n    def __init__(self, room_name):\n        super().__init__(\"Heater\", room_name)\n        self.target_temperature = None\n\n    def set_target_temperature(self, target_temperature):\n        self.target_temperature = target_temperature\n        logger.info(format(f\"Set the target temperature of {self.id} to {self.target_temperature}°C.\"))\n        print(f\"Set the target temperature of {self.id} to {self.target_temperature}°C.\")\n\n    def adjust_temperature(self, current_temperature):\n        if self.target_temperature is not None:\n            if current_temperature < self.target_temperature:\n                self.turn_on()\n            else:\n                self.turn_off()\n\nclass AC(Actuator):\n    def __init__(self, room_name):\n        super().__init__(\"AC\", room_name)\n        self.target_temperature = None\n\n    def set_target_temperature(self, target_temperature):\n        self.target_temperature = target_temperature\n        logger.info(format(f\"Set the target temperature of {self.id} to {self.target_temperature}°C.\"))\n        print(f\"Set the target temperature of {self.id} to {self.target_temperature}°C.\")\n\n    def adjust_temperature(self, current_temperature):\n        if self.target_temperature is not None:\n            if current_temperature > self.target_temperature:\n                self.turn_on()\n            else:\n                self.turn_off()\n\n\nclass CoffeeMachine(Actuator):\n    def __init__(self, room_name):\n        super().__init__(\"CoffeeMachine\", room_name)\n\n    def make_coffee(self, coffee_type):\n        if self.status == \"on\":\n            logger.info(format(self.id + \"Start making \" + coffee_type))\n        elif self.status == \"off\":\n            print(f\" {self.id} is OFF now\")\n            logger.warning(format(\"\\' \" + self.id + \" \\'\" + \" is OFF now, Need to Turn it On First.\"))\n            # self.turn_on()\n            # self.make_coffee(coffee_type)\n        else:\n            logger.error(\"There is Some Error with the Coffee Machine\" + self.id + \".\")\n            print(\"There is Some Error with the Coffee Machine\" + self.id + \".\")\n\n\nclass Window(Actuator):\n    def __init__(self, room_name):\n        super().__init__(\"Window\", room_name)\n\n\nclass Door(Actuator):\n    def __init__(self, room_name):\n        super().__init__(\"Door\", room_name)\n\n    def lock(self):\n        logger.info(format(\"Lock the door\" + self.id + \".\"))\n        print(f\"Lock the door {self.id}.\")\n\n    def unlock(self):\n        logger.info(format(\"Unlock the door\" + self.id + \".\"))\n        print(f\"Unlock the door {self.id}.\")\n\n\nclass Curtain(Actuator):\n    def __init__(self, room_name):\n        super().__init__(\"Curtain\", room_name)\n\n\nclass CleaningRobot(Actuator):\n    def __init__(self, room_name):\n        super().__init__(\"CleaningRobot\", room_name)\n\n    def daily_routine(self):\n        if self.status == \"off\":\n            logger.warning(format(\"Cleaning Robot \" + self.id + \" is OFF now, Need to Turn it ON First\"))\n            print(\"Cleaning Robot \" + self.id + \" is OFF now, Need to Turn it ON First\")\n        elif self.status == \"on\":\n            logger.info(format(\"Cleaning Robot \" + self.id + \" Starts Daily Cleaning Routine\"))\n            print(f\"Cleaning Robot {self.id} Starts Daily Cleaning Routine\")\n            time.sleep(DAILY_ROUTINE_DURATION)\n            logger.info(format(f\"{self.id} Finish Daily Cleaning Routine, Will Turn it OFF\"))\n            print(f\"{self.id} Finish Daily Cleaning Routine, Will Turn it OFF\")\n            self.turn_off()\n        else:\n            logger.error(\"There is Some Error with the Cleaning Robot\" + self.id + \".\")\n            print(f\"There is Some Error with the Cleaning Robot {self.id}.\")\n\n\nclass NotificationSender(Actuator):\n    def __init__(self, room_name):\n        super().__init__(\"NotificationSender\", room_name)\n\n    def notification_sender(self, message):\n        if self.status == \"on\":\n            logger.info(format(\"Notification Sender \" + self.id + \" sends message: \" + message))\n            print(f\"Notification Sender {self.id} send message: {message}\")\n        elif self.status == \"off\":\n            logger.warning(format(\"Notification Sender \" + self.id + \" is OFF, Turn it On First.\"))\n            print(f\"Notification Sender {self.id} is OFF, please turn it on then send the message again.\")\n        else:\n            logger.error(\"Fail to send the message. There is some error with the Notification Sender\")\n            print(\"Fail to send the message. There is some error with the Notification Sender.\")\n\n\nclass MusicPlayer(Actuator):\n    def __init__(self, room_name):\n        super().__init__(\"MusicPlayer\", room_name)\n\n    def play_music(self, playlist):\n        if self.status == \"on\":\n            print(f\"{self.id} start playing {playlist}\")\n            logger.info(format(f\"{self.id} start playing {playlist}\"))\n        elif self.status == \"off\":\n            print(f\"Music Player {self.id} is OFF now, Turn it ON First\")\n            logger.warning(format(\"Music Player\" + self.id + \" is OFF now, Turn it ON First\"))\n            # self.turn_on()\n            # self.play_music(playlist)\n            # print(f\"Turn {self.id} on and Start playing {playlist} list\")\n        else:\n            logger.error(\"Fail to play \" + playlist + \", There is some error with the music player.\")\n            print(\"Fail to play \" + playlist + \", There is some error with the music player.\")\n\n\nclass Light(Actuator):\n    def __init__(self, room_name):\n        super().__init__(\"Light\", room_name)\n        self.brightness_levels = {\n            \"low\": 30,\n            \"medium\": 60,\n            \"high\": 90\n        }\n        self.brightness_level = 0\n\n    def set_brightness_level(self, level_name):\n        if level_name in self.brightness_levels:\n            if self.status == \"on\":\n                self.brightness_level = self.brightness_levels[level_name]\n                print(f\"Set {self.id} light brightness level to {level_name.upper()}\")\n                logger.info(format(\"Set the \" + self.id + \" light brightness level to \" + level_name.upper()))\n            elif self.status == \"off\":\n                print(f\"Light {self.id} is OFF. Please turn it on before setting the brightness level.\")\n                logger.warning(\n                    format(\"Light \" + self.id + \" is OFF. Please turn it on before setting the brightness level.\"))\n            else:\n                print(\"There is an error with the Light.\")\n                logger.error(\"There is an error with the Light.\")\n        else:\n            print(\n                f\"Invalid brightness level: {level_name}. Available levels are {list(self.brightness_levels.keys())}.\")\n            logger.error(format(\"Invalid brightness level: \" + level_name + \". Available levels are \" + str(\n                list(self.brightness_levels.keys()))))\n\n\nclass SmartTV(Actuator):\n    def __init__(self, room_name):\n        super().__init__(\"SmartTV\", room_name)\n\n    def play_channel(self, channel_name):\n        if self.status == \"on\":\n            logger.info(format(\"Start playing \" + channel_name + \" on the \" + self.id + \" in \" + self.room_name))\n            print(f\"Start playing {channel_name} on the {self.id} in {self.room_name}\")\n        elif self.status == \"off\":\n            logger.warning(format(\"\\'\" + self.id + \"\\' is OFF now, Need to Turn it ON First.\"))\n            print(f\"\\'{self.id}\\' is OFF now, Need to Turn it ON First.\")\n            # self.turn_on()\n            # self.play_channel(channel_name)\n        else:\n            logger.error(\"Fail to play \" + channel_name + \", There is some error with the TV.\")\n            print(\"Fail to play \" + channel_name + \", There is some error with the TV.\")\n\n\nclass SmartSocket(Actuator):\n    def __init__(self, room_name):\n        super().__init__(\"SmartSocket\", room_name)\n\n\nclass Humidifier(Actuator):\n    def __init__(self, room_name):\n        super().__init__(\"Humidifier\", room_name)\n\n    def increase_humidity(self):\n        logger.info(f\"Increasing humidity in {self.room_name}\")\n        print(f\"Increasing humidity in {self.room_name}\")\n\n    def decrease_humidity(self):\n        logger.info(f\"Decreasing humidity in {self.room_name}\")\n        print(f\"Decreasing humidity in {self.room_name}\")\n\n# if __name__ == '__main__':\n#   ns = NotificationSender(\"LivingRoom\")\n#   ns.turn_on()\n#   ns.notification_sender(\"test test test\")\n```\n\n## home_plan.py\n```python\nfrom home.sensor import IndoorTemperatureSensor, HumiditySensor, LightIntensiveSensor, SmokeSensor, \\\n    OutdoorTemperatureSensor\nfrom home.actuator import NotificationSender, Light, Window, Curtain, MusicPlayer, Heater, AC, CoffeeMachine, \\\n    SmartSocket, Door, \\\n    CleaningRobot, SmartTV\nfrom home.logger_config import logger\n\n\nclass Room:\n    def __init__(self, name):\n        self.name = name\n        self.sensors = []\n        self.actuators = []\n\n    def add_sensor(self, sensor):\n        self.sensors.append(sensor)\n\n    def add_actuator(self, actor):\n        self.actuators.append(actor)\n\n    def print_info(self):\n        print(f\"\\n{self.name}:\")\n        print(\"Sensors:\")\n        for sensor in self.sensors:\n            print(\"-\", sensor.id)\n        print(\"Actuators:\")\n        for actor in self.actuators:\n            print(\"-\", actor.id)\n\n\ndef create_room_with_components(name, sensor_types, actuator_types):\n    room = Room(name)\n    for sensor_type in sensor_types:\n        room.add_sensor(sensor_type(name))\n    for actuator_type in actuator_types:\n        room.add_actuator(actuator_type(name))\n    return room\n\n\ndef home_plan():\n    # print(\"Starting Home Plan Now\")\n    # Define rooms and their components\n    rooms = [\n        create_room_with_components(\"LivingRoom\", [LightIntensiveSensor, IndoorTemperatureSensor, HumiditySensor],\n                                    [Door, Light, Window, Window, Curtain, MusicPlayer, SmartSocket, SmartSocket,\n                                     CleaningRobot, SmartTV, NotificationSender, AC, Heater]),\n        create_room_with_components(\"Bedroom\", [IndoorTemperatureSensor, HumiditySensor, LightIntensiveSensor],\n                                    [Light, Light, Window, Curtain, AC, Heater, MusicPlayer, Door, SmartSocket,\n                                     SmartSocket, CleaningRobot]),\n        create_room_with_components(\"Kitchen\", [HumiditySensor, SmokeSensor],\n                                    [Light, Window, Heater, CoffeeMachine, SmartSocket, SmartSocket, SmartSocket,\n                                     Door]),\n        create_room_with_components(\"Bathroom\", [IndoorTemperatureSensor, HumiditySensor],\n                                    [Light, Window, Heater, Door, SmartSocket, SmartSocket]),\n        create_room_with_components(\"Balcony\", [OutdoorTemperatureSensor, HumiditySensor],\n                                    [Door])\n    ]\n\n    # Print Home plan\n    # for room in rooms:\n    #     room.print_info()\n\n    return rooms\n\n# Example invocation\n# home_plan()\ndef print_home_plan(home):\n    print(f\"\\n---Home Plan---\")\n    for room in home:\n        room.print_info()\n\n\ndef get_room(home, room_name):\n    for room in home:\n        if room.name == room_name:\n            print(f\"We find {room_name}!\")\n            logger.info(f\"We find {room_name}!\")\n            return room\n\n    print(f\"there is no room called {room_name} at home\")\n    logger.warning(f\"there is no room called {room_name} at home\")\n    return None\n\n\ndef get_room_sensors(home, room_name):\n    for room in home:\n        # if room.name.lower() == room_name.lower():\n        if room.name == room_name:\n            # room.print_info()\n            return room.sensors\n\n    print(f\"there is no Sensor found in {room_name}\")\n    logger.warning(f\"there is no Sensor found in {room_name}\")\n    return None  # no room_name room\n\n\ndef get_room_actuators(home, room_name):\n    for room in home:\n        if room.name == room_name:\n            # room.print_info()\n            return room.actuators\n\n    print(f\"there is no Actuator found in {room_name}\")\n    logger.warning(f\"there is no Actuator found in {room_name}\")\n    return None\n\n\ndef get_all_sensors(home, sensor_type):\n    all_sensors = []\n    for room in home:\n        for sensor in room.sensors:\n            if sensor.sensor_type == sensor_type:\n                # print(sensor.id)\n                all_sensors.append(sensor)\n\n    return all_sensors\n\n\ndef get_all_actuators(home, actuator_type):\n    all_actuators = []\n    for room in home:\n        for actuator in room.actuators:\n            if actuator.actuator_type == actuator_type:\n                all_actuators.append(actuator)\n\n    # print(all_actuators)\n    return all_actuators\n\n\nif __name__ == \"__main__\":\n    # get_room(home_plan(), \"outdoor\")\n    home = home_plan()\n    # get_all_sensors(home, \"IndoorTemperature\")\n    get_all_actuators(home, \"Light\")\n```\n\n## config.py\n```python\n# wait duration\nTEMP_CHANGE_DURATION_WINDOW = 1\n\n# threshold\nTEMP_LOW = 15 # Celsius degree\nTEMP_HIGH = 25\n\nHUMIDITY_LOW = 30 # percentage\nHUMIDITY_HIGH = 50\n\nLIGHT_INTENSITY_LOW = 300 #lux: lumen per square meter\nLIGHT_INTENSITY_HIGH = 900\n\nDAILY_ROUTINE_DURATION = 5\n```"
        },
        {
            "role": "assistant",
            "content": "# Given the functional description and the provided source code, we can create a `function.py` file that handles the specified tasks. Below is the `function.py` file implementation:\n\n# functions/function.py\n\nfrom home.home_plan import home_plan, get_all_actuators\n\ndef main():\n    home = home_plan()\n\n    # Adjust AC temperature to 26°C\n    ac_units = get_all_actuators(home, \"AC\")\n    for ac in ac_units:\n        ac.turn_on()\n        ac.set_target_temperature(26)\n        print(f\"Adjusted {ac.id} temperature to 26°C\")\n\n    # Increase TV volume by 3 levels (assuming each level is 1 step)\n    tv_units = get_all_actuators(home, \"SmartTV\")\n    for tv in tv_units:\n        tv.turn_on()\n        # Assuming there is a method to increase volume; here we mock it as `increase_volume`\n        for _ in range(3):\n            tv.increase_volume()  # This method should be implemented in SmartTV class\n        print(f\"Increased {tv.id} volume by 3 levels\")\n\n    # Heat the electric kettle to 100°C\n    heaters = get_all_actuators(home, \"Heater\")\n    for heater in heaters:\n        heater.turn_on()\n        heater.set_target_temperature(100)\n        print(f\"Set {heater.id} to 100°C\")\n\nif __name__ == \"__main__\":\n    main()"
        },
        {
            "role": "user",
            "content": "Please fix the code reporting the following error messages, and provide me with the updated and complete code:\nTraceback (most recent call last):\nFile \"/Users/minghe/llm4faas/experiments_default/functions_zh/gpt4o_functions/openai_gpt-4o_remote_control_9.py\", line 34, in <module>\nmain()\nFile \"/Users/minghe/llm4faas/experiments_default/functions_zh/gpt4o_functions/openai_gpt-4o_remote_control_9.py\", line 23, in main\ntv.increase_volume()  # This method should be implemented in SmartTV class\n^^^^^^^^^^^^^^^^^^\nAttributeError: 'SmartTV' object has no attribute 'increase_volume'\n\n"
        },
        {
            "role": "assistant",
            "content": "# To resolve the `AttributeError` related to the missing `increase_volume` method in the `SmartTV` class, we'll need to define this method in the `SmartTV` class within the `actuator.py` file. After that, I'll provide you with the complete and updated code for `function.py`.\n# \n# Let's first modify the `actuator.py` file to include the `increase_volume` method in the `SmartTV` class:\n# \n# ### Updated `actuator.py`\n\n# Existing imports and code...\n\nclass SmartTV(Actuator):\n    def __init__(self, room_name):\n        super().__init__(\"SmartTV\", room_name)\n        self.volume_level = 10  # Assume initial volume level is 10\n        self.max_volume = 100   # Maximum volume level\n\n    def play_channel(self, channel_name):\n        if self.status == \"on\":\n            logger.info(format(\"Start playing \" + channel_name + \" on the \" + self.id + \" in \" + self.room_name))\n            print(f\"Start playing {channel_name} on the {self.id} in {self.room_name}\")\n        elif self.status == \"off\":\n            logger.warning(format(\"\\'\" + self.id + \"\\' is OFF now, Need to Turn it ON First.\"))\n            print(f\"\\'{self.id}\\' is OFF now, Need to Turn it ON First.\")\n        else:\n            logger.error(\"Fail to play \" + channel_name + \", There is some error with the TV.\")\n            print(\"Fail to play \" + channel_name + \", There is some error with the TV.\")\n\n    def increase_volume(self):\n        if self.status == \"on\":\n            if self.volume_level < self.max_volume:\n                self.volume_level += 1\n                print(f\"Volume of {self.id} increased to {self.volume_level}\")\n                logger.info(f\"Volume of {self.id} increased to {self.volume_level}\")\n            else:\n                print(f\"Volume of {self.id} is already at maximum level.\")\n                logger.info(f\"Volume of {self.id} is already at maximum level.\")\n        elif self.status == \"off\":\n            print(f\"Smart TV {self.id} is OFF. Please turn it on first.\")\n            logger.warning(f\"Smart TV {self.id} is OFF. Please turn it on first.\")\n        else:\n            logger.error(\"There is an error with the Smart TV.\")\n            print(\"There is an error with the Smart TV.\")\n\n# Other classes..."
        },
        {
            "role": "user",
            "content": "Please fix the code reporting the following error messages, and provide me with the updated and complete code:\nTraceback (most recent call last):\n  File \"/Users/minghe/llm4faas/syntactic_error_loop/test_output/zh/gpt-4o/gpt-4o_remote_control_9_1_0fecd7b7-67c9-4bd7-ac94-53d47f61bdcc.py\", line 9, in <module>\n    class SmartTV(Actuator):\n                  ^^^^^^^^\nNameError: name 'Actuator' is not defined\n\n"
        }
    ]

    messages.append({"role": "assistant", "content": new_python_code})
    messages.append({"role": "user", "content": f"{ERROR_PROMPT}{new_error_msg}\n"})

    inference_id = str(uuid.uuid4())
    iteration_id = 3

    while iteration_id <= MAX_ITERATIONS:
        print(f"-------------Iteration {iteration_id} starts-------------")

        response_content, full_response, start_time, end_time = call_llm_openai(messages)

        python_code = code_extration(response_content)

        base_name = os.path.basename(md_file_path).replace('.md', '')
        python_name = f"{MODEL}_{base_name}_{iteration_id}_{inference_id}.py"
        full_response_name = f"{MODEL}_{base_name}_{iteration_id}_{inference_id}.md"

        python_file = os.path.join(output_dir, python_name)
        full_response_file = os.path.join(output_dir, full_response_name)

        full_response_with_msg = {
            "messages": messages,
            "full_response": full_response
        }

        # save files
        save_python_code(python_code, python_file)
        save_python_code(json.dumps(full_response_with_msg, indent=2, ensure_ascii=False), full_response_file)

        print(f"Saved iteration files: {python_name} / {full_response_name}")

        error = execute_python_file(python_file)

        if error:
            error_status = "error"
            print(f"******* Error found:\n{error} *******")

            # append error message to messages
            messages.append({"role": "assistant", "content": python_code})
            messages.append({"role": "user", "content": f"{ERROR_PROMPT}{error}\n"})

            log_result_to_csv(RESULT_CSV_FILE_PATH, MODEL, base_name, iteration_id, start_time, end_time, inference_id,
                              error_status, json.dumps(error))
            iteration_id += 1

        else:
            error_status = "fixed"
            log_result_to_csv(RESULT_CSV_FILE_PATH, MODEL, base_name, iteration_id, start_time, end_time, inference_id,
                              error_status)
            # print("Code executed without errors reported.")
            print(f"Error fixed at the {iteration_id} iteration.")
            break

if __name__ == "__main__":
    output_dir = f'/Users/minghe/llm4faas/syntactic_error_loop/test_output/{LANGUAGE}/{MODEL}'
    log_file_path = '/Users/minghe/llm4faas/experiments_default/functions_zh/gpt4o_functions/openai_gpt-4o_remote_control_9.log'

    # rerun_qwen_energy_2(log_file_path, output_dir)
    rerun_gpt4o_rc_9(log_file_path, output_dir)
   