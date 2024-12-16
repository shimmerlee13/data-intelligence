
import pymysql
import pandas as pd


connection = pymysql.connect(
    host='ii578293.iptime.org',
    port=13307,
    user='u0001',
    password='1234',
    database='sakila',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)


def get_tables(connection):
    """데이터베이스 내 모든 테이블 이름 가져오기"""
    query = "SHOW TABLES;"
    with connection.cursor() as cursor:
        cursor.execute(query)
        tables = cursor.fetchall()
    return [list(table.values())[0] for table in tables]


def get_columns(connection, table):
    """특정 테이블의 컬럼 이름 가져오기"""
    query = f"DESCRIBE {table};"
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = cursor.fetchall()
    return [column['Field'] for column in columns]


def analyze_column(connection, table, column):
    """컬럼의 고유 값, NULL 여부를 확인하여 PK 후보 검출"""
    query = f"""
        SELECT COUNT(*) AS total_rows, 
               COUNT(DISTINCT `{column}`) AS unique_values, 
               COUNT(`{column}`) AS non_null_values
        FROM `{table}`;
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()
    return {
        'table': table,
        'column': column,
        'total_rows': result['total_rows'],
        'unique_values': result['unique_values'],
        'non_null_values': result['non_null_values'],
        'is_pk_candidate': result['total_rows'] == result['unique_values'] == result['non_null_values']
    }


def main():
    tables = get_tables(connection)
    results = []

    for table in tables:
        columns = get_columns(connection, table)
        for column in columns:
            result = analyze_column(connection, table, column)
            results.append(result)

    df = pd.DataFrame(results)
    print("Primary Key 후보 컬럼:")
    print(df[df['is_pk_candidate']][['table', 'column']])

    df[df['is_pk_candidate']][['table', 'column']].to_csv('primary_key_candidates.csv', index=False)


if __name__ == "__main__":
    main()
