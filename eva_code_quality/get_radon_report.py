import os
import subprocess

PROJECT_ROOT = "/Users/minghe/llm4faas/"

# llm4faas
# SOURCE_DIR = "/Users/minghe/llm4faas/experiments_default/functions_zh/gpt4o_functions"

# no-faas baseline
# SOURCE_DIR = "/Users/minghe/llm4faas/experiments_baseline_v2/baseline_v2_functions_zh/auto_adapt"
# SOURCE_DIR = "/Users/minghe/llm4faas/experiments_baseline_v2/baseline_v2_functions_zh/energy"
# SOURCE_DIR = "/Users/minghe/llm4faas/experiments_baseline_v2/baseline_v2_functions_zh/remote_control"
# SOURCE_DIR = "/Users/minghe/llm4faas/experiments_baseline_v2/baseline_v2_functions_zh/plans"

# human_developer
# SOURCE_DIR = "/Users/minghe/llm4faas/experiments_human_developer/auto_adapt"
# SOURCE_DIR = "/Users/minghe/llm4faas/experiments_human_developer/energy"
# SOURCE_DIR = "/Users/minghe/llm4faas/experiments_human_developer/remote_control"
SOURCE_DIR = "/Users/minghe/llm4faas/experiments_human_developer/plans"

# open_interpreter
# partical...
# SOURCE_DIR = "/Users/minghe/llm4faas/results_open_intepreter"

# repeat-gpt4o
# SOURCE_DIR = "/Users/minghe/llm4faas/experiments_repeat/repeat_functions"

# repeat-gpt4omini
# SOURCE_DIR = '/Users/minghe/llm4faas/experiments_repeat/repeat_functions_4o-mini'



def run_radon_collect_reports(directory):
    output_folder = os.path.join(directory, "radon_reports")
    os.makedirs(output_folder, exist_ok=True)

    for task_name in os.listdir(directory):
        task_path = os.path.join(directory, task_name)
        if os.path.isdir(task_path):
            for exp_name in os.listdir(task_path):
                exp_path = os.path.join(task_path, exp_name)
                if os.path.isdir(exp_path):
                    py_files = [f for f in os.listdir(exp_path) if f.endswith('.py') and f != 'open-interpreter-test.py']

                    if py_files:
                        for py_file in py_files:
                            file_path = os.path.join(exp_path, py_file)
                            absolute_path = os.path.abspath(file_path)
                            relative_path = os.path.relpath(file_path, PROJECT_ROOT)

                            report_filename = f"{os.path.splitext(relative_path)[0].replace(os.sep, '_')}.txt"
                            report_path = os.path.join(output_folder, report_filename)

                            print(f"Analyzing {absolute_path} with Radon...")
                            raw_result = subprocess.run(["radon", "raw", absolute_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


                            cc_result = subprocess.run(["radon", "cc", absolute_path, "-a"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                            mi_result = subprocess.run(["radon", "mi", "-s", absolute_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                            halstead_result = subprocess.run(["radon", "hal", absolute_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                            with open(report_path, "w", encoding="utf-8") as report_file:
                                report_file.write("=== Raw Metrics ===\n")
                                report_file.write(raw_result.stdout + "\n")
                                report_file.write(raw_result.stderr + "\n")

                                report_file.write("=== Cyclomatic Complexity (CC) ===\n")
                                report_file.write(cc_result.stdout + "\n")
                                report_file.write(cc_result.stderr + "\n")

                                report_file.write("=== Maintainability Index (MI) ===\n")
                                report_file.write(mi_result.stdout + "\n")
                                report_file.write(mi_result.stderr + "\n")

                                report_file.write("=== Halstead Metrics ===\n")
                                report_file.write(halstead_result.stdout + "\n")
                                report_file.write(halstead_result.stderr + "\n")

                            print(f"Analysis completed. Report saved to {report_path}")



def run_radon(directory):
    # create radon_reports dir
    output_folder = os.path.join(directory, "radon_reports")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                absolute_path = os.path.abspath(file_path)
                relative_path = os.path.relpath(file_path, PROJECT_ROOT)
                report_filename = f"{os.path.splitext(relative_path)[0].replace(os.sep, '_')}.txt"
                report_path = os.path.join(output_folder, report_filename)

                print(f"Analyzing {absolute_path} with Radon...")
                raw_result = subprocess.run(["radon", "raw", absolute_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                cc_result = subprocess.run(["radon", "cc", absolute_path, "-a"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                mi_result = subprocess.run(["radon", "mi", "-s", absolute_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                # halstead_result = subprocess.run(["radon", "hal", "-f", absolute_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                halstead_result = subprocess.run(["radon", "hal", absolute_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                with open(report_path, "w", encoding="utf-8") as report_file:
                    report_file.write("=== Raw Metrics ===\n")
                    report_file.write(raw_result.stdout + "\n")
                    report_file.write(raw_result.stderr + "\n")

                    report_file.write("=== Cyclomatic Complexity (CC) ===\n")
                    report_file.write(cc_result.stdout + "\n")
                    report_file.write(cc_result.stderr + "\n")

                    report_file.write("=== Maintainability Index (MI) ===\n")
                    report_file.write(mi_result.stdout + "\n")
                    report_file.write(mi_result.stderr + "\n")

                    report_file.write("=== Halstead Metrics ===\n")
                    report_file.write(halstead_result.stdout + "\n")
                    report_file.write(halstead_result.stderr + "\n")

                print(f"Analysis completed. Report saved to {report_path}")


if __name__ == "__main__":
    source_directory = os.path.join(PROJECT_ROOT, SOURCE_DIR)
    run_radon(source_directory)
    # run_radon_collect_reports(source_directory)