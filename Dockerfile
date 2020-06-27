FROM python:3.7
COPY ./sttapp/ /sttapp/
RUN pip install -r requirements.txt
WORKDIR /sttapp/
