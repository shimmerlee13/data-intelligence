# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 15:28:39 2024

@author: shimm
"""
import pandas as pd
import numpy as np

# 1. 데이터 로드
file_path = "../../1-1. describe_result/statistics/summary_statistics_with_classification2.csv"  # 데이터 파일 경로
df = pd.read_csv(file_path)
df = df[df['컬럼구분']=='범주형']

# 2. 필요한 범주형 통계 컬럼 필터링
statistics_columns = [
    '유일값 수', '최빈값_범주(mode)', '범주 집합', 'null 수', '값 중복도 평균'
]

metadata_columns = ['대분류', '파일명', '컬럼명']  # 추가적인 메타정보 컬럼
filtered_df = df[metadata_columns + statistics_columns]

# 2-1. 범주 집합 데이터를 문자열 -> 집합 형태로 변환
filtered_df['범주 집합'] = filtered_df['범주 집합'].apply(eval)  # 문자열을 실제 집합으로 변환

# 3. Jaccard 유사도 계산 함수
def jaccard_similarity(set1, set2):
    """두 집합(set1, set2)의 Jaccard 유사도를 계산."""
    if not set1 and not set2:  # 두 집합이 모두 비어있는 경우 유사도는 1
        return 1
    elif not set1 or not set2:  # 하나만 비어있는 경우 유사도는 0
        return 0
    return len(set1 & set2) / len(set1 | set2)  # 교집합 크기 / 합집합 크기


# 종합 점수 계산을 위한 함수 정의
def combined_similarity(set1, set2, value1, value2, mode1, mode2, weights):
    """
    세 가지 요소 (범주 집합, 값 중복도 평균, 최빈값) 기반 유사도를 계산하고 종합 점수를 반환.
    """
    # 1. 범주 집합 유사도 (Jaccard 유사도)
    jaccard = jaccard_similarity(set1, set2)
    
    # 2. 값 중복도 평균 유사도 (절대값 차이 기반)
    max_range = max(value1, value2, 1)  # max_range가 0이 되는 상황 방지
    value_similarity = 1 - abs(value1 - value2) / max_range
    
    # 3. 최빈값 유사도 (문자열 비교)
    mode_similarity = 1 if mode1 == mode2 else 0

    # 4. 가중치 기반 종합 점수 계산
    combined_score = (
        weights['jaccard'] * jaccard +
        weights['value'] * value_similarity +
        weights['mode'] * mode_similarity
    )

    return combined_score

# 가중치 설정 (사용자 정의 가능)
weights = {'jaccard': 0.8, 'value': 0.1, 'mode': 0.1}

# 종합 유사도 계산
combined_similarity_scores = []
combined_similarity_counts = []

for i in range(len(filtered_df)):
    current_set = filtered_df.iloc[i]['범주 집합']
    current_value = filtered_df.iloc[i]['값 중복도 평균']
    current_mode = filtered_df.iloc[i]['최빈값_범주(mode)']
    current_unique_value_count = filtered_df.iloc[i]['유일값 수']  # 유일값 수 확인

    # 유일값 수가 5 이하인 경우
    if current_unique_value_count <= 5:
        combined_similarity_counts.append(0)  # 유사도 수는 0
        combined_similarity_scores.append(0)  # 평균 유사도도 0
        continue  # 유사도 계산 건너뛰기

    count = 0
    total_combined_score = 0
    for j in range(len(filtered_df)):
        if i != j:
            other_set = filtered_df.iloc[j]['범주 집합']
            other_value = filtered_df.iloc[j]['값 중복도 평균']
            other_mode = filtered_df.iloc[j]['최빈값_범주(mode)']

            # 종합 유사도 계산
            combined_score = combined_similarity(
                current_set, other_set,
                current_value, other_value,
                current_mode, other_mode,
                weights
            )

            # 임계값 조건 설정 (예: 0.5 이상만 카운트)
            if combined_score > 0.5:
                count += 1
                total_combined_score += combined_score

    # 평균 유사도 저장
    combined_similarity_counts.append(count)
    combined_similarity_scores.append(total_combined_score / count if count > 0 else 0)

# 결과를 DataFrame에 추가
filtered_df['종합 유사도 수'] = combined_similarity_counts
filtered_df['종합 평균 유사도'] = combined_similarity_scores
filtered_df = filtered_df[filtered_df['유일값 수']>=5]
filtered_df = filtered_df[filtered_df['종합 유사도 수']>0] #73개
filtered_df['범주 집합'] = filtered_df['범주 집합'].apply(lambda x: list(x)[:10])

# 공통속성 정렬 및 저장
filtered_df_sorted = filtered_df.sort_values(by='종합 평균 유사도', ascending=False)
filtered_df_sorted = filtered_df_sorted[filtered_df_sorted['종합 유사도 수']>=3]
filtered_df_sorted = filtered_df_sorted[filtered_df_sorted['종합 평균 유사도']>0.71]

# 파일 저장
output_path_df = "../../1-1. describe_result/similarity/similarity_calculate/similarity_cat_common.csv"
filtered_df_sorted.to_csv(output_path_df, index=False, encoding='utf-8-sig')

print(f"종합 유사도 결과 데이터프레임이 '{output_path_df}'에 저장되었습니다.")
