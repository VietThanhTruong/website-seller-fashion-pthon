import os
import re

TEMPLATE_DIR = 'templates'

# Kiểm tra xem chuỗi có chứa dấu tiếng Việt không
def contains_vietnamese(text):
    return bool(re.search(r'[àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệđìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]', text, re.IGNORECASE))

# Hàm tìm các đoạn text thuần (không nằm trong thẻ HTML) có dấu tiếng Việt và wrap {% trans %} quanh nó
def wrap_vietnamese_text(line):
    # Regex tách text nằm giữa các tag, hoặc text đứng riêng
    # Ý tưởng: tách line thành các phần tag HTML và text bình thường
    parts = re.split(r'(<[^>]+>)', line)  # tách theo thẻ HTML

    for i, part in enumerate(parts):
        # Nếu không phải tag (chứa text thuần)
        if not part.startswith('<'):
            if contains_vietnamese(part) and '{% trans' not in part:
                # Loại bỏ khoảng trắng 2 đầu để không bọc thừa
                trimmed = part.strip()
                if trimmed:
                    # Bọc phần trimmed bằng trans, rồi thay phần gốc trong part
                    # Thay phần trimmed trong part bằng {% trans "trimmed" %}
                    # Giữ lại các khoảng trắng ngoài
                    leading_ws = part[:len(part) - len(part.lstrip())]
                    trailing_ws = part[len(part.rstrip()):]
                    escaped_text = trimmed.replace('"', '\\"')
                    wrapped = f'{leading_ws}{{% trans "{escaped_text}" %}}{trailing_ws}'
                    parts[i] = wrapped
    return ''.join(parts)

for root, dirs, files in os.walk(TEMPLATE_DIR):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            changed = False
            new_lines = []
            for line in lines:
                # Bỏ qua nếu có sẵn trans/blocktrans
                if '{% trans' in line or '{% blocktrans' in line:
                    new_lines.append(line)
                    continue

                new_line = wrap_vietnamese_text(line)
                if new_line != line:
                    changed = True
                new_lines.append(new_line)
            if changed:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                print(f'Updated: {filepath}')
