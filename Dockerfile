FROM python:3.8-slim
COPY src/requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./
COPY csvs/ ./
EXPOSE 5000
CMD [ "gunicorn", "--workers=5", "--threads=1", "-b 0.0.0.0:80", "app:server"]