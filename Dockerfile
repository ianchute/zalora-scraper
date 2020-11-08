FROM python:3.7-slim

COPY requirements.txt /scraper/
COPY *.py /scraper/

WORKDIR /scraper

RUN pip install --upgrade pip \
    &&  pip install --trusted-host pypi.python.org --requirement requirements.txt

CMD ["python", "-m", "test"]