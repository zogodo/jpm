import re
import os

INPUT_FILE = "《金瓶梅词话》兰陵笑笑生（万历本）.txt"
OUTPUT_DIR = "chapters"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    text = f.read()

pattern = r'(第.+章：[^\n]+)'
matches = list(re.finditer(pattern, text))

if not matches:
    print("No chapters found!")
    exit(1)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Handle duplicate chapter numbers: the second occurrence of 第十二章 should be 第十三章
seen = {}
for i, m in enumerate(matches):
    title = m.group()
    # Extract chapter number from Chinese
    num_match = re.search(r'第(.+?)章', title)
    if num_match:
        num_str = num_match.group(1)
        if num_str in seen:
            # This is the duplicate - replace with next number
            # Convert Chinese number to integer, add 1, convert back
            cn_nums = {
                '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
                '十一': 11, '十二': 12, '十三': 13, '十四': 14,
                '十五': 15, '十六': 16, '十七': 17, '十八': 18,
                '十九': 19, '二十': 20, '二十一': 21, '二十二': 22,
                '二十三': 23, '二十四': 24, '二十五': 25, '二十六': 26,
                '二十七': 27, '二十八': 28, '二十九': 29, '三十': 30,
                '三十一': 31, '三十二': 32, '三十三': 33, '三十四': 34,
                '三十五': 35, '三十六': 36, '三十七': 37, '三十八': 38,
                '三十九': 39, '四十': 40, '四十一': 41, '四十二': 42,
                '四十三': 43, '四十四': 44, '四十五': 45, '四十六': 46,
                '四十七': 47, '四十八': 48, '四十九': 49, '五十': 50,
                '五十一': 51, '五十二': 52, '五十三': 53, '五十四': 54,
                '五十五': 55, '五十六': 56, '五十七': 57, '五十八': 58,
                '五十九': 59, '六十': 60, '六十一': 61, '六十二': 62,
                '六十三': 63, '六十四': 64, '六十五': 65, '六十六': 66,
                '六十七': 67, '六十八': 68, '六十九': 69, '七十': 70,
                '七十一': 71, '七十二': 72, '七十三': 73, '七十四': 74,
                '七十五': 75, '七十六': 76, '七十七': 77, '七十八': 78,
                '七十九': 79, '八十': 80, '八十一': 81, '八十二': 82,
                '八十三': 83, '八十四': 84, '八十五': 85, '八十六': 86,
                '八十七': 87, '八十八': 88, '八十九': 89, '九十': 90,
                '九十一': 91, '九十二': 92, '九十三': 93, '九十四': 94,
                '九十五': 95, '九十六': 96, '九十七': 97, '九十八': 98,
                '九十九': 99, '一百': 100,
            }
            num = cn_nums.get(num_str)
            if num is not None:
                # Find the correct Chinese number for the actual chapter index
                actual_num = i + 1  # 1-based index
                cn_map = {v: k for k, v in cn_nums.items()}
                corrected_cn = cn_map.get(actual_num, num_str)
                corrected_title = title.replace(f'第{num_str}章', f'第{corrected_cn}章')
                print(f"Duplicate '{title}' at index {i} -> corrected to '{corrected_title}'")
                title = corrected_title
        else:
            seen[num_str] = i

# The first line is title/header, treat it as pre-chapter content
# Each chapter starts at its match position and ends at the next match start
# For the last chapter, it ends at end of file

pre_text = text[:matches[0].start()].strip()

for i, m in enumerate(matches):
    title = matches[i].group()
    # Re-apply correction for duplicates
    num_match = re.search(r'第(.+?)章', title)
    if num_match:
        num_str = num_match.group(1)
        # Check if this is the duplicate (second occurrence of same number)
        count_before = sum(1 for j in range(i) if re.search(r'第(.+?)章', matches[j].group()).group(1) == num_str)
        if count_before > 0:
            cn_nums = {
                '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
                '十一': 11, '十二': 12, '十三': 13, '十四': 14,
                '十五': 15, '十六': 16, '十七': 17, '十八': 18,
                '十九': 19, '二十': 20, '二十一': 21, '二十二': 22,
                '二十三': 23, '二十四': 24, '二十五': 25, '二十六': 26,
                '二十七': 27, '二十八': 28, '二十九': 29, '三十': 30,
                '三十一': 31, '三十二': 32, '三十三': 33, '三十四': 34,
                '三十五': 35, '三十六': 36, '三十七': 37, '三十八': 38,
                '三十九': 39, '四十': 40, '四十一': 41, '四十二': 42,
                '四十三': 43, '四十四': 44, '四十五': 45, '四十六': 46,
                '四十七': 47, '四十八': 48, '四十九': 49, '五十': 50,
                '五十一': 51, '五十二': 52, '五十三': 53, '五十四': 54,
                '五十五': 55, '五十六': 56, '五十七': 57, '五十八': 58,
                '五十九': 59, '六十': 60, '六十一': 61, '六十二': 62,
                '六十三': 63, '六十四': 64, '六十五': 65, '六十六': 66,
                '六十七': 67, '六十八': 68, '六十九': 69, '七十': 70,
                '七十一': 71, '七十二': 72, '七十三': 73, '七十四': 74,
                '七十五': 75, '七十六': 76, '七十七': 77, '七十八': 78,
                '七十九': 79, '八十': 80, '八十一': 81, '八十二': 82,
                '八十三': 83, '八十四': 84, '八十五': 85, '八十六': 86,
                '八十七': 87, '八十八': 88, '八十九': 89, '九十': 90,
                '九十一': 91, '九十二': 92, '九十三': 93, '九十四': 94,
                '九十五': 95, '九十六': 96, '九十七': 97, '九十八': 98,
                '九十九': 99, '一百': 100,
            }
            cn_map = {v: k for k, v in cn_nums.items()}
            actual_num = i + 1
            corrected_cn = cn_map.get(actual_num, num_str)
            title = title.replace(f'第{num_str}章', f'第{corrected_cn}章')

    if i + 1 < len(matches):
        chapter_text = text[m.start():matches[i+1].start()]
    else:
        chapter_text = text[m.start():]

    chapter_text = chapter_text.strip()

    # Remove separator lines like "---..." at boundaries
    lines = chapter_text.split('\n')
    # Remove trailing separator lines
    while lines and re.match(r'^-{3,}$', lines[-1].strip()):
        lines.pop()
    # Remove leading separator lines (after chapter title)
    title_line = lines[0]
    rest = lines[1:]
    while rest and re.match(r'^-{3,}$', rest[0].strip()):
        rest.pop(0)
    chapter_text = title_line + '\n' + '\n'.join(rest)

    # Sanitize filename: remove characters not safe for filenames
    safe_title = re.sub(r'[\\/:*?\"<>|]', '_', title)
    # Use zero-padded number for sorting
    num = i + 1
    filename = f"{num:03d}_{safe_title}.txt"

    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as out:
        out.write(chapter_text)

    print(f"Written: {filename} ({len(chapter_text)} chars)")

# Also write the pre-chapter header content if any
if pre_text:
    with open(os.path.join(OUTPUT_DIR, "000_前言.txt"), "w", encoding="utf-8") as out:
        out.write(pre_text)
    print(f"Written: 000_前言.txt ({len(pre_text)} chars)")

print(f"\nDone! Total chapters: {len(matches)}")
