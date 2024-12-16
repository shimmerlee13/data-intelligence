import pymysql
import pandas as pd

def get_tables_and_columns(connection):
    """데이터베이스의 테이블과 컬럼 정보를 가져오는 함수"""
    tables = {}
    query_tables = "SHOW TABLES;"

    with connection.cursor() as cursor:
        cursor.execute(query_tables)
        for row in cursor.fetchall():
            table_name = list(row.values())[0]
            query_columns = f"DESCRIBE {table_name};"
            cursor.execute(query_columns)
            columns = [col['Field'] for col in cursor.fetchall()]
            tables[table_name] = columns

    return tables

def find_fk_candidates(connection, pk_df):
    """
    FK 후보군 탐색 함수

    Parameters:
        connection: DB 연결 객체
        pk_df (DataFrame): Primary Key 정보가 담긴 DataFrame

    Returns:
        DataFrame: FK 후보군 정보
    """
    fk_candidates = []
    all_tables = get_tables_and_columns(connection)

    for table, columns in all_tables.items():
        for column in columns:
            for _, pk_row in pk_df.iterrows():
                pk_table, pk_column = pk_row['table'], pk_row['column']

                # 동일 테이블 및 컬럼은 건너뜀
                if table == pk_table and column == pk_column:
                    continue

                # FK 후보 조건 확인 쿼리
                query = f"""
                    SELECT 
                        (SELECT COUNT(DISTINCT `{column}`) FROM `{table}`) AS fk_unique_count,
                        (SELECT COUNT(DISTINCT `{column}`) 
                         FROM `{table}` 
                         WHERE `{column}` IN (SELECT `{pk_column}` FROM `{pk_table}`)) AS matching_unique_count,
                        (SELECT COUNT(DISTINCT `{column}`) 
                         FROM `{table}` 
                         WHERE `{column}` NOT IN (SELECT `{pk_column}` FROM `{pk_table}`)) AS non_matching_unique_count,
                        (SELECT COUNT(DISTINCT `{pk_column}`) FROM `{pk_table}`) AS pk_unique_count
                    FROM DUAL;
                """

                with connection.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchone()

                fk_unique_count = result['fk_unique_count']
                matching_unique_count = result['matching_unique_count']
                non_matching_unique_count = result['non_matching_unique_count']
                pk_unique_count = result['pk_unique_count']

                # 매칭 비율 계산
                if fk_unique_count > 0 and pk_unique_count > 0:
                    match_ratio = (matching_unique_count / fk_unique_count) * 100
                    total_match_ratio = (matching_unique_count / pk_unique_count) * 100

                    fk_candidates.append({
                        'fk_table': table,
                        'fk_column': column,
                        'pk_table': pk_table,
                        'pk_column': pk_column,
                        'fk_unique_count': fk_unique_count,
                        'pk_unique_count': pk_unique_count,
                        'matching_unique_count': matching_unique_count,
                        'non_matching_unique_count': non_matching_unique_count,
                        'fk_match_percentage': match_ratio,
                        'pk_match_percentage': total_match_ratio
                    })


    return pd.DataFrame(fk_candidates)



# DB 연결 설정
connection = pymysql.connect(
    host='ii578293.iptime.org',
    port=13307,
    user='u0001',
    password='1234',
    database='sakila',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# Primary Key 데이터 로드
pk_df = pd.read_csv('./sakila/pk_results.csv')

# FK 후보군 탐색
fk_df = find_fk_candidates(connection, pk_df)

# FK 후보군 정렬
fk_df = fk_df.sort_values(
    by=['non_matching_unique_count', 'fk_match_percentage'],
    ascending=[True, False]  # non_matching_unique_count 오름차순, fk_match_percentage 내림차순
)

# 결과 출력
print("\n정렬된 FK 후보군:")
print(fk_df)

# 결과 저장 및 출력
fk_df.to_csv('./sakila/fk_results.csv', index=False)
print(fk_df)

# DB 연결 종료
connection.close()
