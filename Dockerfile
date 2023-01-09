FROM python:latest

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

WORKDIR /adapter
COPY adapter.py /adapter

CMD ["python3", "-u", "adapter.py"]