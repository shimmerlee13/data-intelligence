import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances
from scipy.stats import pearsonr
from scipy.spatial.distance import cosine


# Jaccard 유사도 계산 함수 (범주형 분석용)
def jaccard_similarity(set1, set2):
    if not set1 and not set2:
        return 1
    elif not set1 or not set2:
        return 0
    return len(set1 & set2) / len(set1 | set2)


# 유사도 계산 함수 (수치형 분석용)
def calculate_similarity(current_vector, comparison_vector):
    cosine_sim = 1 - cosine(current_vector, comparison_vector)
    euclidean_sim = 1 / (1 + euclidean_distances([current_vector], [comparison_vector])[0][0])
    pearson_sim, _ = pearsonr(current_vector, comparison_vector)
    return {
        'cosine': max(0, cosine_sim),
        'euclidean': max(0, euclidean_sim),
        'pearson': max(0, pearson_sim)
    }


# 범주형 공통 속성 및 대표 속성 분석 함수
def analyze_categorical(df, statistics_columns=None, similarity_threshold=0.7):
    if statistics_columns is None:
        statistics_columns = ['유일값 수', '최빈값_범주(mode)', '범주 집합', '값 중복도 평균']
    
    # 필터링: 범주형 데이터만 사용
    df = df[df['컬럼구분'] == '범주형']
    metadata_columns = ['대분류', '파일명', '컬럼명']
    filtered_df = df[metadata_columns + statistics_columns]
    filtered_df['범주 집합'] = filtered_df['범주 집합'].apply(eval)

    categories = filtered_df['대분류'].unique()
    combined_results = []
    common_attributes = []

    for category in categories:
        current_category_df = filtered_df[filtered_df['대분류'] == category]
        other_categories_df = filtered_df[filtered_df['대분류'] != category]

        for _, row in current_category_df.iterrows():
            current_set = row['범주 집합']
            current_value = row['값 중복도 평균']
            current_mode = row['최빈값_범주(mode)']

            # 같은 대분류와의 유사도
            same_category_similarity = [
                jaccard_similarity(current_set, other_row['범주 집합'])
                for _, other_row in current_category_df.iterrows() if row['컬럼명'] != other_row['컬럼명']
            ]

            # 다른 대분류와의 유사도
            different_category_similarity = [
                jaccard_similarity(current_set, other_row['범주 집합'])
                for _, other_row in other_categories_df.iterrows()
            ]

            # 평균 계산
            same_avg = np.mean(same_category_similarity) if same_category_similarity else 0
            different_avg = np.mean(different_category_similarity) if different_category_similarity else 0

            # 결과 저장
            combined_results.append({
                '대분류': category,
                '파일명': row['파일명'],
                '컬럼명': row['컬럼명'],
                '같은 대분류 평균 유사도': same_avg,
                '다른 대분류 평균 유사도': different_avg,
                '유사도 차이': same_avg - different_avg
            })

            # 공통 속성 조건: 다른 대분류 평균 유사도가 일정 임계값 이상
            if different_avg >= similarity_threshold:
                common_attributes.append({
                    '대분류': category,
                    '파일명': row['파일명'],
                    '컬럼명': row['컬럼명'],
                    '다른 대분류 평균 유사도': different_avg
                })

    combined_df = pd.DataFrame(combined_results)
    common_df = pd.DataFrame(common_attributes)
    return combined_df, common_df


# 수치형 공통 속성 및 대표 속성 분석 함수
def analyze_numerical(df, statistics_columns=None, similarity_threshold=0.7):
    if statistics_columns is None:
        statistics_columns = [
            'null 수', '최댓값', '최솟값', '평균(mean)', '중앙값(median)', '최빈값_수치(mode)', '1분위수(1Q)', '3분위수(3Q)', 'IQR',
            '분산(variance)', '표준편차(standard deviation)', '범위(range)', '왜도(skewness)', '첨도(kurtosis)',
            '유일값 수', '값 중복도 평균'
        ]

    # 필터링: 수치형 데이터만 사용
    df = df[df['컬럼구분'] == '수치형']
    metadata_columns = ['대분류', '파일명', '컬럼명']
    filtered_df = df[metadata_columns + statistics_columns].dropna()

    scaler = StandardScaler()
    statistics_scaled = scaler.fit_transform(filtered_df[statistics_columns])

    categories = filtered_df['대분류'].unique()
    combined_results = []
    common_attributes = []
    weights = {'cosine': 0.4, 'euclidean': 0.2, 'pearson': 0.4}

    for category in categories:
        current_category_df = filtered_df[filtered_df['대분류'] == category]
        other_categories_df = filtered_df[filtered_df['대분류'] != category]

        for i, row in current_category_df.iterrows():
            current_vector = statistics_scaled[i]

            # 같은 대분류와의 유사도
            same_similarity = [
                calculate_similarity(current_vector, statistics_scaled[j])
                for j, other_row in current_category_df.iterrows() if i != j
            ]

            # 다른 대분류와의 유사도
            different_similarity = [
                calculate_similarity(current_vector, statistics_scaled[j])
                for j, other_row in other_categories_df.iterrows()
            ]

            # 평균 계산
            same_avg = np.mean([weights['cosine'] * sim['cosine'] +
                                weights['euclidean'] * sim['euclidean'] +
                                weights['pearson'] * sim['pearson']
                                for sim in same_similarity]) if same_similarity else 0

            different_avg = np.mean([weights['cosine'] * sim['cosine'] +
                                     weights['euclidean'] * sim['euclidean'] +
                                     weights['pearson'] * sim['pearson']
                                     for sim in different_similarity]) if different_similarity else 0

            # 결과 저장
            combined_results.append({
                '대분류': category,
                '파일명': row['파일명'],
                '컬럼명': row['컬럼명'],
                '같은 대분류 평균 유사도': same_avg,
                '다른 대분류 평균 유사도': different_avg,
                '유사도 차이': same_avg - different_avg
            })

            # 공통 속성 조건: 다른 대분류 평균 유사도가 일정 임계값 이상
            if different_avg >= similarity_threshold:
                common_attributes.append({
                    '대분류': category,
                    '파일명': row['파일명'],
                    '컬럼명': row['컬럼명'],
                    '다른 대분류 평균 유사도': different_avg
                })

    combined_df = pd.DataFrame(combined_results)
    common_df = pd.DataFrame(common_attributes)
    return combined_df, common_df


# 호출 코드 예시
if __name__ == "__main__":
    file_path = "../../1-1. describe_result/statistics/summary_statistics_with_classification2.csv"
    df = pd.read_csv(file_path)

    # 범주형 분석
    statistics_columns_cat = ['유일값 수', '최빈값_범주(mode)', '범주 집합']
    cat_results, cat_common = analyze_categorical(df, statistics_columns=statistics_columns_cat)
    print("범주형 대표 속성 결과:")
    print(cat_results.head())
    print("범주형 공통 속성 결과:")
    print(cat_common.head())

    # 수치형 분석
    statistics_columns_num = ['최댓값', '최솟값', '평균(mean)', '유일값 수']
    num_results, num_common = analyze_numerical(df, statistics_columns=statistics_columns_num)
    print("수치형 대표 속성 결과:")
    print(num_results.head())
    print("수치형 공통 속성 결과:")
    print(num_common.head())
