import pymysql
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances
from scipy.stats import pearsonr
from scipy.spatial.distance import cosine

# Jaccard 유사도 계산 (범주형용)
def jaccard_similarity(set1, set2):
    return len(set1 & set2) / len(set1 | set2) if set1 and set2 else 0

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

# 범주형 공통 및 대표 속성 도출
def analyze_categorical(df, threshold=0.7):
    results = []
    for col1 in df.columns:
        for col2 in df.columns:
            if col1 != col2:
                sim = jaccard_similarity(set(df[col1].dropna()), set(df[col2].dropna()))
                if sim > threshold:
                    results.append({'column1': col1, 'column2': col2, 'similarity': sim})
    return results

# 수치형 공통 및 대표 속성 도출
def analyze_numerical(df, threshold=0.7):
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df.dropna())
    results = []

    for i, col1 in enumerate(df.columns):
        for j, col2 in enumerate(df.columns):
            if i < j:  # 중복 비교 방지
                similarity = calculate_similarity(scaled_data[:, i], scaled_data[:, j])

                # 대표 유사도 점수 계산 (평균)
                representative_similarity = np.mean(list(similarity.values()))

                if representative_similarity > threshold:
                    results.append({
                        'column1': col1,
                        'column2': col2,
                        'similarity': representative_similarity
                    })

    return results

# PK 후보군의 유일값 비율 및 NULL 비율 계산
def analyze_column(connection, table, column):
    query = f"""
        SELECT COUNT(*) AS total_rows,
               COUNT(DISTINCT `{column}`) AS unique_values,
               COUNT(`{column}`) AS non_null_values
        FROM `{table}`;
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()

        total_rows = result['total_rows']
        unique_values = result['unique_values']
        non_null_values = result['non_null_values']

        return {
            'table': table,
            'column': column,
            'unique_ratio': unique_values / total_rows if total_rows else 0,
            'null_ratio': 1 - (non_null_values / total_rows) if total_rows else 1
        }
    except Exception as e:
        print(f"Error analyzing column {column} in table {table}: {e}")
        return None

# 메인 로직
def main():
    connection = pymysql.connect(
        host='ii578293.iptime.org',
        port=13307,
        user='u0001',
        password='1234',
        database='sakila',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tables = [list(row.values())[0] for row in cursor.fetchall()]

        pk_candidates = []

        for table in tables:
            print(f"\n분석 중: {table}")
            query = f"SELECT * FROM `{table}`;"
            try:
                df = pd.read_sql(query, connection)

                # 컬럼 타입 구분
                numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

                print(f"수치형 컬럼: {numerical_cols}")
                print(f"범주형 컬럼: {categorical_cols}")

                # 범주형 공통 및 대표 속성 분석
                cat_results = analyze_categorical(df[categorical_cols]) if categorical_cols else []
                num_results = analyze_numerical(df[numerical_cols]) if numerical_cols else []

                # PK 후보군 합치기
                candidate_columns = list(set(c for r in cat_results + num_results for c in [r['column1'], r['column2']]))

                # PK 후보군 분석
                for column in candidate_columns:
                    result = analyze_column(connection, table, column)
                    if result:  # 유효한 결과만 추가
                        pk_candidates.append(result)
            except Exception as e:
                print(f"Error analyzing table {table}: {e}")

        # 결과 정렬 및 출력
        pk_df = pd.DataFrame(pk_candidates)
        pk_df = pk_df.sort_values(by=['unique_ratio', 'null_ratio'], ascending=[False, True])
        print("\nPK 후보 컬럼:")
        print(pk_df)

        # 결과 저장
        pk_df.to_csv("./sakila/pk_results.csv", encoding='utf-8', index=False)
        print("\n결과가 './sakila/pk_results.csv'에 저장되었습니다.")

if __name__ == "__main__":
    main()
