import re

def extract_metadata(text):
    pattern = r'^![0-9]+\s=\s.*'
    result = re.findall(pattern, text, re.MULTILINE)
    result_str = '\n'.join(result)
    return result_str

def remove_debug_lines(text):
    # 定义正则表达式模式，匹配以!开头，接着一个或多个数字，然后一个等号
    pattern = r'^![0-9]+ = .*?$'
    
    # 使用re.MULTILINE标志以支持多行匹配
    # 将所有匹配的行替换为空字符串，然后去掉多余的换行符
    filtered_text = re.sub(pattern, '', text, flags=re.MULTILINE)
    
    # 去掉多余的换行符
    filtered_text = '\n'.join(line for line in filtered_text.split('\n') if line.strip() != '')
    
    return filtered_text

