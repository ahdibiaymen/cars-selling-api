FROM python:3.10-alpine


ENV USERNAME=cars_api

RUN adduser -D -h /cars_api -u 1000 ${USERNAME}

WORKDIR /cars_api
COPY /app ./app
COPY /requirements.txt ./

COPY --chown=${USERNAME}:${USERNAME} /docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod u+x ./docker-entrypoint.sh

RUN apk add --no-cache gcc musl-dev linux-headers
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
USER $USERNAME

ENTRYPOINT ["./docker-entrypoint.sh"]
