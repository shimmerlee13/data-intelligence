import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# 데이터 로드
df = pd.read_csv("../../1-1. describe_result/statistics/summary_statistics_with_classification2.csv")

# 수치형, 범주형 컬럼 지정
numerical_cols = ['null 수', '최댓값', '최솟값', '평균(mean)', '중앙값(median)', '최빈값_수치(mode)', '1분위수(1Q)', '3분위수(3Q)', 'IQR',
                  '분산(variance)', '표준편차(standard deviation)', '범위(range)', '왜도(skewness)', '첨도(kurtosis)',
                  '유일값 수', '값 중복도 평균']
categorical_cols = ['대분류', '소분류', '파일명', '컬럼구분', '범주값 변화(고정/가변)', '최빈값_범주(mode)', '범주 집합']


# 수치형 유사도 계산
def compute_numerical_similarity(df, numerical_cols):
    scaler = MinMaxScaler()
    normalized_data = scaler.fit_transform(df[numerical_cols].fillna(0))
    return cosine_similarity(normalized_data)

numerical_similarity = compute_numerical_similarity(df, numerical_cols)

# 범주형 유사도 계산 (자카드 유사도 기반)
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

categorical_similarity = compute_categorical_similarity(df, categorical_cols)

# 가중 평균을 통해 전체 유사도 계산
alpha, beta = 0.7, 0.3  # 수치형, 범주형 가중치
overall_similarity = alpha * numerical_similarity + beta * categorical_similarity

# 유사도 기준으로 그룹화
similarity_threshold = 0.9
groups = []
visited = set()

for i in range(overall_similarity.shape[0]):
    if i not in visited:
        group = set([i])
        for j in range(i + 1, overall_similarity.shape[1]):
            if overall_similarity[i, j] >= similarity_threshold:
                group.add(j)
                visited.add(j)
        groups.append(group)
        visited.update(group)

# 각 그룹의 대표 특성 추출
group_representatives = []
for group in groups:
    group_list = list(group)
    submatrix = overall_similarity[group_list, :][:, group_list]
    representative = group_list[np.argmax(submatrix.sum(axis=1))]
    group_representatives.append((group, representative))

# 결과 생성
output_data = []

for idx, (group, representative) in enumerate(group_representatives):
    group_members = sorted(group)
    for member in group_members:
        output_data.append({
            "파일명": df.loc[member, "파일명"],
            "컬럼명": df.loc[member, "컬럼명"],
            "공통 특성 그룹": idx + 1,
            "대표 특성": "대표" if member == representative else ""
        })

# 결과 DataFrame으로 저장, UTF-8 인코딩 설정
output_df = pd.DataFrame(output_data)
output_df.to_csv('../data_parsing/similarity/similarity_feature_groups/similarity_feature_groups.csv', index=False, encoding='utf-8-sig')
print("공통 및 대표 특성 요약 파일이 저장되었습니다.")