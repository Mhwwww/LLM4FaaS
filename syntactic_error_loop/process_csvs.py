import csv
import os

def clean_malformed_csv(input_path,output_path, expected_fields=9):
    # output_path = input_path.replace(".csv", "_fixed.csv")
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(output_path, 'w', encoding='utf-8') as f_out:
        header = lines[0].strip()
        f_out.write(header + '\n')

        for line in lines[1:]:
            # extract error_msgs
            parts = line.strip('\n').split(',', 8)
            if len(parts) < 9:
                print(line)
                print(f"!!! format error !!! : {line[:60]} {line}")
                continue

            # cleanup error_msgs
            error_msg = parts[8].replace('"', "'").replace('\r', '').replace('\n', '\\n')
            error_msg = f'"{error_msg}"'

            f_out.write(','.join(parts[:8]) + ',' + error_msg + '\n')

    print(f"------Fixed and write to------: {output_path}")

if __name__ == '__main__':
    input_dir = '/Users/minghe/llm4faas/syntactic_error_loop/csvs/zh'
    output_dir = '/Users/minghe/llm4faas/syntactic_error_loop/csvs/new/zh'
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith('.csv'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            clean_malformed_csv(input_path, output_path)