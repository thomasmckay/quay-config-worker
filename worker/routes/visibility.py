import logging
import json
from flask import request

from data.database import Visibility
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
            visibility = Visibility.get(name=p_name)
        except Visibility.DoesNotExist:
            visibility = None
        if p_state == "absent":
            if visibility is not None:
                changed = True
                visibility.delete_instance()
                response.append("Visibility '%s' deleted" % p_name)
                changed = True
            else:
                response.append("Visibility '%s' does not exist" % p_name)
        else:
            if visibility is None:
                changed = True
                visibility = Visibility.create(name=p_name)
                response.append("Visibility '%s' created" % p_name)
            else:
                response.append("Visibility '%s' exists" % p_name)

    return {"failed": False, "changed": changed, "meta": response}, 200
