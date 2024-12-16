# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 22:57:57 2024

@author: JADEE
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import cosine
import numpy as np

# 1. 데이터 로드
file_path = "../../1-1. describe_result/statistics/summary_statistics_with_classification2.csv"  # 데이터 파일 경로
df = pd.read_csv(file_path)

# 2. 필요한 통계 수치 컬럼 필터링
statistics_columns = [
    'null 수', '최댓값', '최솟값', '평균(mean)', '중앙값(median)', '최빈값_수치(mode)', '1분위수(1Q)', '3분위수(3Q)', 'IQR',
    '분산(variance)', '표준편차(standard deviation)', '범위(range)', '왜도(skewness)', '첨도(kurtosis)',
    '유일값 수', '값 중복도 평균'
]

metadata_columns = ['대분류', '파일명', '컬럼명', '컬럼구분']  # 추가적인 메타정보 컬럼
filtered_df = df[metadata_columns + statistics_columns].dropna()  # 필요한 컬럼만 선택

# 3. 통계 수치 정규화
scaler = StandardScaler()
statistics_scaled = scaler.fit_transform(filtered_df[statistics_columns])

# 4. 유사도 계산
similarity_counts = []
similar_column_names = []  # 유사한 컬럼명을 저장할 리스트

for i in range(len(statistics_scaled)):
    current_vector = statistics_scaled[i]
    count = 0
    similar_columns = set()  # 현재 컬럼과 유사한 컬럼명을 저장할 집합
    for j in range(len(statistics_scaled)):
        if i != j:  # 자기 자신과는 비교하지 않음
            other_vector = statistics_scaled[j]
            similarity = 1 - cosine(current_vector, other_vector)
            if similarity > 0.9:  # 유사도의 임계값 설정 (예: 0.9)
                count += 1
                similar_columns.add(filtered_df.iloc[j]['컬럼명'])  # 유사한 컬럼명 추가
    similarity_counts.append(count)
    similar_column_names.append(similar_columns)  # 유사한 컬럼명을 저장

# 5. 결과를 새로운 컬럼으로 추가
filtered_df['유사도 수'] = similarity_counts
filtered_df['유사한 컬럼명'] = similar_column_names

# 6. 유사도 수가 많은 순으로 정렬
filtered_df_sorted = filtered_df.sort_values(by='유사도 수', ascending=False)

# 7. 대표속성 계산
representative_attributes = []

# 각 대분류별로 대표속성을 선정
categories = filtered_df_sorted['대분류'].unique()
for category in categories:
    # 현재 카테고리 데이터 추출
    category_df = filtered_df_sorted[filtered_df_sorted['대분류'] == category]

    # 다른 카테고리 데이터 추출
    other_df = filtered_df_sorted[filtered_df_sorted['대분류'] != category]

    # 현재 카테고리에서 대표속성 후보 리스트 생성
    candidates = []
    for _, row in category_df.iterrows():
        current_column = row['컬럼명']
        current_score = row['유사도 수']

        # 다른 카테고리에서 해당 컬럼의 유사도 수 확인
        in_other_score = other_df[other_df['컬럼명'] == current_column]['유사도 수'].sum()

        # 조건: 다른 카테고리에서는 유사도 수가 낮아야 함
        if in_other_score == 0:  # 다른 카테고리에서 유사도가 없을 때
            candidates.append({'컬럼명': current_column, '유사도 수': current_score})

    # 유사도 수 기준으로 정렬
    candidates = sorted(candidates, key=lambda x: x['유사도 수'], reverse=True)

    # 대표속성 저장 (카테고리와 모든 후보 속성을 함께 저장)
    representative_attributes.append({'카테고리': category, '속성 리스트': candidates})

# 8. 공통속성 계산
# 여러 카테고리에 걸쳐 유사도 수가 일정 임계값 이상인 컬럼 선정
threshold = 10  # 임계값 예시
common_attributes = filtered_df_sorted[
    filtered_df_sorted['유사도 수'] >= threshold
]['컬럼명'].unique().tolist()

# 9. 결과 출력
print("대표속성 리스트:")
for attr in representative_attributes:
    print(f"카테고리: {attr['카테고리']}")
    for candidate in attr['속성 리스트']:
        print(f"  속성: {candidate['컬럼명']}, 유사도 수: {candidate['유사도 수']}")

print("공통속성:", common_attributes)