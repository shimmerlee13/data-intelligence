# summary_statistics_with_classification.csv에 기반하여 PK/FK 후보를 탐색한 후,
# 실제 CSV 파일 데이터를 불러와서 일치율을 계산하고
# PK와 FK 관계를 검증


import pandas as pd
import numpy as np
import glob

# 1. (수정필요) 대표속성, 공통속성 데이터 로드
#df_summary = pd.read_csv('../../1-1. describe_result/statistics/summary_statistics_with_classification.csv')

# 2. 수치형 및 범주형 컬럼 리스트 정의
numerical_cols = ['null 수', '유일값 수', '값 중복도 평균', '최댓값', '최솟값', '평균(mean)',
                  '중앙값(median)', '1분위수(1Q)', '3분위수(3Q)', 'IQR', '분산(variance)',
                  '표준편차(standard deviation)', '범위(range)', '왜도(skewness)', '첨도(kurtosis)']
categorical_cols = ['대분류', '소분류', '파일명', '최빈값(mode)']

# 3. 파일 리스트 불러오기
file_paths = glob.glob("../../data_utf8/*.csv")

# 4. 대표 속성(PK 후보) 찾기
pk_candidates = {}

for file_name in df_summary['파일명'].unique():
    file_data = df_summary[df_summary['파일명'] == file_name]
    pk_cols = file_data[(file_data['유일값 수'] == file_data['유일값 수'].max()) &
                        (file_data['null 수'] == 0)]
    if not pk_cols.empty:
        pk_candidates[file_name] = pk_cols['컬럼명'].values.tolist()

print("PK 후보:", pk_candidates)

# 5. 공통 속성(FK 후보) 찾기
common_columns = df_summary.groupby('컬럼명').filter(lambda x: x['대분류'].nunique() == df_summary['대분류'].nunique())
common_column_names = common_columns['컬럼명'].unique()

print("공통 속성(FK 후보):", common_column_names)

# 6. 실제 데이터 로드 및 PK/FK 관계 체크
fk_candidates = {}

for file_path in file_paths:
    file_name = file_path.split("\\")[-1]  # 경로에서 파일명 추출
    if file_name not in pk_candidates:
        continue  # PK 후보가 없는 파일은 건너뜁니다

    # CSV 파일 로드
    df = pd.read_csv(file_path)

    # PK 후보 컬럼 추출
    for pk_col in pk_candidates[file_name]:
        for common_col in common_column_names:
            # 공통 속성이 실제 데이터에 있는지 확인
            if pk_col in df.columns and common_col in df.columns:
                # 일치율 계산
                match_rate = np.mean(df[pk_col].isin(df[common_col]))
                if match_rate > 0.8:  # 80% 이상의 일치율을 FK 관계로 가정
                    fk_candidates[(file_name, pk_col)] = common_col

print("FK 후보:", fk_candidates)

# 결과 출력
print("PK 후보 컬럼:", pk_candidates)
print("FK 후보 컬럼:", fk_candidates)
