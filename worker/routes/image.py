import logging
import json
from uuid import UUID
import hashlib

from ansible.module_utils.basic import AnsibleModule

from data.database import db
from data.database import (Repository, User)
from data import model
from app import app as store

from decorators import task_resources

logger = logging.getLogger(__name__)

@task_resources
def process(resources):
  response = []
  changed = False

  for resource in resources:
    p_state = resource['state']
    p_project = resource['project']
    p_repository = resource['repository']
    p_image_id = resource['image_id']
    image_id = hashlib.md5(p_image_id).hexdigest()

    repository = model.repository.get_repository(p_project, p_repository)
    if repository is None:
      return {
        "failed": True,
        "msg": "Repository '%s/%s' exists" % (p_project, p_repository)
      }, 400

    image = model.image.get_image(repository, image_id)

    if p_state == 'absent':
      return {
        "failed": True,
        "msg": "TODO: Image 'absent' not implemented"
      }, 400
    else:  # present
      if image is None:
        changed = True
        username = None
        translations = {}
        preferred_location = "local_us"
        image = model.image.find_create_or_link_image(image_id, repository, username,
                                                      translations, preferred_location)

        image.storage.uuid = UUID(bytes=hashlib.md5(p_image_id).digest())
        image.storage.uploading = False
        image.storage.content_checksum = 'tarsum+sha256:' + hashlib.md5(image_id).hexdigest()
        image.storage.save()
        model.storage.save_torrent_info(image.storage, 1, 'deadbeef')
        model.storage.set_image_storage_metadata(image_id, p_project, p_repository, 1024, 2 * 1024)

        image.security_indexed = False
        image.security_indexed_engine = -1
        image.save()

        created = "2013-06-23 00:00:00"
        comment = "no comment"
        command = ""
        v1_json_metadata = json.dumps({'id': image_id})
        parent = None
        image = model.image.set_image_metadata(image_id, p_project, p_repository, created,
                                               comment, command, v1_json_metadata, parent)
        image.storage.content_checksum = 'tarsum+sha256:' + hashlib.md5(image_id).hexdigest()
        image.storage.save()

        response.append("Image created")
      else:
        response.append("Image exists")

      response.append("????? image=%s" % image.id)
      response.append("????? storage=%s" % image.storage.id)

  return {
    "failed": False,
    "changed": changed,
    "meta": response
  }, 200
