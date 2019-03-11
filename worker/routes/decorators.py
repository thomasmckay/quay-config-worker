import logging
import json
from flask import request
from functools import wraps
from util.http import abort

logger = logging.getLogger(__name__)

def task_resources(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    params = request.get_json()
    resources = []
    if params is not None and params.has_key("results"):
      for result in params["results"]:
        resources.append(json.loads(result["meta"]))
    elif params is not None and params.has_key("meta"):
      resources.append(json.loads(params["meta"]))
    else:
      logger.error('Unable to load resources from call params: %s', params)
      abort(400, message='Missing resources from params')

    return func(resources, *args, **kwargs)
  return wrapper
