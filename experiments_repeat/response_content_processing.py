import os

def process_file(file_path):
    """comment out the no-python parts"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    def comment_out_non_python(content):
        result = []
        inside_python_block = False

        lines = content.split('\n')
        for line in lines:
            if '```python' in line:
                inside_python_block = True
                result.append(f"# {line}")  
                continue

            if '```' in line and inside_python_block:
                inside_python_block = False
                result.append(f"# {line}")  
                continue 

            if inside_python_block:
                result.append(line)
            else:
                result.append(f"# {line}")  

        return '\n'.join(result)

    processed_content = comment_out_non_python(content)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(processed_content)
    print(f"Processed and updated file: {file_path}")


def process_directory(directory):
    """process all Python files in the dirtory"""
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if os.path.isfile(file_path) and filename.endswith('.py'):
            print(f"Processing Python file: {file_path}")
            process_file(file_path)


if __name__ == '__main__':
    # target_directory = '/Users/minghe/llm4faas/experiments_baseline_v2/baseline_v2_functions_zh/plans'
    # target_directory = '/Users/minghe/llm4faas/experiments_baseline/baseline_functions_zh/auto_adapt'
    # target_directory = '/Users/minghe/llm4faas/experiments_baseline/baseline_functions_zh/remote_control'
    # target_directory = '/Users/minghe/llm4faas/experiments_baseline/baseline_functions_zh/plans'
    # target_directory = '/Users/minghe/llm4faas/experiments_baseline/baseline_functions_zh/energy'
    # target_directory = '/Users/minghe/llm4faas/experiments_repeat/repeat_functions'
    target_directory = '/Users/minghe/llm4faas/experiments_repeat/repeat_functions_4o-mini'

    process_directory(target_directory)