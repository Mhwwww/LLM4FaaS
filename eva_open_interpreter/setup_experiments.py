import os
import shutil


def organize_files(md_folder, python_file, output_folder):
    if not os.path.isdir(md_folder):
        print(f"ERROR: {md_folder} is not a valid path")
        return

    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    if not os.path.isfile(python_file):
        print(f"Error: {python_file} is not existing")
        return

    for filename in os.listdir(md_folder):
        if filename.endswith('.md'):
            file_path = os.path.join(md_folder, filename)
            folder_name = os.path.splitext(filename)[0]
            folder_path = os.path.join(output_folder, folder_name)

            os.makedirs(folder_path, exist_ok=True)

            shutil.copy(file_path, os.path.join(folder_path, filename))

            shutil.copy(python_file, os.path.join(folder_path, os.path.basename(python_file)))

            print(f"Processed: {filename}")


if __name__ == "__main__":
    # md_folder = '/Users/minghe/llm4faas/experiments_baseline_v2/baseline_v2_prompt_zh/auto_adapt'

    # md_folder = '/Users/minghe/llm4faas/experiments_baseline_v2/baseline_v2_prompt_zh/plans'
    # md_folder = '/Users/minghe/llm4faas/experiments_baseline_v2/baseline_v2_prompt_zh/energy'

    python_file = '/Users/minghe/llm4faas/eva/scripts/open-interpreter/open-interpreter-test.py'
    output_folder = '/Users/minghe/llm4faas/eva_open_interpreter/'
    md_folder = '/Users/minghe/llm4faas/experiments_baseline_v2/baseline_v2_prompt_zh/remote_control/'

    organize_files(md_folder, python_file, output_folder)
