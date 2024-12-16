import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# 파일 로드
df = pd.read_csv("../../1-1. describe_result/statistics/summary_statistics_with_classification2.csv")

# 수치형, 범주형 컬럼 분리
numerical_cols = ['null 수', '최댓값', '최솟값', '평균(mean)', '중앙값(median)', '최빈값_수치(mode)', '1분위수(1Q)', '3분위수(3Q)', 'IQR',
                  '분산(variance)', '표준편차(standard deviation)', '범위(range)', '왜도(skewness)', '첨도(kurtosis)',
                  '유일값 수', '값 중복도 평균']
categorical_cols = ['대분류', '소분류', '파일명', '컬럼구분', '범주값 변화(고정/가변)', '최빈값_범주(mode)', '범주 집합']



# 수치형 데이터에 대해 유사도 측정
def compute_numerical_similarity(df, numerical_cols):
    scaler = MinMaxScaler()
    normalized_data = scaler.fit_transform(df[numerical_cols].fillna(0))
    cosine_sim = cosine_similarity(normalized_data)
    return cosine_sim

# 범주형 데이터에 대해 유사도 측정 (자카드 유사도 기반)
def compute_categorical_similarity(df, categorical_cols):
    categorical_sim = np.zeros((len(df), len(df)))
    for i in range(len(df)):
        for j in range(len(df)):
            if i != j:
                intersect = sum(df.iloc[i][col] == df.iloc[j][col] for col in categorical_cols)
                union = len(categorical_cols)
                categorical_sim[i, j] = intersect / union
            else:
                categorical_sim[i, j] = 1
    return categorical_sim

# 각 유사도 계산
numerical_similarity = compute_numerical_similarity(df, numerical_cols)
categorical_similarity = compute_categorical_similarity(df, categorical_cols)

# 전체 유사도 (가중 평균)
alpha = 0.7  # 수치형 가중치
beta = 0.3   # 범주형 가중치
overall_similarity = alpha * numerical_similarity + beta * categorical_similarity

# 결과 CSV 파일로 저장
pd.DataFrame(numerical_similarity).to_csv("../../1-1. describe_result/similarity/similarity_calculate/numerical_similarity.csv", index=False, header=False)
pd.DataFrame(categorical_similarity).to_csv("../../1-1. describe_result/similarity/similarity_calculate/categorical_similarity.csv", index=False, header=False)
pd.DataFrame(overall_similarity).to_csv("../../1-1. describe_result/similarity/similarity_calculate/overall_similarity.csv", index=False, header=False)

print("Similarity matrices saved as CSV files.")
