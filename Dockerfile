FROM python:3.12
LABEL authors="Sapp"

WORKDIR /backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmpc-dev \
    libgmp-dev \
    libmpfr-dev \
    cron

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools
RUN pip install -r requirements.txt --no-cache-dir

COPY . .
RUN chmod +x entrypoint_django.sh
RUN chmod +x entrypoint_bot.sh
CMD ["/bin/bash", "./entrypoint_django.sh"]
