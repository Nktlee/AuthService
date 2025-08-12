FROM python:3.11.4

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["sh", "-c", "alembic upgrade head && python src/main.py"]