import pandas as pd
import numpy as np
import glob

# CSV 파일 로딩
file_paths = glob.glob("../../data_utf8/*.csv")

results = []

for file in file_paths:  # file list
    file_name = file.split("\\")[-1]  # 경로 제거해서 파일명만
    df = pd.read_csv(file)

    for column in df.columns:  # 각 컬럼 별 통계값 계산

        non_null_data = df[column].dropna()  # 결측치 제거

        null_count = non_null_data.isnull().sum() + (df[column] == '').sum()  # Null 혹은 빈값 갯수

        # 결과 dictionary, 수치형 및 범주형 공통 특성
        column_result = {
            '파일명': file_name,
            '컬럼명': column,
            'null 수': null_count
        }

        if pd.api.types.is_numeric_dtype(non_null_data):  # 수치형 데이터 case
            column_result.update({
                '컬럼구분': '수치형',
                '최댓값': non_null_data.max(),
                '최솟값': non_null_data.min(),
                '평균(mean)': non_null_data.mean(),
                '중앙값(median)': non_null_data.median(),
                '최빈값_수치(mode)': non_null_data.mode()[0] if not non_null_data.mode().empty and non_null_data.mode()[0] >= 5 else None,
                '1분위수(1Q)': non_null_data.quantile(0.25),
                '3분위수(3Q)': non_null_data.quantile(0.75),
                'IQR': non_null_data.quantile(0.75) - non_null_data.quantile(0.25),
                '분산(variance)': non_null_data.var(),
                '표준편차(standard deviation)': non_null_data.std(),
                '범위(range)': non_null_data.max() - non_null_data.min(),
                '유일값 수': non_null_data.nunique(),
                '값 중복도 평균': non_null_data.value_counts().mean() if not non_null_data.value_counts().empty else None,
                '왜도(skewness)': non_null_data.skew(),
                '첨도(kurtosis)': non_null_data.kurtosis()
            })
        else:  # 범주형 데이터 case
            column_result.update({
                '컬럼구분': '범주형',
                '범주값 변화(고정/가변)': '고정' if non_null_data.apply(
                    lambda x: len(str(x)) if pd.notna(x) else 0).nunique() == 1 else '가변',
                '유일값 수': non_null_data.nunique(),
                '최빈값_범주(mode)': non_null_data.mode()[0] if not non_null_data.mode().empty and
                                                           isinstance(non_null_data.mode()[0], (int, float)) and
                                                           non_null_data.mode()[0] >= 5 else None,
                '범주 집합': set(non_null_data.unique()),  # 범주 리스트를 set으로 변환
                '값 중복도 평균': non_null_data.value_counts().mean() if not non_null_data.value_counts().empty else None
            })

        # 결과 저장
        results.append(column_result)

# 결과 -> DataFrame
result_df = pd.DataFrame(results)

# DataFrame -> CSV file
result_df.to_csv("../../1-1. describe_result/statistics/summary_statistics2.csv", index=False, encoding='utf-8-sig')


print(result_df.head())
