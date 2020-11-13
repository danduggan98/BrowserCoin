FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine
WORKDIR /node

COPY ./browsercoin/ browsercoin/
COPY .env .env
COPY definitions.py definitions.py
COPY ./docker/node/requirements.txt requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/node"
RUN pip install -r requirements.txt

WORKDIR /node/browsercoin/servers
ENTRYPOINT [ "gunicorn" ]
CMD [ "--bind", "0.0.0.0:5000", "node_server:app" ]
