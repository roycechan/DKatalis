FROM python:3.8-slim
COPY app/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . ./
EXPOSE 5000
CMD [ "gunicorn", "--workers=5", "--threads=1", "-b 0.0.0.0:80", "app:server"]