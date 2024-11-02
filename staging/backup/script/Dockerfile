FROM postgres:15

RUN apt-get update
RUN apt-get install -y python3 python3-pip python3-venv

WORKDIR /app
# copy requirements to image dir
COPY requirements.txt .
RUN python3 -m venv venv && \
    ./venv/bin/pip install --upgrade pip && \
    ./venv/bin/pip install -r requirements.txt
# Add the virtual environment to PATH
ENV PATH="/app/venv/bin:$PATH"
COPY . .

CMD ["python3", "app.py"]