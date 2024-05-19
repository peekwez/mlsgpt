FROM python:3.12

LABEL author="Kwesi P Apponsah" \
    author-email="kwesi@kwap-consulting.com"

#RUN curl -sSL https://install.python-poetry.org | python3 -
RUN pip install poetry
ENV PATH="${PATH}:/root/.local/bin"

# working directory
WORKDIR /app

# add directories
ADD ./mlsgpt /app/mlsgpt
ADD ./assets /app/assets
ADD ./pyproject.toml /app/pyproject.toml
ADD ./README.md /app/README.md

RUN pip install --upgrade pip
RUN poetry config virtualenvs.create false && poetry install --compile
RUN pip install --upgrade certifi

EXPOSE 80
CMD ["dotenv", "--file=.env", "run", "mlsgpt", "run-services", "--api-version=v2", "--ngrok"]