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

# 4. 유사도 계산

# 4-1. 코사인 유사도
cosine_similarity_counts = []
cosine_similarity_scores = []

for i in range(len(statistics_scaled)):
    current_vector = statistics_scaled[i]
    count = 0
    total_similarity = 0
    for j in range(len(statistics_scaled)):
        if i != j:
            other_vector = statistics_scaled[j]
            similarity = 1 - cosine(current_vector, other_vector)
            if similarity > 0.9:  # 코사인 유사도의 임계값 설정
                count += 1
                total_similarity += similarity
    cosine_similarity_counts.append(count)
    cosine_similarity_scores.append(total_similarity / count if count > 0 else 0)

# 4-2. 유클리디안 거리 기반 유사도
euclidean_similarity_counts = []
euclidean_similarity_scores = []

euclidean_matrix = euclidean_distances(statistics_scaled)

for i in range(len(euclidean_matrix)):
    count = 0
    total_similarity = 0
    for j in range(len(euclidean_matrix)):
        if i != j and euclidean_matrix[i, j] < 1.0:  # 유클리디안 거리 임계값
            count += 1
            total_similarity += 1 / (1 + euclidean_matrix[i, j])  # 거리 -> 유사도 변환
    euclidean_similarity_counts.append(count)
    euclidean_similarity_scores.append(total_similarity / count if count > 0 else 0)

# 4-3. 피어슨 상관계수 기반 유사도
pearson_similarity_counts = []
pearson_similarity_scores = []

for i in range(len(statistics_scaled)):
    current_vector = statistics_scaled[i]
    count = 0
    total_similarity = 0
    for j in range(len(statistics_scaled)):
        if i != j:
            corr, _ = pearsonr(current_vector, statistics_scaled[j])
            if corr > 0.8:  # 피어슨 상관계수 임계값
                count += 1
                total_similarity += corr
    pearson_similarity_counts.append(count)
    pearson_similarity_scores.append(total_similarity / count if count > 0 else 0)

# 5. 가중치 기반 종합 점수 계산
weights = {'cosine': 0.4, 'euclidean': 0.2, 'pearson': 0.4}

combined_similarity_scores = []
for i in range(len(statistics_scaled)):
    combined_score = (
        weights['cosine'] * cosine_similarity_scores[i] +
        weights['euclidean'] * euclidean_similarity_scores[i] +
        weights['pearson'] * pearson_similarity_scores[i]
    )
    combined_similarity_scores.append(combined_score)

# 6. 결과를 DataFrame에 추가
filtered_df['코사인 유사도 수'] = cosine_similarity_counts
filtered_df['코사인 평균 유사도'] = cosine_similarity_scores
filtered_df['유클리디안 유사도 수'] = euclidean_similarity_counts
filtered_df['유클리디안 평균 유사도'] = euclidean_similarity_scores
filtered_df['피어슨 유사도 수'] = pearson_similarity_counts
filtered_df['피어슨 평균 유사도'] = pearson_similarity_scores
filtered_df['종합 평균 유사도'] = combined_similarity_scores

# 필터링
filtered_df = filtered_df[filtered_df['유일값 수'] >= 5]
filtered_df = filtered_df[filtered_df['왜도(skewness)'] != 0]
filtered_df = filtered_df[filtered_df['값 중복도 평균'] != 1]

# 정렬
filtered_df_sorted = filtered_df.sort_values(by='종합 평균 유사도', ascending=False)

# 파일 저장
output_path_df = "../../1-1. describe_result/similarity/similarity_calculate/similarity_num_common.csv"
filtered_df_sorted.to_csv(output_path_df, index=False, encoding='utf-8-sig')

print(f"유사도 결과 데이터프레임이 '{output_path_df}'에 저장되었습니다.")
