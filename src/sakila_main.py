# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 19:17:00 2024

@author: shimm
"""



file_path = "../1-1. describe_result/statistics/summary_statistics_with_classification2.csv"
df = pd.read_csv(file_path)

# 범주형 분석
statistics_columns_cat = ['유일값 수', '최빈값_범주(mode)', '범주 집합', '값 중복도 평균']
cat_representative, cat_common = analyze_categorical(df, statistics_columns=statistics_columns_cat)
print("범주형 대표 속성 결과:")
print(cat_results.head())
print("범주형 공통 속성 결과:")
print(cat_common.head())

# 수치형 분석
statistics_columns_num = [
    'null 수', '최댓값', '최솟값', '평균(mean)', '중앙값(median)', '최빈값_수치(mode)', '1분위수(1Q)', '3분위수(3Q)', 'IQR',
    '분산(variance)', '표준편차(standard deviation)', '범위(range)', '왜도(skewness)', '첨도(kurtosis)',
    '유일값 수', '값 중복도 평균'
]
num_representative, num_common = analyze_numerical(df, statistics_columns=statistics_columns_num)
print("수치형 대표 속성 결과:")
print(num_results.head())
print("수치형 공통 속성 결과:")
print(num_common.head())



import pymysql
import pandas as pd

from similarity.attribute_analysis import analyze_categorical, analyze_numerical
from sakila.sakila_finding_pk import main



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



