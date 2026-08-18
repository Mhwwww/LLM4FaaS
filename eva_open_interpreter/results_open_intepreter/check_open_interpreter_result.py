import json
import os
import csv


def process_json_file(task_path, file_path):
    # if has_json, then the json file name is 'response.json'
    python_filename = task_path + '/oi_' + os.path.basename(task_path) + ".py"
    log_filename = task_path + '/oi_' + os.path.basename(task_path) + ".log"

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    code_content = None
    log_content = None

    for entry in data.get("response", []):
        if entry.get("role") == "assistant" and entry.get("type") == "code":
            code_content = entry.get("content")
        elif entry.get("role") == "computer" and entry.get("type") == "console":
            log_content = entry.get("content")

    if code_content:
        with open(python_filename, "w", encoding="utf-8") as code_file:
            code_file.write(code_content)
        print(f"Python Code: {python_filename}")

    if log_content:
        with open(log_filename, "w", encoding="utf-8") as log_file:
            log_file.write(log_content)
        print(f"Log file: {log_filename}")


def check_output_type(task_path):
    files = os.listdir(task_path)

    json_file = next((os.path.join(task_path, f) for f in files if f == "response.json"), None)
    has_json = bool(json_file)

    python_file = next(
        (os.path.join(task_path, f) for f in files if f.endswith(".py") and f != "open-interpreter-test.py"), None)
    has_python = bool(python_file)

    if has_json and has_python:
        # nothing needs to do in this case
        return "BOTH"
    elif has_json:
        process_json_file(task_path, os.path.abspath(json_file))
        return "JSON"
    elif has_python:
        return "PYTHON"
    else:
        return "NONE"



def check_rate_limit_error(task_path):
    file_path = task_path + "/logfile.txt" 

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "RateLimitError" in content or "rate limit reached" in content:
        print("Rate Limit Error detected!")
        return True
    else:
        print("No Rate Limit Error found.")
        return False


def main():
    ROOT_DIR = "."
    output_csv = "task_results.csv"

    if not os.path.exists(ROOT_DIR):
        print(f"Directory '{ROOT_DIR}' does not exist.")
        return

    data = []

    for task_folder in os.listdir(ROOT_DIR):
        if os.path.basename(task_folder) != 'temp':
            task_path = os.path.join(ROOT_DIR, task_folder)
            if os.path.isdir(task_path):
                task_name = os.path.basename(task_folder)
                print(f"Task Name: {task_name}")
                for sub_folder in os.listdir(task_path):
                    sub_folder_path = os.path.join(task_path, sub_folder)
                    if os.path.isdir(sub_folder_path):
                        index = os.path.basename(sub_folder).strip(task_name + "_")
                        print(index)
                        output_type = check_output_type(sub_folder_path)
                        rate_limit = check_rate_limit_error(sub_folder_path)
                        data.append([task_name, index, output_type, rate_limit])


    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["TASK_NAME", "INDEX", "OUTPUT", "RATE_LIMIT_ERROR", "SUCCESS RATE(%)", "STATUS"])
        writer.writerows(data)

    print(f"Results saved to {output_csv}")


if __name__ == "__main__":
    main()
