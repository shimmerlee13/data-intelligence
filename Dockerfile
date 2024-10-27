# 미니콘다 베이스 이미지 사용
FROM continuumio/miniconda3

# 작업 디렉토리 설정
WORKDIR /app

# 환경 파일 복사 및 환경 설치
COPY environment.yml .

# Miniconda 환경 설치
RUN conda env create -f environment.yml

# 환경 활성화 명령 설정
SHELL ["conda", "run", "-n", "data_analysis_env", "/bin/bash", "-c"]

# 소스 코드와 데이터 폴더 복사
COPY src/ /app/src/
COPY data/ /app/data/

# 컨테이너 시작 시 Jupyter Notebook 실행 (필요에 따라 수정 가능)
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
