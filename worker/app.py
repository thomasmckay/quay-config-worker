
import logging
import json
import os
import yaml

from Crypto.PublicKey import RSA
from jwkest.jwk import RSAKey

from flask import Flask, request, Request
from flask_principal import Principal
from util.saas.analytics import Analytics
from data import database
from data import model
from data.queue import WorkQueue
from util.metrics.metricqueue import MetricQueue
from util.metrics.prometheus import PrometheusPlugin
# from util.names import urn_generator

from _init import config_provider
from config import DefaultConfig

app = Flask(__name__)
logger = logging.getLogger(__name__)

app.config.from_object(DefaultConfig())
app.teardown_request(database.close_db_filter)  # ???? why is this needed?
app.config.update(yaml.load(os.environ.get('ANSIBLE_WORKER_CONFIG', '')))
app.config.update(json.loads(os.environ.get('ANSIBLE_WORKER_OVERRIDE', '{}')))
analytics = Analytics(app)

@staticmethod
def create_transaction(db):
  return db.transaction()
tf = create_transaction

prometheus = PrometheusPlugin(app)
metric_queue = MetricQueue(prometheus)

ansible_queue = WorkQueue('ansible', tf, has_namespace=False, metric_queue=metric_queue)

database.configure(app.config)
app.teardown_request(database.close_db_filter)

model.config.app_config = app.config

# ???? This is not correct. The signing key needs to match app.
docker_v2_signing_key = RSAKey(key=RSA.generate(2048))

# class RequestWithId(Request):
#   request_gen = staticmethod(urn_generator(['request']))

#   def __init__(self, *args, **kwargs):
#     super(RequestWithId, self).__init__(*args, **kwargs)
#     self.request_id = self.request_gen()


# @app.before_request
# def _request_start():
#   logger.debug('Starting request: %s (%s)', request.request_id, request.path,
#                extra={"request_id": request.request_id})

# @app.after_request
# def _request_end(resp):
#   jsonbody = request.get_json(force=True, silent=True)
#   values = request.values.to_dict()

#   if jsonbody and not isinstance(jsonbody, dict):
#     jsonbody = {'_parsererror': jsonbody}

#   if isinstance(values, dict):
#     filter_logs(values, FILTERED_VALUES)

#   extra = {
#     "endpoint": request.endpoint,
#     "request_id" : request.request_id,
#     "remote_addr": request.remote_addr,
#     "http_method": request.method,
#     "original_url": request.url,
#     "path": request.path,
#     "parameters":  values,
#     "json_body": jsonbody,
#     "confsha": CONFIG_DIGEST,
#   }

#   if request.user_agent is not None:
#     extra["user-agent"] = request.user_agent.string

#   logger.debug('Ending request: %s (%s)', request.request_id, request.path, extra=extra)
#   return resp

# app.request_class = RequestWithId

Principal(app, use_sessions=False)
