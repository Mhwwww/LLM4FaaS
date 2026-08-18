import pandas as pd
import os

# data source
# excel_file = 'data_en.xlsx'  # excel path
# sheet_name = 'en'  # sheet name

excel_file = '../eva/data.xlsx'  # excel path
sheet_name = 'Sheet1'  # sheet name

# Remote Control Markdown file generation
markdown_template = 'baseline_v2_remote-control_template.md'  # Markdown template file path

output_dir = './baseline_v2_prompt_zh/remote_control'  # output directory

output_prefix = 'remote_control_'  # prefix of the output file name
column_index = 6


# Energy Markdown file generation
# output_dir = 'baseline_v2_prompt_zh/energy'  # output directory
#
# output_prefix = 'energy_control_'   # prefix of the output file name
# column_index = 13

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
