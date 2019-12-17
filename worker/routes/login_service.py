import logging
import json
from flask import request

from data.database import LoginService
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
            login_service = LoginService.get(name=p_name)
        except LoginService.DoesNotExist:
            login_service = None
        if p_state == "absent":
            if login_service is not None:
                changed = True
                login_service.delete_instance()
                response.append("Login Service '%s' deleted" % p_name)
                changed = True
            else:
                response.append("Login Service '%s' does not exist" % p_name)
        else:
            if login_service is None:
                changed = True
                login_service = LoginService.create(name=p_name)
                response.append("Login Service '%s' created" % p_name)
            else:
                response.append("Login Service '%s' exists" % p_name)

    return {"failed": False, "changed": changed, "meta": response}, 200
