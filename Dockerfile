FROM python:3.10-alpine

WORKDIR /app

COPY . .

RUN pip install pipenv && \
    pipenv install --deploy --system && \
    pip uninstall pipenv -y

CMD ["python", "src/schedule.py"]