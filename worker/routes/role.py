import logging
import json
from flask import request

from data.database import Role
from data import model

from decorators import task_resources

logger = logging.getLogger(__name__)


@task_resources
def process(resources):
    response = []
    changed = True

    for resource in resources:
        p_state = resource["state"]
        p_name = resource["name"]

        try:
            role = Role.get(name=p_name)
        except Role.DoesNotExist:
            role = None
        if p_state == "absent":
            if role is not None:
                changed = True
                role.delete_instance()
                response.append("Role '%s' deleted" % p_name)
                changed = True
            else:
                response.append("Role '%s' does not exist" % p_name)
        else:
            if role is None:
                changed = True
                role = Role.create(name=p_name)
                response.append("Role '%s' created" % p_name)
            else:
                response.append("Role '%s' exists" % p_name)

    return {"failed": False, "changed": changed, "meta": response}, 200
