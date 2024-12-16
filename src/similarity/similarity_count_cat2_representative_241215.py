# -*- coding: utf-8 -*-
"""
모든 속성을 포함하고, 각 대분류 내에서 유사도 높은 순으로 정렬
"""
import pandas as pd
import numpy as np

# 1. 데이터 로드
file_path = "../../1-1. describe_result/statistics/summary_statistics_with_classification2.csv"  # 데이터 파일 경로
df = pd.read_csv(file_path)
df = df[df['컬럼구분'] == '범주형']

# 2. 필요한 범주형 통계 컬럼 필터링
statistics_columns = [
    '유일값 수', '최빈값_범주(mode)', '범주 집합', 'null 수', '값 중복도 평균'
]

metadata_columns = ['대분류', '파일명', '컬럼명']  # 추가적인 메타정보 컬럼
filtered_df = df[metadata_columns + statistics_columns]

# 2-1. 범주 집합 데이터를 문자열 -> 집합 형태로 변환
filtered_df['범주 집합'] = filtered_df['범주 집합'].apply(eval)  # 문자열을 실제 집합으로 변환

# Jaccard 유사도 함수
def jaccard_similarity(set1, set2):
    """두 집합(set1, set2)의 Jaccard 유사도를 계산."""
    if not set1 and not set2:
        return 1
    elif not set1 or not set2:
        return 0
    return len(set1 & set2) / len(set1 | set2)

# 가중치 설정
weights = {'jaccard': 0.8, 'value': 0.1, 'mode': 0.1}

# 종합 유사도 함수
def combined_similarity(set1, set2, value1, value2, mode1, mode2, weights):
    jaccard = jaccard_similarity(set1, set2)
    max_range = max(value1, value2, 1)
    value_similarity = 1 - abs(value1 - value2) / max_range
    mode_similarity = 1 if mode1 == mode2 else 0

    combined_score = (
        weights['jaccard'] * jaccard +
        weights['value'] * value_similarity +
        weights['mode'] * mode_similarity
    )
    return combined_score

# 3. 모든 데이터의 유사도 계산
all_attributes = []

categories = filtered_df['대분류'].unique()  # 대분류 목록
for category in categories:
    # 현재 대분류와 다른 대분류 데이터 추출
    current_category_df = filtered_df[filtered_df['대분류'] == category]
    other_categories_df = filtered_df[filtered_df['대분류'] != category]

    for _, row in current_category_df.iterrows():
        current_set = row['범주 집합']
        current_value = row['값 중복도 평균']
        current_mode = row['최빈값_범주(mode)']

        # 같은 대분류와 유사도 계산
        same_category_similarity = 0
        for _, other_row in current_category_df.iterrows():
            if row['컬럼명'] != other_row['컬럼명']:
                score = combined_similarity(
                    current_set, other_row['범주 집합'],
                    current_value, other_row['값 중복도 평균'],
                    current_mode, other_row['최빈값_범주(mode)'],
                    weights
                )
                same_category_similarity += score

        # 다른 대분류와의 유사도 계산
        different_category_similarity = 0
        for _, other_row in other_categories_df.iterrows():
            score = combined_similarity(
                current_set, other_row['범주 집합'],
                current_value, other_row['값 중복도 평균'],
                current_mode, other_row['최빈값_범주(mode)'],
                weights
            )
            different_category_similarity += score

        # 평균 유사도 계산
        same_category_avg = same_category_similarity / len(current_category_df) if len(current_category_df) > 0 else 0
        different_category_avg = different_category_similarity / len(other_categories_df) if len(other_categories_df) > 0 else 0

        # 모든 속성 결과 저장
        all_attributes.append({
            '대분류': category,
            '파일명': row['파일명'],
            '컬럼명': row['컬럼명'],
            '유일값 수': row['유일값 수'],
            '범주 집합': row['범주 집합'],
            '같은 대분류 평균 유사도': same_category_avg,
            '다른 대분류 평균 유사도': different_category_avg,
            '유사도 차이': same_category_avg - different_category_avg
        })

# 모든 속성 결과를 DataFrame으로 변환
all_attributes_df = pd.DataFrame(all_attributes)
all_attributes_df['범주 집합'] = all_attributes_df['범주 집합'].apply(lambda x: list(x)[:10])

# 4. 대분류별 정렬
all_attributes_df_sorted = all_attributes_df.sort_values(
    by=['대분류', '같은 대분류 평균 유사도', '다른 대분류 평균 유사도'], ascending=[True, False, False]
)


# 파일 저장
output_path_rep = "../../1-1. describe_result/similarity/similarity_calculate/similarity_cat_representative.csv"
all_attributes_df_sorted.to_csv(output_path_rep, index=False, encoding='utf-8-sig')

print(f"대표 속성 결과 데이터프레임이 '{output_path_rep}'에 저장되었습니다.")
