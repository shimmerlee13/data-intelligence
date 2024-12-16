# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 19:17:00 2024

@author: shimm
"""

from similarity.attribute_analysis import analyze_categorical, analyze_numerical

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