FROM python:3.12-alpine
 
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
 
WORKDIR /code
 
RUN apk add --no-cache \
    build-base
 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
COPY . .
 
EXPOSE 8000
 
CMD ["python", "dashboard.py"]