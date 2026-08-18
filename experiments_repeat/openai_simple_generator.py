import json
import os
import re
import shutil
import time

import openai

from eva.scripts.model_setting import MAX_TOKENS, TEMPERATURE, OPENAI_MODEL, DELAY_SECONDS, SYSTEM_PROMPT

openai.api_key = ''
model = OPENAI_MODEL

# MD_FILES_DIR = '/Users/minghe/llm4faas/experiments_repeat/repeat_prompts'
# GPT_OUTPUT_DIR = '/Users/minghe/llm4faas/experiments_repeat/repeat_functions_4o-mini'

# pyton experiments
# MD_FILES_DIR = "/Users/minghe/llm4faas/experiments_default/logs_questionnaire_in_Chinese/remote_control/"
# GPT_OUTPUT_DIR = '/Users/minghe/llm4faas/experiments_default/logs_questionnaire_in_Chinese/output/'

# nodejs experiments
MD_FILES_DIR = '/Users/minghe/llm4faas/experiments_js/prompt_zh/auto_adapt/'
GPT_OUTPUT_DIR = '/Users/minghe/llm4faas/experiments_js/output/'

# tinyfaas preparation for NodeJS functions
def process_js_file(file_path):
    print(f"[START] Process {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # if contains main block
    has_main_block = any('if (require.main === module)' in line and not line.startswith('//') for line in lines)
    has_module_exports = any('module.exports' in line and not line.strip().startswith('//') for line in lines)

    new_lines = []
    inside_exports_block = False

    if has_main_block:
        print(f"Found main block in {file_path}, processing...")
        for line in lines:
            if 'if (require.main === module)' in line:
                new_lines.append("// " + line)
                add_line = line.replace('if (require.main === module)',
                                        'module.exports = (req, res) =>')
                new_lines.append(add_line) 

                continue

            if 'module.exports' in line:
                if '{' in line and '};' not in line:
                    new_lines.append('// ' + line)
                    inside_exports_block = True
                    continue
                # else:  # add module.exports 
                new_lines.append('// ' + line)
                continue

            if inside_exports_block:
                new_lines.append('// ' + line)
                if '};' in line:
                    inside_exports_block = False
                continue
            new_lines.append(line)

    else:
        print(f"Not found main block in {file_path}, processing...")
        has_export_statement = False
        for line in lines:
            if 'module.exports =' in line:
                has_export_statement = True
                new_lines.append("// " + line)
                new_lines.append(line.replace('module.exports =', 'module.exports = (req, res) =>'))
                continue

            new_lines.append(line)
        if not has_module_exports and not has_export_statement:
            new_lines.append("\nmodule.exports = (req, res) => { main(); }\n")
            print("Added default: module.exports = (req, res) => { main(); }")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)


    print(f'[DONE] Processed {file_path}')


def process_output_to_index(output_file):
    print("Process NodeJS output files for tinyFaaS...")
    # 1. create folder for the output function
    folder_path = os.path.abspath(output_file).strip('.js')

    # folder_path = os.path.splitext(os.path.abspath(output_file))[0]
    os.makedirs(folder_path, exist_ok=True)

    # 2. copy NodeJS 'home' folder to function folder
    shutil.copytree('/Users/minghe/llm4faas_js/home', os.path.join(folder_path, "home"),
                    dirs_exist_ok=True)

    # 4. create the 'package.json' in the function folder
    requirement_path = os.path.join(folder_path, "package.json")
    with open(requirement_path, "w", encoding="utf-8") as f:
        f.write('{"name": "fn", "version": "1.0.0", "main": "./functions/index.js"}')

    # 3. create 'index.js' in the 'functions' folder and copy the content of generated function to it
    functions_path = os.path.join(folder_path, "functions")
    os.makedirs(functions_path, exist_ok=True)

    new_fn_path = os.path.join(functions_path, "index.js")
    shutil.copy(output_file, new_fn_path)

    # process the index.js file to exports function with req and res
    process_js_file(new_fn_path)

    print(f"Processed the Generated file: {os.path.basename(output_file)} -> {folder_path}")

    return folder_path

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
            # {"role": "system", "content": SYSTEM_PROMPT},
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


def comment_out_non_js(content):
    result = []
    # only keep the python code block
    inside_python_block = False

    # split the content by lines
    lines = content.split('\n')
    for line in lines:
        if '```javascript' in line:
            inside_python_block = True
            # comment out ```python``` and move to next line
            result.append(f"// {line}")
            continue

        # if it is the end of python code block
        if '```' in line and inside_python_block:
            inside_python_block = False
            # comment out ``` and move to next line
            result.append(f"// {line}")
            continue

        # keep the python code block
        if inside_python_block:
            result.append(line)
        else:
            # comment out non-python code block
            result.append(f"// {line}")

    return '\n'.join(result)


def get_results_single_md(md_file_path, output_dir):
    markdown_content = read_markdown(md_file_path)
    prompt = f"{markdown_content}"

    generation_start_time = time.time_ns()
    print(f"{OPENAI_MODEL} starts generating code at {generation_start_time}")
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

    fn_folder = process_output_to_fn(output_file)
    return fn_folder, output_file_name, generation_end_time, generation_start_time


def get_results_single_md_nodejs(md_file_path, output_dir):
    markdown_content = read_markdown(md_file_path)
    prompt = f"{markdown_content}"

    generation_start_time = time.time_ns()
    print(f"{OPENAI_MODEL} starts generating code at {generation_start_time}")
    python_code, response = generate_python_code(prompt)

    generation_end_time = time.time_ns()
    print(f"{OPENAI_MODEL} finished generating code at {generation_end_time}")

    base_name = os.path.basename(md_file_path).replace('.md', '')
    output_file_name = f'openai_{model}_{base_name}_{time.time_ns()}.js'
    output_file = os.path.join(output_dir, output_file_name)

    md_file_name = os.path.join(output_dir, f'openai_{model}_{base_name}_{time.time_ns()}.md')
    save_python_code(json.dumps(response, indent=2, ensure_ascii=False), md_file_name)
    print(f"Saved FULL RESPONSE to {md_file_name}")

    python_code = comment_out_non_js(python_code)
    # save the generated python code to a file
    save_python_code(python_code, output_file)
    print(f"Saved Python file to {output_file_name}")

    fn_folder = process_output_to_index(output_file)
    return fn_folder, output_file_name, generation_end_time, generation_start_time

def generate_files_from_directory(prompt_dir, output_dir):
    # def main():
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(prompt_dir):
        if filename.endswith('.md'):
            md_file_path = os.path.join(prompt_dir, filename)

            get_results_single_md_nodejs(md_file_path, output_dir)

            time.sleep(DELAY_SECONDS)


def repeatable_experiments(md_dir, output_dir, repeat_times):
    for i in range(repeat_times):
        print(f"Start {i + 1} Iteration")
        generate_files_from_directory(md_dir, output_dir)
        print(f"Finished {i + 1} round iteration.\n")


if __name__ == '__main__':
    repeatable_experiments(MD_FILES_DIR, GPT_OUTPUT_DIR, 1)
