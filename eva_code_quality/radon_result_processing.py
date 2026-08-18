import os
import re
import csv

# gpt4o
# folders = ["/Users/minghe/llm4faas/experiments_default/functions_zh/gpt4o_functions/radon_reports/"]
# output_csv = os.path.join('/Users/minghe/llm4faas/eva/_results_ic2e/radon' ,"gpt4o.csv")

# human
# folders = [
#     "/Users/minghe/llm4faas/experiments_human_developer/auto_adapt/radon_reports",
#     "/Users/minghe/llm4faas/experiments_human_developer/energy/radon_reports",
#     "/Users/minghe/llm4faas/experiments_human_developer/plans/radon_reports",
#     "/Users/minghe/llm4faas/experiments_human_developer/remote_control/radon_reports"
# ]
# output_csv = os.path.join('/Users/minghe/llm4faas/eva/_results_ic2e/radon' ,"human.csv")

# baseline
folders = [
    "/Users/minghe/llm4faas/experiments_baseline_v2/baseline_v2_functions_zh/auto_adapt/radon_reports",
    "/Users/minghe/llm4faas/experiments_baseline_v2/baseline_v2_functions_zh/energy/radon_reports",
    "/Users/minghe/llm4faas/experiments_baseline_v2/baseline_v2_functions_zh//plans/radon_reports",
    "/Users/minghe/llm4faas/experiments_baseline_v2/baseline_v2_functions_zh//remote_control/radon_reports"
]
output_csv = os.path.join('/Users/minghe/llm4faas/eva/_results_ic2e/radon' ,"baseline.csv")

# oi
# folders = ["/Users/minghe/llm4faas/results_open_intepreter/radon_reports"]
# output_csv = os.path.join('/Users/minghe/llm4faas/eva/_results_ic2e/radon', "oi.csv")

cc_pattern = re.compile(r"Average complexity: \w+ \(([\d.]+)\)")
mi_pattern = re.compile(r"- \w+ \(([\d.]+)\)")
hals_pattern = re.compile(r"effort:\s*([\d.]+)")

results = []

for folder_path in folders:
    if not os.path.exists(folder_path):
        print(f"!!!Folder {folder_path} Does Not Exitst!!! Pass")
        continue

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"): 
            file_path = os.path.join(folder_path, filename)

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

                cc_average = None
                mi_value = None
                total_hals_effort = 0.0

                match = cc_pattern.search(content)
                if match:
                    cc_average = match.group(1)

                match = mi_pattern.search(content)
                if match:
                    mi_value = match.group(1)

                efforts = hals_pattern.findall(content)
                if efforts:
                    total_hals_effort = sum(map(float, efforts))

                results.append({
                    "absolute_path": file_path,
                    "cc_average": cc_average,
                    "mi_value": mi_value,
                    "hals_effort": total_hals_effort
                })

with open(output_csv, "w", newline='', encoding="utf-8") as csvfile:
    fieldnames = ["absolute_path", "cc_average", "mi_value", "hals_effort"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()  
    writer.writerows(results)

print(f"Results: {output_csv}")