# 카테고리 범주 집합을 가지고 타 컬럼과의 유사도 비교
# 높을수록 공통속성의 값을 가

import pandas as pd
import numpy as np

# 1. 데이터 로드
file_path = "../../1-1. describe_result/statistics/summary_statistics_with_classification2.csv"  # 데이터 파일 경로
df = pd.read_csv(file_path)
df = df[df['컬럼구분']=='범주형']

# 2. 필요한 범주형 통계 컬럼 필터링
statistics_columns = [
    '유일값 수', '범주값 변화(고정/가변)', '최빈값_범주(mode)', '범주 집합', 'null 수', '값 중복도 평균'
]

metadata_columns = ['대분류', '파일명', '컬럼명']  # 추가적인 메타정보 컬럼
filtered_df = df[metadata_columns + statistics_columns].dropna()  # 필요한 컬럼만 선택

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


# 3-1. Jaccard 유사도 기반 유사도 계산
jaccard_similarity_counts = []
jaccard_similarity_scores = []  # 각 컬럼별 Jaccard 평균 유사도 저장

for i in range(len(filtered_df)):
    current_set = filtered_df.iloc[i]['범주 집합']
    count = 0
    total_similarity = 0
    for j in range(len(filtered_df)):
        if i != j:
            other_set = filtered_df.iloc[j]['범주 집합']
            similarity = jaccard_similarity(current_set, other_set)  # Jaccard 유사도 계산
            if similarity > 0.5:  # 유사도의 임계값 설정 (예: 0.5)
                count += 1
                total_similarity += similarity
    jaccard_similarity_counts.append(count)
    jaccard_similarity_scores.append(total_similarity / count if count > 0 else 0)

# 4. 문자열 기반 직접 비교 (범주값 변화, 최빈값)
category_similarity_counts = []
mode_similarity_counts = []

for i in range(len(filtered_df)):
    current_category_change = filtered_df.iloc[i]['범주값 변화(고정/가변)']
    current_mode = filtered_df.iloc[i]['최빈값_범주(mode)']
    category_count = 0
    mode_count = 0
    for j in range(len(filtered_df)):
        if i != j:
            other_category_change = filtered_df.iloc[j]['범주값 변화(고정/가변)']
            other_mode = filtered_df.iloc[j]['최빈값_범주(mode)']

            # 범주값 변화 비교
            if current_category_change == other_category_change:
                category_count += 1

            # 최빈값 비교
            if current_mode == other_mode:
                mode_count += 1

    category_similarity_counts.append(category_count)
    mode_similarity_counts.append(mode_count)

# 5. 결과를 DataFrame에 추가
filtered_df['Jaccard 유사도 수'] = jaccard_similarity_counts
filtered_df['Jaccard 평균 유사도'] = jaccard_similarity_scores
filtered_df['범주값 변화 유사도 수'] = category_similarity_counts
filtered_df['최빈값 유사도 수'] = mode_similarity_counts

# 6. 정렬 및 저장
filtered_df_sorted = filtered_df.sort_values(by='Jaccard 유사도 수', ascending=False)

# 파일 저장
output_path_df = "../../1-1. describe_result/similarity/similarity_calculate/similarity_categorical_df.csv"  # 저장할 파일 경로
filtered_df_sorted.to_csv(output_path_df, index=False, encoding='utf-8-sig')

print(f"범주형 데이터 유사도 결과 데이터프레임이 '{output_path_df}'에 저장되었습니다.")
