import os
from pathlib import Path

def get_project_structure(base_path):
    project_structure = []

    for root, dirs, files in os.walk(base_path):
        level = root.replace(base_path, '').count(os.sep)
        indent = ' ' * 4 * level
        project_structure.append(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            project_structure.append(f"{subindent}{f}")
    
    return '\n'.join(project_structure)

def extract_functions_and_classes(file_path):
    functions_and_classes = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith('def '):
                function_name = line.split('(')[0].replace('def ', '')
                functions_and_classes.append(f"    - {function_name}")
            elif line.startswith('class '):
                class_name = line.split(':')[0].replace('class ', '')
                functions_and_classes.append(f"    - {class_name}")
    return functions_and_classes

def generate_detailed_structure(base_path):
    detailed_structure = []

    for root, dirs, files in os.walk(base_path):
        level = root.replace(base_path, '').count(os.sep)
        indent = ' ' * 4 * level
        detailed_structure.append(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            file_path = os.path.join(root, f)
            detailed_structure.append(f"{subindent}{f}")
            if f.endswith('.py'):
                functions_and_classes = extract_functions_and_classes(file_path)
                for item in functions_and_classes:
                    detailed_structure.append(f"{subindent}{item}")
    
    return '\n'.join(detailed_structure)

# プロジェクトのベースパスを指定
base_path = str(Path(__file__).parent)

# プロジェクト構造を生成
project_structure = generate_detailed_structure(base_path)

# 結果を表示
print(project_structure)
