import logging
import json
from flask import request

from data.database import ImageStorageLocation
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
            image_storage_location = ImageStorageLocation.get(name=p_name)
        except ImageStorageLocation.DoesNotExist:
            image_storage_location = None
        if p_state == "absent":
            if image_storage_location is not None:
                changed = True
                image_storage_location.delete_instance()
                response.append("Image Storage Location '%s' deleted" % p_name)
                changed = True
            else:
                response.append("Image Storage Location '%s' does not exist" % p_name)
        else:
            if image_storage_location is None:
                changed = True
                image_storage_location = ImageStorageLocation.create(name=p_name)
                response.append("Image Storage Location '%s' created" % p_name)
            else:
                response.append("Image Storage Location '%s' exists" % p_name)

    return {"failed": False, "changed": changed, "meta": response}, 200
