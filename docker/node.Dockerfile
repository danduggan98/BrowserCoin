FROM python:3.8.5-alpine
WORKDIR /node

COPY ./browsercoin/ browsercoin/
COPY .env .env
COPY definitions.py definitions.py
COPY requirements.txt requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/node"
RUN pip install -r requirements.txt
ENTRYPOINT [ "python3", "browsercoin/servers/node_server.py" ]
