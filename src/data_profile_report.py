# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 23:38:36 2024

@author: JADEE
"""
#create profile report

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import os
from ydata_profiling import ProfileReport
import chardet

# 데이터 폴더 경로 설정
data_folder = '../data_utf8/'
output_folder = '../1-2. data_profile/'
os.makedirs(output_folder, exist_ok=True)

# 한글 폰트 설정 (예: Windows에서 'Malgun Gothic' 사용)
plt.rc('font', family='Malgun Gothic')  # Windows
# plt.rc('font', family='AppleGothic')  # MacOS의 경우
# plt.rc('font', family='NanumGothic')  # Linux의 경우

# Unicode minus 처리 (마이너스 기호 깨짐 방지)
plt.rcParams['axes.unicode_minus'] = False

# 폴더 내 모든 파일 순회
for filename in os.listdir(data_folder):
    # CSV 파일만 선택
    if filename.endswith('.csv'):
        file_path = os.path.join(data_folder, filename)

        # 저장할 HTML 파일 경로 설정
        output_path = os.path.join(output_folder, f"{filename[:-4]}_profiling_report.html")

        # 파일이 이미 존재하면 건너뜀
        if os.path.exists(output_path):
            print(f"Report for {filename} already exists. Skipping.")
            continue

        # 인코딩 자동 감지
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read(10000))  # 처음 10000바이트로 인코딩 추정
            encoding = result['encoding']

        # CSV 파일 불러오기
        try:
            data = pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError:
            print(f"Failed to read {filename} with encoding {encoding}. Skipping.")
            continue

        # 프로파일링 리포트 생성
        profile = ProfileReport(data, title=f"Data Profiling Report for {filename}")

        # 결과 HTML로 저장
        profile.to_file(output_path)
        print(f"Generated profiling report for {filename} in {output_folder}")

        # 시각화 예제 (테스트용)
        #plt.figure(figsize=(10, 5))
        #data.plot(kind='bar')
        #plt.title(f"{filename} 데이터 시각화")
        #plt.show()