import logging
import json
from flask import request

from data.database import TeamRole
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
            team_role = TeamRole.get(name=p_name)
        except TeamRole.DoesNotExist:
            team_role = None
        if p_state == "absent":
            if team_role is not None:
                changed = True
                team_role.delete_instance()
                response.append("Team Role '%s' deleted" % p_name)
                changed = True
            else:
                response.append("Team Role '%s' does not exist" % p_name)
        else:
            if team_role is None:
                changed = True
                team_role = TeamRole.create(name=p_name)
                response.append("Team Role '%s' created" % p_name)
            else:
                response.append("Team Role '%s' exists" % p_name)

    return {"failed": False, "changed": changed, "meta": response}, 200
