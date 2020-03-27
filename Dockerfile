FROM python:3.7-slim-buster

RUN apt-get update -y \
    && apt-get install -y libpq-dev git \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /bdc_stac

COPY requirements.txt /bdc_stac
COPY ./bdc_stac /bdc_stac
RUN pip install -r bdc_stac/requirements.txt

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
