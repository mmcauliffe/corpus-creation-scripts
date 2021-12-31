import os
cleaned_dir = r'C:\Users\michael\Documents\Dev\mfa-models\dictionary'
temp_dir = r'C:\Users\michael\Documents\Dev\mfa-models\dictionary\temp'
os.makedirs(temp_dir,exist_ok=True)

for fn in os.listdir(cleaned_dir):
    if not fn.endswith('.dict'):
        continue
    line_set = set()
    line_counter = 0
    with open(os.path.join(cleaned_dir, fn), 'r', encoding='utf8') as f:
        for line in f:
            line_counter +=1
            line = line.strip()
            if not line:
                continue
            line_set.add(line)
    with open(os.path.join(cleaned_dir, fn), 'w', encoding='utf8') as f:
        for line in sorted(line_set):
            f.write(line + '\n')
    print(f"Reduced {fn} from {line_counter} to {len(line_set)}")