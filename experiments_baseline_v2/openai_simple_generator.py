import json
import os
import time
import openai

from eva.scripts.model_setting import MAX_TOKENS, TEMPERATURE, OPENAI_MODEL, DELAY_SECONDS, SYSTEM_PROMPT

from dotenv import load_dotenv
load_dotenv()

api_key = os.environ["OPENAI_API_KEY"]
openai.api_key = api_key

model = OPENAI_MODEL

MD_FILES_DIR = '/Users/minghe/llm4faas/experiments_baseline_v2/baseline_v2_prompt_zh/plans'
OUTPUT_DIR = '/Users/minghe/llm4faas/experiments_baseline_v2/baseline_v2_functions_zh/plans'
# MD_FILES_DIR = '/Users/minghe/llm4faas/experiments_baseline/baseline_prompt_zh/energy'
# OUTPUT_DIR = '/Users/minghe/llm4faas/experiments_baseline/baseline_functions_zh/energy'

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

def generate_files_from_directory(prompt_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(prompt_dir):
        if filename.endswith('.md'):
            md_file_path = os.path.join(prompt_dir, filename)
            markdown_content = read_markdown(md_file_path)
            prompt = f"{markdown_content}"
            python_code, response = generate_python_code(prompt)

            base_name = os.path.basename(md_file_path).replace('.md', '')
            output_file_name = os.path.join(output_dir, f'openai_{model}_{base_name}_{time.time_ns()}.py')
            md_file_name = os.path.join(output_dir, f'openai_{model}_{base_name}_{time.time_ns()}.md')

            # save the generated python code to a file
            save_python_code(python_code, output_file_name)
            print(f"Saved Python file to {output_file_name}")

            time.sleep(DELAY_SECONDS)

            save_python_code(json.dumps(response, indent=2, ensure_ascii=False), md_file_name)
            print(f"Saved FULL RESPONSE to {md_file_name}")

            time.sleep(DELAY_SECONDS)


def repeatable_experiments(md_dir, output_dir, repeat_times):
    for i in range(repeat_times):
        print(f"Start {i+1} Iteration")
        generate_files_from_directory(md_dir, output_dir)
        print(f"Finished {i + 1} round iteration.\n")

if __name__ == '__main__':
    repeatable_experiments(MD_FILES_DIR, OUTPUT_DIR, 1)
