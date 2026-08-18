import os
import subprocess

TIMEOUT = 30

# folder path where the generated function files are stored

# folder_path = '/Users/minghe/llm4faas/functions_zh/gpt4o_functions'
# folder_path = '/Users/minghe/llm4faas/functions_zh/azure_openai_gpt3516k_functions'
# folder_path = '/Users/minghe/llm4faas/functions_zh/gemini_functions'
# folder_path = '/Users/minghe/llm4faas/functions_zh/llama31_functions'
# folder_path = '/Users/minghe/llm4faas/functions_zh/copilot_functions/autoadapt'
# folder_path = '/Users/minghe/llm4faas/functions_zh/4o-mini_functions'

# folder_path = '/Users/minghe/llm4faas/functions_en/4o-mini_en_functoins'
# folder_path = '/Users/minghe/llm4faas/functions_en/azure_en_functions'
# folder_path = '/Users/minghe/llm4faas/functions_en/gemini_en_functions'
# folder_path = '/Users/minghe/llm4faas/functions_en/llama31_en_functions'
# folder_path = '/Users/minghe/llm4faas/functions_en/copilot_en_functions/auto-adapt'
# folder_path = '/Users/minghe/llm4faas/functions_en/copilot_en_functions/energy-control'
# folder_path = '/Users/minghe/llm4faas/functions_en/copilot_en_functions/plan'
# folder_path = '/Users/minghe/llm4faas/functions_en/copilot_en_functions/remote-control'

# folder_path = '/Users/minghe/llm4faas/system_prompts_experiments/zh_functions/gpt4o-mini'

# folder_path = '/Users/minghe/llm4faas/default_experiments/functions_zh/4o-mini_functions/'
# folder_path = '/Users/minghe/llm4faas/default_experiments/functions_en/gpt-4o_en_functions/energy/'

# folder_path = '/Users/minghe/llm4faas/functions_repeat/gemini_repeat_functions'
# folder_path = '/Users/minghe/llm4faas/default_experiments/functions_repeat_zh/gpt4o/'

folder_path = '/Users/minghe/llm4faas/zhipu_functions/remote/'

# Iterate through all generated function files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.py'):
        # full path of the file
        file_path = os.path.join(folder_path, filename)

        # save to .log
        log_file_path = os.path.join(folder_path, filename.replace('.py', '.log'))

        with open(log_file_path, 'w') as log_file:
            try:
                # start subprocess and catch stdout & stderr
                process = subprocess.Popen(
                    ['python3', file_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                # catch stdout & stderr when timeout
                stdout, stderr = process.communicate(timeout=TIMEOUT)

                # write stdout & stderr to log file
                log_file.write("Standard Output:\n")
                log_file.write(stdout)
                log_file.write("\nStandard Error:\n")
                log_file.write(stderr)
                log_file.write(f"\nReturn code: {process.returncode}\n")

            except subprocess.TimeoutExpired:
                log_file.write("Error: Execution timed out\n")
                process.kill()
                outs, errs = process.communicate()  # get the remaining output
                log_file.write("Standard Output:\n")
                log_file.write(outs)
                log_file.write("\nStandard Error:\n")
                log_file.write(errs)
            except FileNotFoundError:
                log_file.write(f"Error: File not found {file_path}\n")
            except Exception as e:
                log_file.write(f"Unexpected error: {str(e)}\n")

        print(f'Executed {filename}, output saved to {log_file_path}')
