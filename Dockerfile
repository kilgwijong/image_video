# Dockerfile

# 1. 베이스 이미지 선택 (파이썬 3.11 버전)
FROM python:3.11-slim

# 2. 작업 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. 작업 디렉토리 생성 및 설정
WORKDIR /app

# 4. 필요한 라이브러리 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5. 프로젝트 파일 복사
COPY . /app/

# 6. 정적 파일 및 미디어 파일 경로 설정 (이 부분은 settings.py와 연관됨)
#    (이 예제에서는 Django가 직접 처리하도록 설정)

# 7. 서버 실행 (Gunicorn 사용)
#    Gunicorn 설치
RUN pip install gunicorn

#    Gunicorn으로 Django 서버 실행
#    config.wsgi:
#    - 'config'는 wsgi.py 파일이 있는 폴더 이름입니다.
#    - 'wsgi'는 wsgi.py 파일 이름입니다.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]