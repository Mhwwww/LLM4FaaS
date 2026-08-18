import os

# TASK_NAME = 'auto_adapt'
# TASK_NAME = 'plan'
# TASK_NAME = 'energy_control'
# TASK_NAME = 'remote_control'
TASK_NAMES =['auto_adapt', 'plan', 'energy_control', 'remote_control']

def file_generator(task_name):
    standard_path = f'/Users/minghe/llm4faas/test/{task_name}'
    os.makedirs(standard_path, exist_ok=True)

    for i in range(26):
        file_path = os.path.join(standard_path, f'{task_name}_{i+1}.log')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('Standard Output:\n')

        print(f'Generated file: {file_path}')


if __name__ == '__main__':
    for task_name in TASK_NAMES:
        file_generator(task_name)


