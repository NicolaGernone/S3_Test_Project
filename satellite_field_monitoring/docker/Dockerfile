FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

CMD [ "python", "-m", "satellite_field_monitoring.satellite" ]