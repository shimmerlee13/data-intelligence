import pandas as pd
import chardet
import glob
import os

# 1. CSV 파일 목록 가져오기
file_paths = glob.glob("../data/*.csv")

# 2. 변환된 파일을 저장할 폴더 경로 설정
output_folder = "../data_utf8"

# 변환된 파일을 저장할 폴더가 없으면 생성
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 3. 각 파일의 인코딩을 감지하고 UTF-8로 변환하여 새로운 폴더에 저장
for file in file_paths:
    # 파일명 추출 (경로 포함)
    file_name = os.path.basename(file)  # 파일명만 가져옴

    # 1. 파일의 인코딩 감지
    with open(file, 'rb') as f:
        result = chardet.detect(f.read(10000))  # 파일의 일부를 읽어 인코딩 감지
        encoding = result['encoding']

    # 2. 감지된 인코딩으로 파일 읽기
    try:
        df = pd.read_csv(file, encoding=encoding)
    except Exception as e:
        print(f"Error reading {file_name}: {e}")
        continue  # 문제 발생 시 해당 파일 건너뜀

    # 3. 변환된 파일을 새로운 폴더에 UTF-8로 저장
    output_file_path = os.path.join(output_folder, file_name)
    try:
        df.to_csv(output_file_path, encoding='utf-8', index=False)
        print(f"Converted {file_name} to UTF-8 and saved to {output_folder}")
    except Exception as e:
        print(f"Error saving {file_name}: {e}")