# Official ubuntu image
FROM avr24rakuten/karma:karma_base

# ADD ARGUMENT FOR DOCKER IMAGE BUILD THEN CREATE ENV VARIABLE AVAILABLE FOR KARMA
ARG HOST_IP
ENV HOST_IP=$HOST_IP

COPY docker/karma_test_int/requirements.txt ./
COPY test_int ./app/

RUN apt update && pip install -r requirements.txt

WORKDIR /app

CMD ["tail", "-f", "/dev/null"]