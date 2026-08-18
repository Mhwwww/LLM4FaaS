import pandas as pd
import os

# excel_file = 'data_en.xlsx'
# sheet_name = 'en'

excel_file = 'data.xlsx'
sheet_name = 'Sheet1'

# morning_column_index = 7
# leave_home_column_index = 8
# movie_column_index = 9
# #
# # markdown_template = 'baseline_v2_plans_template.md'
# # # output_dir = '../logs_questionnaire_in_Chinese/plans'
# # output_dir = '../logs_questionnaire_in_English/plans'
# # output_prefix = 'plan_'

# markdown_template = '/Users/minghe/llm4faas/eva/js_prompt_template/js_keyword-prompt_template.md'
# output_dir = '/results_open_intepreter/experiments_js/prompt_zh/plan'

# markdown_template = './js_prompt_template/js_baseline_plans_template.md'  # Markdown template file path
# output_dir = '../experiments_js/prompt_baseline/plan'

markdown_template = './js_prompt_template/js_baseline_auto_adapt_template.md'
output_dir = '../experiments_js/prompt_baseline/auto_adapt'


#
# markdown_template = './system_prompt_keyword-prompt_template.md'
# # output_dir = '../system_prompts_experiments/user_prompt_zh_short/plans'  # output directory
# output_dir = '../system_prompts_experiments/user_prompt_en_short/plans'  # output directory
# output_prefix = 'plan_'

# # read Excel data
df = pd.read_excel(excel_file, sheet_name=sheet_name)
#
# # extract Excel column data
# morning_plans = df.iloc[:, morning_column_index].dropna().tolist()
# leave_home_plans = df.iloc[:, leave_home_column_index].dropna().tolist()
# movie_plans = df.iloc[:, movie_column_index].dropna().tolist()


# excel_file = 'data.xlsx'
# sheet_name = 'Sheet1'

temperature_column_index = 10
humidity_column_index = 11
light_column_index = 12

# markdown_template = './system_prompt_keyword-prompt_template.md'
# output_dir = '../logs_questionnaire_in_English/auto_adapt'
# markdown_template = '/Users/minghe/llm4faas/eva/js_prompt_template/js_keyword-prompt_template.md'
# output_dir = '/Users/minghe/llm4faas/experiments_js/prompt_zh/plan'
# output_dir = '/Users/minghe/llm4faas/experiments_js/prompt_zh/auto_adapt'

# output_dir = '../system_prompts_experiments/user_prompt_zh_short/auto_adapt'  # output directory
# output_dir = '../system_prompts_experiments/user_prompt_en_short/auto_adapt'  # output directory

output_prefix = 'auto_adapt_'
# #
# #
# df = pd.read_excel(excel_file, sheet_name=sheet_name)
#
#
morning_plans = df.iloc[:, temperature_column_index].dropna().astype(str).tolist()
leave_home_plans = df.iloc[:, humidity_column_index].dropna().astype(str).tolist()
movie_plans = df.iloc[:, light_column_index].dropna().astype(str).tolist()
#


os.makedirs(output_dir, exist_ok=True)

for i in range(len(morning_plans)):
    with open(markdown_template, 'r', encoding='utf-8') as file:
        content = file.read()

    content = content.replace('<!-- INSERT TEMPERATURE HERE -->', morning_plans[i])
    content = content.replace('<!-- INSERT HUMIDITY HERE -->', leave_home_plans[i])
    content = content.replace('<!-- INSERT LIGHT HERE -->', movie_plans[i])

    output_file = os.path.join(output_dir, f'{output_prefix}{i+1}.md')
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(content)

    print(f'Generated file: {output_file}')

print('All files generated successfully.')
