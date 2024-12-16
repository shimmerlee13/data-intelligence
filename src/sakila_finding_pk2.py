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
                representative_similarity = np.mean(list(similarity.values()))  # 평균 유사도
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
        FROM `{table}`;"""
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
            'null_ratio': 1 - (non_null_values / total_rows) if total_rows else 1,
            'is_high_unique': unique_values / total_rows >= 0.99  # 0.99 이상인 경우 True

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

        final_results = []

        for table in tables:
            print(f"\n분석 중: {table}")
            query = f"SELECT * FROM `{table}`;"
            try:
                df = pd.read_sql(query, connection)

                # 컬럼 타입 구분
                numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

                # 범주형 및 수치형 분석
                cat_results = analyze_categorical(df[categorical_cols]) if categorical_cols else []
                num_results = analyze_numerical(df[numerical_cols]) if numerical_cols else []

                # PK 후보군 합치기
                candidate_columns = list(set(c for r in cat_results + num_results for c in [r['column1'], r['column2']]))
                candidate_columns = candidate_columns or df.columns.tolist()  # 모든 컬럼 검사

                # PK 후보군 분석
                table_results = []
                for column in candidate_columns:
                    result = analyze_column(connection, table, column)
                    if result:
                        table_results.append(result)

                # 테이블별 정렬: unique_ratio 내림차순, null_ratio 오름차순
                table_results = sorted(table_results, key=lambda x: (-x['unique_ratio'], x['null_ratio']))
                final_results.extend(table_results)

            except Exception as e:
                print(f"Error analyzing table {table}: {e}")

        # 결과 정리 및 출력
        pk_df = pd.DataFrame(final_results)
        print("\n테이블별 PK 후보 컬럼 (unique_ratio 기준 정렬):")
        print(pk_df)

        # 결과 저장
        pk_df.to_csv("./sakila/pk_results.csv", encoding='utf-8', index=False)
        print("\n결과가 './sakila/pk_results.csv'에 저장되었습니다.")
        

if __name__ == "__main__":
    main()
