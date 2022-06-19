import os
in_dir = r"D:\Data\speech\Buckeye\original"

for f in os.listdir(in_dir):
    if not f.endswith('.words'):
        continue
    file_path = os.path.join(in_dir, f)
    lines = []
    print(file_path)
    with open(file_path, 'r', encoding='utf8') as f:
        for line in f:
            line = line.rstrip()
            if not line:
                continue
            print(repr(line))
            if line.count(';') == 3:
                line = ';'.join(line.split(';')[:-1])
                line = line.rstrip()
            lines.append(line)
    #error
    with open(file_path, 'w', encoding='utf8', newline='') as f:
        for line in lines:
            f.write(f"{line}\n")