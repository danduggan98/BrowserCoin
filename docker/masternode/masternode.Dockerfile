FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine
WORKDIR /masternode

COPY ./browsercoin/ browsercoin/
COPY .env .env
COPY definitions.py definitions.py
COPY ./docker/masternode/requirements.txt requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/masternode"
RUN pip install -r requirements.txt

WORKDIR /masternode/browsercoin/servers
ENTRYPOINT [ "gunicorn" ]
CMD [ "--bind", "0.0.0.0:3000", "masternode_server:app" ]
