FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt constraints.txt ./
RUN pip install --no-cache-dir -r requirements.txt -c constraints.txt

COPY . .

EXPOSE 8000
CMD ["python", "main.py", "--serve"]
