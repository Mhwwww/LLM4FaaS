import os
import re

def process_js_file(file_path):
    print(f"[START] Process {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # find main block
    has_main_block = any('if (require.main === module)' in line and not line.startswith('//') for line in lines)
    has_module_exports = any('module.exports' in line and not line.strip().startswith('//') for line in lines)

    new_lines = []
    inside_exports_block = False

    if has_main_block:
        print(f"Found main block in {file_path}, processing...")
        for line in lines:
            if 'if (require.main === module)' in line:
                new_lines.append("// " + line)
                add_line = line.replace('if (require.main === module)',
                                        'module.exports = (req, res) =>')  # comment out if (require.main === module)
                new_lines.append(add_line)  # add FaaS 

                continue

            # comment out module.exports
            if 'module.exports' in line:
                if '{' in line and '};' not in line:
                    new_lines.append('// ' + line)
                    inside_exports_block = True
                    continue
                # else:  # add module.exports
                new_lines.append('// ' + line)
                continue

            if inside_exports_block:
                new_lines.append('// ' + line)
                if '};' in line:
                    inside_exports_block = False
                continue
            new_lines.append(line)

    else:
        print(f"Not found main block in {file_path}, processing...")
        has_export_statement = False
        for line in lines:
            if 'module.exports =' in line:
                has_export_statement = True
                new_lines.append("// " + line)
                new_lines.append(line.replace('module.exports =', 'module.exports = (req, res) =>'))
                continue

            new_lines.append(line)
        if not has_module_exports and not has_export_statement:
            new_lines.append("\nmodule.exports = (req, res) => { main(); }\n")
            print("Added default: module.exports = (req, res) => { main(); }")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)


    print(f'[DONE] Processed {file_path}')

def convert_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.js'):
            process_js_file(os.path.join(folder_path, filename))

if __name__ == '__main__':
    target_folder = '/Users/minghe/llm4faas/experiments_js/output/'
    convert_folder(target_folder)
