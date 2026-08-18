import os
import shutil
import ast

home_folder = "/Users/minghe/llm4faas/tinyFaaS/test/fns/llm/home"
# gpt4o-zh
source_folder = "/Users/minghe/llm4faas/experiments_default/functions_zh/gpt4o_functions" 

destination_root = "./"
os.makedirs(destination_root, exist_ok=True)

for filename in os.listdir(source_folder):
    if filename.endswith(".py"): 
        file_path = os.path.join(source_folder, filename)

        folder_name = os.path.splitext(filename)[0]
        folder_path = os.path.join(destination_root, folder_name)

        os.makedirs(folder_path, exist_ok=True)
        shutil.copytree(home_folder, os.path.join(folder_path, "home"), dirs_exist_ok=True)

        new_fn_path = os.path.join(folder_path, "fn.py")
        shutil.copy(file_path, os.path.join(folder_path, "fn.py"))

        requirement_path = os.path.join(folder_path, "requirements.txt")
        with open(requirement_path, "w", encoding="utf-8") as f:
            pass  

        with open(new_fn_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        inserted_fn = False 

        for line in lines:
            stripped_line = line.strip()
            if stripped_line == 'if __name__ == "__main__":':
                new_lines.append("# " + line)
                if not inserted_fn:
                    new_lines.append("def fn(data, headers):\n")  
                    inserted_fn = True
            else:
                new_lines.append(line)

        if not inserted_fn:
            new_lines.insert(0, "def fn(data, headers):\n\n")

        with open(new_fn_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        print(f"Processed {filename} -> {folder_path}")

print("All Done!")
