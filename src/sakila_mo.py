import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy import create_engine

# MySQL 데이터베이스 연결 설정
engine = create_engine("mysql+pymysql://u0001:1234@ii578293.iptime.org:13307/sakila")

def fetch_column_info(engine, schema_name):
    """스키마의 모든 테이블 컬럼 정보를 조회"""
    query = f"""
    SELECT 
        TABLE_NAME AS 테이블명,
        COLUMN_NAME AS 컬럼명,
        DATA_TYPE AS 데이터_타입
    FROM 
        INFORMATION_SCHEMA.COLUMNS
    WHERE 
        TABLE_SCHEMA = '{schema_name}';
    """
    return pd.read_sql(query, engine)

def fetch_table_data(engine, table_name):
    """특정 테이블 데이터를 가져오는 함수"""
    query = f"SELECT * FROM {table_name} LIMIT 1000"
    return pd.read_sql(query, engine)

def detect_outliers_numeric(data):
    """수치형 데이터 이상치 탐지"""
    if data.empty:
        return {"normal_range": None, "outliers": []}

    model = IsolationForest(contamination=0.1, random_state=42)
    data = data.dropna()
    predictions = model.fit_predict(data.values.reshape(-1, 1))
    normal_data = data[predictions == 1]
    outlier_data = data[predictions == -1]

    return {
        "normal_range": (normal_data.min(), normal_data.max()),
        "outliers": outlier_data.tolist()[:4],
    }

def detect_outliers_text(data):
    """텍스트 데이터 이상치 탐지"""
    if data.empty:
        return {"frequent_values": None, "outliers": []}

    value_counts = data.value_counts()
    total = len(data)
    frequent_values = value_counts[value_counts > 0.01 * total].index.tolist()[:4]
    outlier_values = value_counts[value_counts <= 0.01 * total].index.tolist()[:4]

    return {
        "frequent_values": frequent_values,
        "outliers": outlier_values,
    }

def detect_outliers_date(data):
    """날짜 데이터 이상치 탐지"""
    if data.empty:
        return {"date_range": None, "outliers": []}

    data = pd.to_datetime(data, errors='coerce').dropna()
    if data.empty:
        return {"date_range": None, "outliers": []}

    min_date = data.min()
    max_date = data.max()

    return {
        "date_range": (min_date, max_date),
        "outliers": [],
    }

def analyze_table_data(table_name, table_data, column_info):
    """테이블 데이터를 분석하고 이상치 탐지"""
    results = []
    columns = column_info[column_info['테이블명'] == table_name]

    for _, row in columns.iterrows():
        column_name = row['컬럼명']
        data_type = row['데이터_타입']

        if column_name not in table_data.columns:
            continue

        column_data = table_data[column_name]

        # 수치형 데이터 처리
        if data_type in ['tinyint', 'smallint', 'mediumint', 'int', 'bigint', 'float', 'double', 'decimal']:
            outlier_info = detect_outliers_numeric(column_data)
            results.append({
                "테이블명": table_name,
                "컬럼명": column_name,
                "데이터_타입": data_type,
                "분석결과": f"정상 범위: {outlier_info['normal_range']}, 이상치: {outlier_info['outliers']}",
            })

        # 텍스트 데이터 처리
        elif data_type in ['varchar', 'char', 'text']:
            outlier_info = detect_outliers_text(column_data)
            results.append({
                "테이블명": table_name,
                "컬럼명": column_name,
                "데이터_타입": data_type,
                "분석결과": f"자주 나타나는 값: {outlier_info['frequent_values']}, 이상치: {outlier_info['outliers']}",
            })

        # 날짜 데이터 처리
        elif data_type in ['date', 'datetime', 'timestamp', 'year']:
            outlier_info = detect_outliers_date(column_data)
            results.append({
                "테이블명": table_name,
                "컬럼명": column_name,
                "데이터_타입": data_type,
                "분석결과": f"날짜 범위: {outlier_info['date_range']}",
            })

        else:
            results.append({
                "테이블명": table_name,
                "컬럼명": column_name,
                "데이터_타입": data_type,
                "분석결과": "지원되지 않는 데이터 유형입니다.",
            })

    return results

def main():
    schema_name = 'sakila'

    # 스키마 정보와 테이블 데이터 로드
    print("스키마의 컬럼 정보를 조회 중...")
    column_info = fetch_column_info(engine, schema_name)

    print("테이블 데이터를 로드 중...")
    table_names = column_info['테이블명'].unique()

    all_results = []
    for table_name in table_names:
        try:
            print(f"테이블 {table_name} 데이터 처리 중...")
            table_data = fetch_table_data(engine, table_name)
            results = analyze_table_data(table_name, table_data, column_info)
            all_results.extend(results)
        except Exception as e:
            print(f"테이블 {table_name} 처리 중 오류 발생: {e}")

    # 결과를 DataFrame으로 변환 및 저장
    result_df = pd.DataFrame(all_results)
    print("\n분석 결과:")
    print(result_df)

    output_file = "./sakila/sakila_이상치_분석결과_1.csv"
    result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"결과가 {output_file}에 저장되었습니다.")

if __name__ == "__main__":
    main()
