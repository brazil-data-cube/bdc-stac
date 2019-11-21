FROM python:3.7-slim-buster

# Prepare work directory

RUN apt-get update -y \
    && apt-get install -y libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /bdc_stac
WORKDIR /bdc_stac

# Get opensearch source and install python requirements
COPY requirements.txt /bdc_stac
RUN pip install -r requirements.txt

# Expose the Flask port
EXPOSE 5000

# Run the opensearch application
CMD ["flask", "run", "--host=0.0.0.0"]