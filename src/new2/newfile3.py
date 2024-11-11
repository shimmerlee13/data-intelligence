import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import os
import glob

# 파일 목록 수집
file_pattern = "result/*.csv"  # .csv 확장자 파일만 선택
file_paths = glob.glob(file_pattern)

# 모든 데이터 로드
dataframes = {os.path.basename(path): pd.read_csv(path) for path in file_paths}

# 결과 저장 리스트
most_similar_rows_within = []
least_similar_rows_across = []

# 파일 내 유사도가 높은 행 찾기
for file_name, df in dataframes.items():
    # 수치형 데이터만 사용하여 유사도 계산
    numerical_data = df.select_dtypes(include='number').fillna(0)  # 결측값을 0으로 대체
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(numerical_data)

    # 코사인 유사도 계산
    similarity_matrix = cosine_similarity(scaled_data)

    # 유사도 행렬에서 자기 자신이 아닌 행들 중 유사도가 높은 행 추출
    max_sim_index = None
    max_sim_value = float('-inf')
    for i in range(len(similarity_matrix)):
        for j in range(i + 1, len(similarity_matrix)):
            if similarity_matrix[i, j] > max_sim_value:
                max_sim_value = similarity_matrix[i, j]
                max_sim_index = (i, j)

    # 저장 (origin파일명 컬럼 추가)
    row1 = df.iloc[max_sim_index[0]].copy()
    row2 = df.iloc[max_sim_index[1]].copy()
    row1['origin파일명'] = file_name
    row2['origin파일명'] = file_name
    row1['유사도'] = max_sim_value
    row2['유사도'] = max_sim_value
    most_similar_rows_within.append(row1)
    most_similar_rows_within.append(row2)

# 파일 간 유사도가 가장 낮은 행 찾기
file_names = list(dataframes.keys())
for i in range(len(file_names)):
    for j in range(i + 1, len(file_names)):
        # 두 파일 간 공통 열만 선택
        df1 = dataframes[file_names[i]]
        df2 = dataframes[file_names[j]]
        common_columns = df1.columns.intersection(df2.columns)

        # 공통 열만 사용하고 결측값을 0으로 대체
        df1_common = df1[common_columns].select_dtypes(include='number').fillna(0)
        df2_common = df2[common_columns].select_dtypes(include='number').fillna(0)

        # 각각의 데이터에 대해 별도로 스케일러 적용
        scaler1 = StandardScaler()
        scaler2 = StandardScaler()
        data1 = scaler1.fit_transform(df1_common)
        data2 = scaler2.fit_transform(df2_common)

        # 코사인 유사도 계산
        similarity_matrix = cosine_similarity(data1, data2)

        # 유사도가 가장 낮은 인덱스 찾기
        min_sim_index = None
        min_sim_value = float('inf')
        for row in range(similarity_matrix.shape[0]):
            for col in range(similarity_matrix.shape[1]):
                if similarity_matrix[row, col] < min_sim_value:
                    min_sim_value = similarity_matrix[row, col]
                    min_sim_index = (row, col)

        # 저장 (origin파일명 컬럼 추가)
        row_from_file1 = df1.iloc[min_sim_index[0]].copy()
        row_from_file2 = df2.iloc[min_sim_index[1]].copy()
        row_from_file1['origin파일명'] = file_names[i]
        row_from_file2['origin파일명'] = file_names[j]
        row_from_file1['유사도'] = min_sim_value
        row_from_file2['유사도'] = min_sim_value
        least_similar_rows_across.append(row_from_file1)
        least_similar_rows_across.append(row_from_file2)

# 결과를 데이터프레임으로 변환
most_similar_df = pd.DataFrame(most_similar_rows_within)
least_similar_df = pd.DataFrame(least_similar_rows_across)

# CSV 파일로 저장
most_similar_df.to_csv('most_similar_rows_within.csv', index=False, encoding='utf-8-sig')
least_similar_df.to_csv('least_similar_rows_across.csv', index=False, encoding='utf-8-sig')
