FROM python:3.11-slim
WORKDIR /app
COPY ./requirements.txt ./requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
COPY start.sh /app
RUN chmod +x /app/start.sh
CMD ["./start.sh"]

