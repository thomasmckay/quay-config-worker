import logging
import json
from flask import request

from data.database import (Repository, User)
from data import model

from decorators import task_resources

logger = logging.getLogger(__name__)

@task_resources
def process(resources):
  response = []
  changed = True

  for resource in resources:
    p_name = resource['name']
    p_user = resource['user']
    p_public = resource['public']
    p_state = resource['state']
    p_description = resource['description']

    user = model.user.get_user(p_user)
    if user is None:
      return {
        "failed": True,
        "msg": "User '%s' does not exist" % (p_user)
      }, 400

  return {
    "failed": False,
    "changed": changed,
    "meta": response
  }, 200
