FROM python:3.9-bullseye

RUN pip3 install --no-cache-dir --upgrade \
    pip \
    virtualenv

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
&& rm -rf /var/lib/apt/lists/* \
&& groupadd --gid 1000 appuser \
&& useradd --uid 1000 --gid 1000 -ms /bin/bash appuser

USER appuser
WORKDIR /home/appuser

RUN git clone https://github.com/streamlit/streamlit-example.git app

ENV VIRTUAL_ENV=/home/appuser/venv
RUN virtualenv ${VIRTUAL_ENV}
RUN ${VIRTUAL_ENV}/bin/pip install -r app/requirements.txt

COPY run.sh /home/appuser/run.sh
# RUN chmod +x /home/appuser/run.sh

EXPOSE 8501

ENTRYPOINT ["/home/appuser/run.sh"]