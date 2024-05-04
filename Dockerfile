FROM python:3.12

WORKDIR /app

COPY . /app/

RUN pip install poetry

RUN poetry config virtualenvs.create false && poetry install --no-dev

CMD ["poetry", "run", "python", "main.py"]
