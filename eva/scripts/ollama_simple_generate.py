import os
import json
import shutil
import threading
import time
import requests

from openai import OpenAI
from eva.scripts.model_setting import TEMPERATURE, OLLAMA_URL, OLLAMA_MODEL
from eva_latency.llm4faas_automation import upload_single_fn

# directory
MD_FILES_DIR = "~/llm4faas/experiments_default/logs_questionnaire_in_Chinese/temp"
# OUTPUT_DIR = '~/llm4faas/experiments_default/functions_zh/deepseek-r1-functions'
OUTPUT_DIR = '~/llm4faas/experiments_default/logs_questionnaire_in_Chinese/temp'


def generate(prompt_file, context, output_file):
    with open(prompt_file, 'r') as f:
        prompt = f.read()

    r = requests.post(OLLAMA_URL,
                      json={
                          'model': OLLAMA_MODEL,
                          'prompt': prompt,
                          'context': context,
                          # 'system': SYSTEM_PROMPT, # comment this line when running the default experiment
                          'options': {
                              'temperature': TEMPERATURE,
                          },
                      },
                      stream=True)
    r.raise_for_status()
    print(r)
    response_parts = []
    for line in r.iter_lines():
        body = json.loads(line)
        response_part = body.get('response', '')

        if 'error' in body:
            raise Exception(body['error'])

        response_parts.append(response_part)

        if body.get('done', False):
            break

    response_content = ''.join(response_parts).strip()
    print(f"Response content: {response_content}")

    result_lines = []
    in_code_block = False

    for line in response_content.splitlines():
        if '```python' in line or '```' in line:
            result_lines.append(f'# {line}')  # Commenting out the start and end markers of a code block
            in_code_block = not in_code_block
        elif in_code_block:
            result_lines.append(line)  # Adding content within a code block
        else:
            result_lines.append(f'# {line}')  # Commenting out non-block content

    # write the processed content to a file
    with open(output_file, 'w') as f:
        f.write('\n'.join(result_lines))


def generate_via_openai_api(prompt_file):
    with open(prompt_file, 'r') as f:
        prompt = f.read()

    client = OpenAI(
        base_url = 'http://localhost:11434/v1',
        api_key='ollama')
    # required, but unused
    start_time = time.time()
    response = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )
    end_time = time.time()

    duration = end_time - start_time
    print(f"Response time: {duration:.2f} seconds")
    print(response.choices[0].message.content)

def tinyfaas_upload(fn_folder, output_file_name):
    print("3333333333")
    upload_thread = threading.Thread(target=upload_single_fn, args=(fn_folder, output_file_name))

    upload_thread.start()
    upload_thread.join()


def process_output_to_fn(output_file):
    print("222222222")
    folder_path = os.path.abspath(output_file).strip('.py')

    os.makedirs(folder_path, exist_ok=True)
    shutil.copytree('/Users/minghe/llm4faas/tinyFaaS/test/fns/llm/home', os.path.join(folder_path, "home"), dirs_exist_ok=True)

    new_fn_path = os.path.join(folder_path, "fn.py")
    shutil.copy(output_file, os.path.join(folder_path, "fn.py"))

    requirement_path = os.path.join(folder_path, "requirements.txt")
    with open(requirement_path, "w", encoding="utf-8") as f:
        pass


    with open(new_fn_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    inserted_fn = False 

    for line in lines:
        stripped_line = line.strip()
        if stripped_line == 'if __name__ == "__main__":':
            new_lines.append("# " + line)
            if not inserted_fn:
                new_lines.append("def fn(data, headers):\n")  
                inserted_fn = True
        else:
            new_lines.append(line)

    if not inserted_fn:
        new_lines.insert(0, "def fn(data, headers):\n\n")

    with open(new_fn_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"Processed the Generated file: {os.path.basename(output_file)} -> {folder_path}")

    return folder_path


def process_directory(directory):
    context = []  # Storing dialogue history for better contextual understanding by the model
    output_files = []
    for filename in os.listdir(directory):
        if filename.endswith('.md'):
            prompt_file = os.path.join(directory, filename)
            base_name = filename.replace('.md', '')
            output_file_name = f"{OLLAMA_MODEL}_{base_name}_{time.time_ns()}.py"
            output_file = os.path.join(OUTPUT_DIR, output_file_name)
            print("11111111111")
            context = generate(prompt_file, context, output_file)
            print(f"Saved Python file to {output_file_name}")

            fn_folder = process_output_to_fn(output_file)

            tinyfaas_upload(fn_folder, output_file_name)

            time.sleep(5)


def main():
    process_directory(MD_FILES_DIR)

if __name__ == "__main__":
    # main()
    generate_test('/Users/minghe/llm4faas/experiments_default/logs_questionnaire_in_Chinese/temp/remote_control_1.md')