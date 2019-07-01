FROM python:3-alpine
MAINTAINER Matheus Zaglia <mzaglia@gmail.com.br>

# Install dependencies
RUN apk update
RUN apk add --no-cache gcc musl-dev mariadb-dev

# Prepare work directory
RUN mkdir -p /bdc_stac
WORKDIR /bdc_stac

# Get opensearch source and install python requirements
COPY requirements.txt /bdc_stac
RUN pip install -r requirements.txt

# Setting environment variables
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP __init__
ENV FLASK_DEBUG True
# Expose the Flask port
EXPOSE 5000

# Run the opensearch application
CMD ["flask", "run", "--host=0.0.0.0"]