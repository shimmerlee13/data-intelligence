import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances
from scipy.stats import pearsonr
from scipy.spatial.distance import cosine

# 1. 데이터 로드
file_path = "../../1-1. describe_result/statistics/summary_statistics_with_classification2.csv"  # 데이터 파일 경로
df = pd.read_csv(file_path)
df = df[df['컬럼구분'] == '수치형']

# 2. 필요한 통계 수치 컬럼 필터링
statistics_columns = [
    'null 수', '최댓값', '최솟값', '평균(mean)', '중앙값(median)', '최빈값_수치(mode)', '1분위수(1Q)', '3분위수(3Q)', 'IQR',
    '분산(variance)', '표준편차(standard deviation)', '범위(range)', '왜도(skewness)', '첨도(kurtosis)',
    '유일값 수', '값 중복도 평균'
]

metadata_columns = ['대분류', '파일명', '컬럼명']  # 추가적인 메타정보 컬럼
filtered_df = df[metadata_columns + statistics_columns].dropna()  # 필요한 컬럼만 선택

# 3. 통계 수치 정규화
scaler = StandardScaler()
statistics_scaled = scaler.fit_transform(filtered_df[statistics_columns])

# 4. 유사도 계산 함수
def calculate_similarity(current_vector, comparison_vector):
    cosine_sim = 1 - cosine(current_vector, comparison_vector)
    euclidean_sim = 1 / (1 + euclidean_distances([current_vector], [comparison_vector])[0][0])
    pearson_sim, _ = pearsonr(current_vector, comparison_vector)
    return {
        'cosine': max(0, cosine_sim),  # 음수는 0으로 변환
        'euclidean': max(0, euclidean_sim),
        'pearson': max(0, pearson_sim)
    }

# 5. 모든 속성의 계산 결과 저장
all_attributes = []
weights = {'cosine': 0.4, 'euclidean': 0.2, 'pearson': 0.4}
categories = filtered_df['대분류'].unique()

filtered_df = filtered_df.reset_index(drop=True)  # 인덱스 초기화

for category in categories:
    current_category_df = filtered_df[filtered_df['대분류'] == category]
    other_categories_df = filtered_df[filtered_df['대분류'] != category]

    for i, row in current_category_df.iterrows():
        current_vector = statistics_scaled[i]

        # 같은 대분류와의 유사도 계산
        same_category_similarity = []
        for _, other_row in current_category_df.iterrows():
            j = other_row.name
            if i != j:  # 자기 자신은 제외
                comparison_vector = statistics_scaled[j]
                similarity = calculate_similarity(current_vector, comparison_vector)
                combined_score = (
                    weights['cosine'] * similarity['cosine'] +
                    weights['euclidean'] * similarity['euclidean'] +
                    weights['pearson'] * similarity['pearson']
                )
                same_category_similarity.append(combined_score)

        # 다른 대분류와의 유사도 계산
        different_category_similarity = []
        for _, other_row in other_categories_df.iterrows():
            j = other_row.name
            comparison_vector = statistics_scaled[j]
            similarity = calculate_similarity(current_vector, comparison_vector)
            combined_score = (
                weights['cosine'] * similarity['cosine'] +
                weights['euclidean'] * similarity['euclidean'] +
                weights['pearson'] * similarity['pearson']
            )
            different_category_similarity.append(combined_score)

        # 평균 유사도 계산
        same_category_avg = np.mean(same_category_similarity) if same_category_similarity else 0
        different_category_avg = np.mean(different_category_similarity) if different_category_similarity else 0
        similarity_difference = same_category_avg - different_category_avg

        # 모든 결과 저장
        all_attributes.append({
            '대분류': category,
            '파일명': row['파일명'],
            '컬럼명': row['컬럼명'],
            '같은 대분류 평균 유사도': same_category_avg,
            '다른 대분류 평균 유사도': different_category_avg,
            '유사도 차이': similarity_difference
        })

# 6. 모든 속성 결과를 DataFrame으로 변환
all_attributes_df = pd.DataFrame(all_attributes)

# 7. 대분류별 정렬
all_attributes_df_sorted = all_attributes_df.sort_values(
    by=['대분류', '유사도 차이'], ascending=[True, False]
)

# 파일 저장
output_path_all = "../../1-1. describe_result/similarity/similarity_calculate/similarity_num_representative.csv"
all_attributes_df_sorted.to_csv(output_path_all, index=False, encoding='utf-8-sig')

print(f"모든 속성 결과 데이터프레임이 '{output_path_all}'에 저장되었습니다.")
