import pandas as pd
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import cosine
import numpy as np

# 1. 데이터 로드
file_path = "../1-1. describe_result/statistics/summary_statistics_with_classification.csv"  # 데이터 파일 경로
df = pd.read_csv(file_path)

# 2. 필요한 통계 수치 컬럼 필터링
statistics_columns = [
    '유일값 수', '값 중복도 평균', '최댓값', '최솟값', '평균(mean)', '중앙값(median)',
    '1분위수(1Q)',	'3분위수(3Q)',	'IQR',
    '분산(variance)', '표준편차(standard deviation)',
    '범위(range)', '왜도(skewness)', '첨도(kurtosis)'
]
metadata_columns = ['대분류', '파일명', '컬럼명']  # 추가적인 메타정보 컬럼
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
    similar_columns = []  # 현재 컬럼과 유사한 컬럼명을 저장할 리스트
    for j in range(len(statistics_scaled)):
        if i != j:  # 자기 자신과는 비교하지 않음
            other_vector = statistics_scaled[j]
            similarity = 1 - cosine(current_vector, other_vector)
            if similarity > 0.9:  # 유사도의 임계값 설정 (예: 0.9)
                count += 1
                similar_columns.append(filtered_df.iloc[j]['컬럼명'])  # 유사한 컬럼명 추가
    similarity_counts.append(count)
    similar_column_names.append(similar_columns)  # 유사한 컬럼명을 저장

# 5. 결과를 새로운 컬럼으로 추가
filtered_df['유사도 수'] = similarity_counts
filtered_df['유사한 컬럼명'] = similar_column_names


# 6. 유사도 수가 많은 순으로 정렬
filtered_df_sorted = filtered_df.sort_values(by='유사도 수', ascending=False)

# 7. 결과를 사용자에게 표시
#import ace_tools as tools; tools.display_dataframe_to_user(name="Similarity Count Analysis with Normalization", dataframe=filtered_df_sorted)


###########################

from sklearn.metrics.pairwise import euclidean_distances
from scipy.stats import pearsonr
import pandas as pd
import numpy as np

# 1. 유클리디안 거리 기반 유사도 계산
euclidean_matrix = euclidean_distances(statistics_scaled)
euclidean_similarity_counts = []

for i in range(len(euclidean_matrix)):
    count = 0
    for j in range(len(euclidean_matrix)):
        if i != j and euclidean_matrix[i, j] < 1.0:  # 유클리디안 거리 임계값 (예: 1.0)
            count += 1
    euclidean_similarity_counts.append(count)

# 2. 피어슨 상관계수 기반 유사도 계산
pearson_similarity_counts = []
for i in range(len(statistics_scaled)):
    current_vector = statistics_scaled[i]
    count = 0
    for j in range(len(statistics_scaled)):
        if i != j:
            corr, _ = pearsonr(current_vector, statistics_scaled[j])
            if corr > 0.8:  # 피어슨 상관계수 임계값 (예: 0.8)
                count += 1
    pearson_similarity_counts.append(count)

# 3. 기존 코사인 유사도 계산
cosine_similarity_counts = []
from scipy.spatial.distance import cosine

for i in range(len(statistics_scaled)):
    current_vector = statistics_scaled[i]
    count = 0
    for j in range(len(statistics_scaled)):
        if i != j:
            similarity = 1 - cosine(current_vector, statistics_scaled[j])
            if similarity > 0.9:  # 코사인 유사도 임계값 (예: 0.9)
                count += 1
    cosine_similarity_counts.append(count)

# 4. 결과를 데이터프레임에 추가
filtered_df['유클리디안 유사도 수'] = euclidean_similarity_counts
filtered_df['피어슨 유사도 수'] = pearson_similarity_counts
filtered_df['코사인 유사도 수'] = cosine_similarity_counts

output_path_df = "filtered_df.csv"  # 저장할 파일 경로
filtered_df.to_csv(output_path_df, index=False, encoding='utf-8-sig')
print(f"유사도 결과 데이터프레임이 '{output_path_df}'에 저장되었습니다.")

# 5. 정렬 및 결과 표시
filtered_df_sorted = filtered_df.sort_values(by='코사인 유사도 수', ascending=False)

import ace_tools as tools; tools.display_dataframe_to_user(name="Cross-Validation with Multiple Similarity Measures", dataframe=filtered_df_sorted)
