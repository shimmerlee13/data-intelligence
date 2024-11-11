import pandas as pd

# 통계 요약 데이터 파일 경로와 대분류 및 소분류 정보 파일 경로 설정
summary_file_path = "../../data_parsing/statistics/summary_statistics.csv"
classification_file_path = "../../data_parsing/statistics/classification_data.csv"  # 대분류 및 소분류 정보 CSV 파일

# CSV 파일 로드
summary_df = pd.read_csv(summary_file_path)
classification_df = pd.read_csv(classification_file_path)

# 대분류와 소분류 정보를 병합하기 위한 새로운 컬럼 초기화
summary_df['대분류'] = ""
summary_df['소분류'] = ""

# 파일명이 포함되는지 확인하여 대분류 및 소분류 정보 추가
for idx, row in classification_df.iterrows():
    keyword = row['파일명']  # 분류 파일명에서 검색할 키워드 추출
    if isinstance(keyword, str):  # keyword가 문자열인지 확인
        # 파일명에 키워드 포함 여부 확인, regex=False로 정규식 해석 비활성화
        mask = summary_df['파일명'].str.contains(keyword, na=False, regex=False)
        summary_df.loc[mask, '대분류'] = row['대분류']
        summary_df.loc[mask, '소분류'] = row['소분류']

# 결과 CSV 파일로 저장
output_file_path = "../../data_parsing/statistics/summary_statistics_with_classification.csv"
summary_df.to_csv(output_file_path, index=False, encoding='utf-8-sig')

print("Merged file saved to:", output_file_path)