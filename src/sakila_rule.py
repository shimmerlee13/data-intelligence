import pandas as pd
from sqlalchemy import create_engine
import re

# SQLAlchemy를 사용해 MySQL 데이터베이스 연결 설정
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
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql(query, engine)


def extract_rules(data, column_info):
    """컬럼 정보와 데이터를 기반으로 업무 규칙 추출"""
    rules = {}
    for _, row in column_info.iterrows():
        table_name = row['테이블명']
        column_name = row['컬럼명']
        data_type = row['데이터_타입']

        if table_name not in data:
            continue  # 해당 테이블 데이터가 없으면 건너뜀

        column_data = data[table_name][column_name].dropna()  # 결측값 제외

        # 텍스트형 데이터에서만 이메일 형식 검증
        if data_type in ['varchar', 'char', 'text']:
            # 이메일 형식 검증 함수
            def is_email(value):
                email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
                return bool(re.match(email_pattern, value))

            if len(column_data) > 0:
                email_like = column_data.apply(lambda x: is_email(str(x))).sum()
                email_percentage = email_like / len(column_data) * 100
                if email_percentage >= 80:  # 80% 이상이 이메일 형식이면
                    rules[f"{table_name}.{column_name}"] = f"이메일 컬럼으로 추정: {email_percentage:.2f}%의 데이터가 이메일 형식입니다."
                    continue

            # 텍스트형 기본 규칙
            unique_count = column_data.nunique()
            rules[f"{table_name}.{column_name}"] = f"텍스트형 컬럼: 고유값 {unique_count}개가 있습니다."

        # 수치형 데이터 타입 처리
        elif data_type in ['tinyint', 'smallint', 'mediumint', 'int', 'bigint', 'float', 'double', 'decimal']:
            if column_data.empty:
                rules[f"{table_name}.{column_name}"] = "수치형 컬럼: 데이터가 없습니다."
            else:
                min_val = column_data.min()
                max_val = column_data.max()
                rules[f"{table_name}.{column_name}"] = f"수치형 컬럼: 값의 범위는 {min_val} ~ {max_val}입니다."

        # 날짜형 데이터 타입 처리 (Year 속성 추가)
        elif data_type in ['date', 'datetime', 'timestamp', 'year']:
            if column_data.empty:
                rules[f"{table_name}.{column_name}"] = "날짜형 컬럼: 데이터가 없습니다."
            else:
                min_date = column_data.min()
                max_date = column_data.max()
                min_year = pd.to_datetime(column_data).dt.year.min()
                max_year = pd.to_datetime(column_data).dt.year.max()
                rules[f"{table_name}.{column_name}"] = (
                    f"날짜형 컬럼: 값의 범위는 {min_date} ~ {max_date}, "
                    f"연도 범위는 {min_year} ~ {max_year}입니다."
                )

        # 이진(Binary) 데이터 처리
        elif data_type in ['boolean', 'tinyint'] and column_data.nunique() <= 2:
            unique_values = column_data.unique()
            rules[f"{table_name}.{column_name}"] = f"이진(Binary) 컬럼: 값은 {unique_values.tolist()}입니다."

        # 그 외 데이터 타입 처리
        else:
            rules[f"{table_name}.{column_name}"] = "명확한 규칙을 찾을 수 없습니다."

    return rules


def main():
    try:
        schema_name = 'sakila'  # 분석할 스키마 이름

        # 1. 컬럼 정보 조회
        print("스키마의 모든 컬럼 정보를 조회 중...")
        column_info = fetch_column_info(engine, schema_name)

        # 2. 각 테이블 데이터 조회
        print("테이블 데이터를 로드 중...")
        table_names = column_info['테이블명'].unique()
        table_data = {}
        for table_name in table_names:
            try:
                print(f"테이블 {table_name} 데이터 로드 중...")
                table_data[table_name] = fetch_table_data(engine, table_name)
            except Exception as e:
                print(f"테이블 {table_name} 데이터 로드 중 오류 발생: {e}")

        # 3. 업무 규칙 추출
        print("\n업무 규칙을 추출 중...")
        rules = extract_rules(table_data, column_info)

        # 4. 결과 출력
        print("\n업무 규칙 추출 결과:")
        for column, rule in rules.items():
            print(f"{column} - {rule}")
    finally:
        # SQLAlchemy 연결 해제
        engine.dispose()


# 실행
main()