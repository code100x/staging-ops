FROM postgres:15


RUN apt-get update
RUN apt-get install -y python3 python3-pip

# copy requirements to image dir
COPY requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt

COPY backup.py /backup.py

CMD ["python3", "/backup.py"]