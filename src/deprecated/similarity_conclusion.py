import pandas as pd
import numpy as np

# 전체 유사도 매트릭스 파일 경로 설정
overall_similarity_path = "../../data_parsing/similarity/similarity_calculate/overall_similarity.csv"

# 전체 유사도 매트릭스 파일 로드
overall_similarity_df = pd.read_csv(overall_similarity_path, header=None)

# 하위 10% 퍼센타일 유사도 값 계산
lower_percentile = np.percentile(overall_similarity_df.values[np.triu_indices_from(overall_similarity_df, k=1)], 10)

# 공통 속성 도출: 95% 상위 퍼센타일 이상의 유사도를 보이는 속성을 공통 속성으로 간주
upper_percentile = np.percentile(overall_similarity_df.values[np.triu_indices_from(overall_similarity_df, k=1)], 95)
common_attributes = []
for i in range(len(overall_similarity_df)):
    for j in range(i + 1, len(overall_similarity_df)):
        if overall_similarity_df.iat[i, j] >= upper_percentile:
            common_attributes.append(f"파일 {i+1}와 파일 {j+1}은 공통적인 특성을 가집니다.")

# 대표 속성 도출: 하위 10% 퍼센타일 이하 유사도를 가진 파일 쌍을 대표 속성으로 간주
representative_attributes = []
for i in range(len(overall_similarity_df)):
    for j in range(i + 1, len(overall_similarity_df)):
        if overall_similarity_df.iat[i, j] <= lower_percentile:
            representative_attributes.append(f"파일 {i+1}와 파일 {j+1}은 서로 유사도가 낮아 대표적인 특성을 가집니다.")

# 결론 출력
print("=== 공통 속성 ===")
if common_attributes:
    for attribute in common_attributes:
        print(attribute)
else:
    print("공통 속성을 가진 파일이 없습니다.")

print("\n=== 대표 속성 ===")
if representative_attributes:
    for attribute in representative_attributes:
        print(attribute)
else:
    print("대표 속성을 가진 파일이 없습니다.")

# 결과를 텍스트 파일로 저장
output_path = "../../data_parsing/deprecated/similarity_conclusion.txt"
with open(output_path, "w", encoding='utf-8') as f:
    f.write("=== 공통 속성 ===\n")
    if common_attributes:
        for attribute in common_attributes:
            f.write(attribute + "\n")
    else:
        f.write("공통 속성을 가진 파일이 없습니다.\n")
    f.write("\n=== 대표 속성 ===\n")
    if representative_attributes:
        for attribute in representative_attributes:
            f.write(attribute + "\n")
    else:
        f.write("대표 속성을 가진 파일이 없습니다.\n")

print("결론이 포함된 파일이 생성되었습니다:", output_path)