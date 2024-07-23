# Official ubuntu image
FROM avr24rakuten/karma:karma_base

COPY docker/karma_test_int/requirements.txt ./
COPY test_int ./app/

RUN apt update && pip install -r requirements.txt

WORKDIR /app

CMD ["tail", "-f", "/dev/null"]