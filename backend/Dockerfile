FROM python:3.9
WORKDIR /app
COPY . /app
RUN pip install Flask flask-cors openai
EXPOSE 5500
CMD ["python", "app.py"]
