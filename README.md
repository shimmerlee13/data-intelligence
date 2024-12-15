# data-intelligence
공공데이터분석 (2024-2)

data-intelligence/  
├── 1. data/                 			# CSV 파일이 들어있는 폴더  
├── data_utf8/					# 1. data csv 파일 인코딩
├── 1-1. describe_result/			# 분석 코드 실행 결과가 들어있는 폴더
├───├──statistics				# (1) 파생변수 생성 코드 결과
├───├──smilarity				# (2) 공통, 대표속성 추출을 위한 유사도 분석 결과
├───├──├──smilarity_calculate 	# 유사도분석 결과
├── src/                  				# 분석 코드가 들어갈 폴더  
├───├──statistics				# (1) 파생변수 생성 코드
├───├──smilarity				# (2) 공통, 대표속성 추출을 위한 유사도 분석 코드
├───├──sakila					# (3) sakila 데이터 pk, fk 추출 코드
├── Dockerfile            				# Docker 환경 설정 파일  
├── environment.yml       			# Miniconda 환경 설정 파일  
├── .gitignore            				# Git에서 제외할 파일 목록  
└── README.md             			# 프로젝트 설명 파일  


실행순서
1. src/statistics/summary_statistics
2. src/statistics/summary_statistics_with_classification
3. src/smilarity/모든파일