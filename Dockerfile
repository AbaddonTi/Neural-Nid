FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install Flask gunicorn flask_cors openai
CMD ["gunicorn", "--workers=3", "--bind=0.0.0.0:5500", "Backend:app"]
