FROM python:3.8 as builder
RUN pip install pipenv
WORKDIR /app
COPY Pipfile* ./
RUN pipenv install
RUN pipenv run pip freeze > requirements.txt

FROM python:3.8
WORKDIR /app
COPY --from=builder /app/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT python run.py