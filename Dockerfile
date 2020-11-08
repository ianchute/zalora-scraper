FROM python:3.7-slim

COPY requirements.txt /scraper/
COPY *.py /scraper/
COPY test.sh /scraper/
RUN chmod +x /scraper/test.sh

WORKDIR /scraper

RUN pip install --upgrade pip \
    &&  pip install --trusted-host pypi.python.org --requirement requirements.txt

CMD ["sh", "test.sh"]