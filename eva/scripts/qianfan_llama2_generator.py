import os
import time

import qianfan
from openai import OpenAI
from eva.scripts.model_setting import QIANFAN_MODEL

# todo: add api key here
os.environ["QIANFAN_AK"] = ""
os.environ["QIANFAN_SK"] = ""
qianfan_openai_api_key = ''

MD_FILES_DIR = '~/llm4faas/default_experiments/logs_questionnaire_in_Chinese/auto_adapt/'
# MD_FILES_DIR = '~/llm4faas/default_experiments/logs_questionnaire_in_Chinese/energy_control/'
# MD_FILES_DIR = '~/llm4faas/default_experiments/logs_questionnaire_in_Chinese/remote_control/'
# MD_FILES_DIR = '~/llm4faas/default_experiments/logs_questionnaire_in_Chinese/plan/'

OUTPUT_DIR = '../../baidu_functions/'

model = QIANFAN_MODEL

def test_openai_generation():
    client = OpenAI(
        api_key=qianfan_openai_api_key,
        base_url="https://qianfan.baidubce.com/v2",
    )

    messages = [{"role": "user", "content": "20和11，哪个数大?"}]

    response = client.chat.completions.create(
        model=QIANFAN_MODEL,
        messages=messages
    )

    # print(response.choices[0].message)
    print(response.to_dict())

def read_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # print(content)
    return content


def baidu_generate_python_code(messages):
    start_time = time.time_ns()

    resp = qianfan.ChatCompletion().do(
        model=model,
        messages = messages,
        # messages=[
        #     {"role": "user", "content": prompt},
        # ],
        system = "你是一个乐于解答各种问题的助手，你的任务是为用户提供专业、准确、有见地的建议。",
        temperature=0.7,
        max_output_tokens=1500, # default 4096
    )
    end_time = time.time_ns()
    response_content = resp["body"]['result']

    return response_content, resp, start_time, end_time

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
            python_code = baidu_generate_python_code(prompt)

            base_name = os.path.basename(md_file_path).replace('.md', '')
            output_file_name = os.path.join(output_dir, f'zhipu_{model}_{base_name}_{time.time_ns()}.py')

            # save the generated python code to a file
            save_python_code(python_code, output_file_name)
            print(f"Saved Python file to {output_file_name}")
            time.sleep(1)

if __name__ == '__main__':
    generate_files_from_directory(MD_FILES_DIR, OUTPUT_DIR)
