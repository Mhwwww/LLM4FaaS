import pandas as pd
import os

# data source
# excel_file = 'data_en.xlsx'  # excel path
# sheet_name = 'en'  # sheet name

excel_file = 'data.xlsx'  # excel path
sheet_name = 'Sheet1'  # sheet name

# Remote Control Markdown file generation
# markdown_template = 'system_prompt_remote-control-prompt_template.md'  # Markdown template file path

# js_baseline_prompt
markdown_template = './js_prompt_template/js_baseline_remote_control_template.md'  # Markdown template file path
# output_dir = '../experiments_js/prompt_baseline/remote_control'
output_dir = '../experiments_js/prompt_baseline/energy_control'

# js_prompt
# markdown_template = './js_prompt_template/js_remote-control-prompt_template.md'  # Markdown template file path
# output_dir = '/results_open_intepreter/experiments_js/prompt_zh/remote_control'  # output directory

# output_dir = '../logs_questionnaire_in_English/remote_control'  # output directory
# output_dir = '../logs_questionnaire_in_Chinese/remote_control'  # output directory

# output_dir = '../system_prompts_experiments/user_prompt_zh_short/remote_control'  # output directory
# output_dir = '../system_prompts_experiments/user_prompt_en_short/remote_control'  # output directory

# output_prefix = 'remote_control_'  # prefix of the output file name
# column_index = 6


# Energy Markdown file generation
# markdown_template = 'baseline_v2_remote-control_template.md'  # Markdown template file path
# markdown_template = './js_prompt_template/js_remote-control-prompt_template.md'  # Markdown template file path
# output_dir = '/Users/minghe/llm4faas/experiments_js/prompt_zh/energy'  # output directory

# output_dir = '../logs_questionnaire_in_English/energy'  # output directory
# output_dir = '../logs_questionnaire_in_Chinese/energy'  # output directory

# output_dir = '../system_prompts_experiments/user_prompt_zh_short/energy'  # output directory
# output_dir = '../system_prompts_experiments/user_prompt_en_short/energy'  # output directory
output_prefix = 'energy_control_'   # prefix of the output file name
column_index = 13

# read Excel data
df = pd.read_excel(excel_file, sheet_name=sheet_name)

# extract column text
texts = df.iloc[:, column_index].dropna().tolist()

# create the output directory (if it does not exist)
os.makedirs(output_dir, exist_ok=True)

# generate multiple Markdown files
for i, text in enumerate(texts):
    # read Markdown template
    with open(markdown_template, 'r', encoding='utf-8') as file:
        content = file.read()

    # insert content in the specific location
    content = content.replace('<!-- INSERT HERE -->', text)
    output_file = os.path.join(output_dir, f'{output_prefix}{i+1}.md')
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(content)

    print(f'Generated file: {output_file}')

print('All files generated successfully.')
