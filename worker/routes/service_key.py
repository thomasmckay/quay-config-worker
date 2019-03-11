import logging
import json
from flask import request

from data.database import (ServiceKey, User)
from data import model

from decorators import task_resources

logger = logging.getLogger(__name__)

@task_resources
def process(resources):
  response = []
  changed = True

  for resource in resources:
    p_state = resource['state']
    p_name = resource['name']
    p_key = resource['key']
    p_service = resource['service']
    p_jwk = resource['jwk']
    p_expiration = resource['expiration']
    p_metadata = {}

    try:
      servicekey = model.service_keys.get_service_key(p_key, p_service)
    except model.ServiceKeyDoesNotExist:
      servicekey = None
    if p_state == 'absent':
      if servicekey is not None:
        servicekey.delete_instance()
        changed = True
        response.append("Service Key '%s' removed" % p_name)
      else:
        response.append("Service Key '%s' does not exist" % p_name)
    else:  # present
      if servicekey is None:
        if p_jwk is not None:
          model.service_keys.create_service_key(p_name, p_kid, p_service, p_metadata,
                                                p_expiration)
        else:
          model.service_keys.generate_service_key(p_service, p_expiration, p_key, p_name, p_metadata,
                                                  p_expiration)
      else:
        response.append("Organization '%s' exists" % p_name)
        # TODO: update

  return {
    "failed": False,
    "changed": changed,
    "meta": response
  }, 200
