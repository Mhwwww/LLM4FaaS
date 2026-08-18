import json
import os
import shutil
import time
import openai

from eva.scripts.model_setting import MAX_TOKENS, TEMPERATURE, OPENAI_MODEL, DELAY_SECONDS, SYSTEM_PROMPT

openai.api_key = ''
model = OPENAI_MODEL

# MD_FILES_DIR = '/Users/minghe/llm4faas/experiments_repeat/repeat_prompts'
# GPT_OUTPUT_DIR = '/Users/minghe/llm4faas/experiments_repeat/repeat_functions_4o-mini'

# nodejs baseline
MD_FILES_DIR = "/Users/minghe/llm4faas/experiments_baseline_v2/baseline_v2_prompt_zh/remote_control"
GPT_OUTPUT_DIR = '/Users/minghe/llm4faas/experiments_js/baseline_output/'

BASELINE_LATENCY_OUTPUT = '/Users/minghe/llm4faas/eva_latency/_out/nodejs_baseline_latency.out'

def read_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # print(content)
    return content


def generate_python_code(prompt):
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE
    )
    response_content = response.choices[0].message.content.strip()
    return response_content, response.to_dict()


def save_python_code(code, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(code)


def comment_out_non_python(content):
    result = []
    # only keep the python code block
    inside_python_block = False

    # split the content by lines
    lines = content.split('\n')
    for line in lines:
        if '```python' in line:
            inside_python_block = True
            # comment out ```python``` and move to next line
            result.append(f"# {line}")
            continue

        # if it is the end of python code block
        if '```' in line and inside_python_block:
            inside_python_block = False
            # comment out ``` and move to next line
            result.append(f"# {line}")
            continue

        # keep the python code block
        if inside_python_block:
            result.append(line)
        else:
            # comment out non-python code block
            result.append(f"# {line}")

    return '\n'.join(result)


def get_results_single_md(md_file_path, output_dir):
    markdown_content = read_markdown(md_file_path)
    prompt = f"{markdown_content}"

    generation_start_time = time.time_ns()
    print(f"{OPENAI_MODEL} starts generating code for {os.path.basename(md_file_path)} at {generation_start_time}")
    python_code, response = generate_python_code(prompt)

    generation_end_time = time.time_ns()
    print(f"{OPENAI_MODEL} finished generating code at {generation_end_time}")

    base_name = os.path.basename(md_file_path).replace('.md', '')
    output_file_name = f'openai_{model}_{base_name}_{time.time_ns()}.py'
    output_file = os.path.join(output_dir, output_file_name)

    md_file_name = os.path.join(output_dir, f'openai_{model}_{base_name}_{time.time_ns()}.md')
    save_python_code(json.dumps(response, indent=2, ensure_ascii=False), md_file_name)
    print(f"Saved FULL RESPONSE to {md_file_name}")

    python_code = comment_out_non_python(python_code)
    # save the generated python code to a file
    save_python_code(python_code, output_file)
    print(f"Saved Python file to {output_file_name}")


    return base_name, generation_end_time, generation_start_time


def generate_files_from_directory(prompt_dir, output_dir):
    if not os.path.exists(BASELINE_LATENCY_OUTPUT):
        with open(BASELINE_LATENCY_OUTPUT, "w") as f:
            f.write('fn_name, generate_end_time, generate_start_time\n')

    for filename in os.listdir(prompt_dir):
        if filename.endswith('.md'):
            md_file_path = os.path.join(prompt_dir, filename)

            base_name, end_time, start_time =  get_results_single_md(md_file_path, output_dir)

            with open(BASELINE_LATENCY_OUTPUT, 'a') as f:
                f.write(f'{base_name}, {end_time}, {start_time}\n')

            time.sleep(DELAY_SECONDS)


def repeatable_experiments(md_dir, output_dir, repeat_times):
    for i in range(repeat_times):
        print(f"Start {i + 1} Iteration")
        generate_files_from_directory(md_dir, output_dir)
        print(f"Finished {i + 1} round iteration.\n")


if __name__ == '__main__':
    repeatable_experiments(MD_FILES_DIR, GPT_OUTPUT_DIR, 1)
