FROM python:latest

LABEL Maintainer="sujayrittikar"

WORKDIR /usr/app/src

COPY anime_scraper.py ./
COPY requirements.txt ./

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python3 -m pip install -r requirements.txt
RUN python3 -m pip install requests

CMD [ "python3", "./anime_scraper.py" ]