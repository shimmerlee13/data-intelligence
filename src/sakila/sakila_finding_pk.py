
import pandas as pd
import mysql.connector
from itertools import combinations
def find_primary_key(table_name, connection):
    # 테이블 데이터를 읽어오기
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql(query, connection)

    # 모든 컬럼명 가져오기
    columns = df.columns

    # NULL 값이 없는 컬럼 필터링
    non_null_columns = [col for col in columns if not df[col].isnull().any()]

    # 유일성 확인: 각 컬럼의 고유값 수와 데이터프레임 전체 행 수 비교
    candidate_keys = [col for col in non_null_columns if df[col].nunique() == len(df)]

    # 단일 컬럼으로 PK 후보가 없으면, 조합으로 확인
    if not candidate_keys:
        for i in range(2, len(non_null_columns) + 1):  # 2개 이상 컬럼 조합
            for combo in combinations(non_null_columns, i):
                if df[list(combo)].drop_duplicates().shape[0] == len(df):
                    candidate_keys.append(combo)
                    break  # 첫 번째 조합을 찾으면 종료
            if candidate_keys:
                break

    return candidate_keys

def find_potential_primary_keys(table_name, connection):
    # 데이터 로드
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql(query, connection)

    total_rows = len(df)
    results = []

    # 1. 단일 컬럼 분석
    for col in df.columns:
        null_count = df[col].isnull().sum()
        unique_count = df[col].nunique()
        unique_ratio = unique_count / total_rows  # 고유성 비율 계산

        results.append({
            "column": col,
            "is_null_free": null_count == 0,  # NULL이 없는지
            "unique_count": unique_count,
            "unique_ratio": unique_ratio,
            "pk_candidate": null_count == 0 and unique_count == total_rows
        })

    # 2. 복합 컬럼 조합 분석 (최대 3개 조합만 확인)
    non_null_columns = [col for col in df.columns if not df[col].isnull().any()]
    for r in range(2, 4):  # 2~3개 컬럼 조합
        for combo in combinations(non_null_columns, r):
            combo_df = df[list(combo)]
            unique_count = combo_df.drop_duplicates().shape[0]
            unique_ratio = unique_count / total_rows

            results.append({
                "column": combo,
                "is_null_free": True,  # 조합의 컬럼은 이미 NULL이 없음
                "unique_count": unique_count,
                "unique_ratio": unique_ratio,
                "pk_candidate": unique_count == total_rows
            })

    # 결과 정리
    results_df = pd.DataFrame(results)
    pk_candidates = results_df[results_df["pk_candidate"]]

    if not pk_candidates.empty:
        print("완벽한 PK 후보:")
        print(pk_candidates)
    else:
        print("완벽한 PK는 없지만, 고유성이 높은 컬럼/조합:")
        print(results_df.sort_values(by="unique_ratio", ascending=False).head())

    return results_df


# MySQL 데이터베이스 연결 설정
connection = mysql.connector.connect(
    host='ii578293.iptime.org',
    port=13307,
    user='u0001',
    password='1234',
    database='sakila',
)

# 함수 실행
table_name = 'address'  # 확인할 테이블 이름
primary_keys = find_primary_key(table_name, connection)

if primary_keys:
    print("Primary Key 후보:", primary_keys)
else:
    print("Primary Key를 찾을 수 없습니다.")

# 함수 실행
table_name = 'your_table_name'  # 테이블 이름
pk_analysis = find_potential_primary_keys(table_name, connection)