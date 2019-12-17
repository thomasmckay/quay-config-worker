import logging
import json
from uuid import UUID
import hashlib

from ansible.module_utils.basic import AnsibleModule

from data.database import db
from data.database import (Repository, User)
from data import model
from app import app
from worker import ansible_queue

from decorators import task_resources

logger = logging.getLogger(__name__)

def enqueue(name, resource):
  ansible_queue.put([name], json.dumps(resource))

@task_resources
def process(resources):
  response = []
  changed = False

  for resource in resources:
    p_state = resource['state']
    p_name = resource['name']

    if p_state == 'absent':
      return {
        "failed": True,
        "msg": "TODO: Work Queue 'absent' not implemented"
      }, 400
    else: # present
      changed = True
      ansible_queue.put(p_name, json.dumps(resource))

  return {
    "failed": False,
    "changed": changed,
    "meta": response
  }, 200
