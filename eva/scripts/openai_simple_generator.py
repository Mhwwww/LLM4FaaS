import os
import time
import openai

from model_setting import MAX_TOKENS, TEMPERATURE, OPENAI_MODEL, DELAY_SECONDS, SYSTEM_PROMPT
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ["OPENAI_API_KEY"]

openai.api_key = api_key
model = OPENAI_MODEL

# repeat experiments
MD_FILES_DIR = '~/llm4faas/default_experiments/logs_repeat_Chinese/temp/'
OUTPUT_DIR = '../../functions_repeat/'


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
        temperature=TEMPERATURE,
    )
    response_content = response.choices[0].message.content.strip()
    # return response_content
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

def generate_files_from_directory(prompt_dir, output_dir):
# def main():
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(prompt_dir):
        if filename.endswith('.md'):
            md_file_path = os.path.join(prompt_dir, filename)
            markdown_content = read_markdown(md_file_path)
            prompt = f"{markdown_content}"
            python_code = generate_python_code(prompt)

            base_name = os.path.basename(md_file_path).replace('.md', '')
            output_file_name = os.path.join(output_dir, f'openai_{model}_{base_name}_{time.time_ns()}.py')

            # save the generated python code to a file
            save_python_code(python_code, output_file_name)
            print(f"Saved Python file to {output_file_name}")
            time.sleep(DELAY_SECONDS)

def repeatable_experiments(md_dir, output_dir, repeat_times):
    for i in range(repeat_times):
        print(f"Start {i+1} Iteration")
        generate_files_from_directory(md_dir, output_dir)
        print(f"Finished {i + 1} round iteration.\n")

if __name__ == '__main__':
    repeatable_experiments(MD_FILES_DIR, OUTPUT_DIR, 1)
