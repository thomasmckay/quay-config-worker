import logging
import json
from flask import request
import hashlib

from data.database import db
from data.database import Repository, RepositoryTag
from data import model
from data.registry_model import registry_model

from decorators import task_resources

logger = logging.getLogger(__name__)


@task_resources
def process(resources):
    response = []
    changed = True

    for resource in resources:
        p_state = resource["state"]
        p_project = resource["project"]
        p_name = resource["name"]
        p_repository = resource["repository"]
        p_image_id = resource["image_id"]

        repository = model.repository.get_repository(p_project, p_repository)
        if repository is None:
            return (
                {
                    "failed": True,
                    "msg": "Repository '%s/%s' does not exist"
                    % (p_project, p_repository),
                },
                400,
            )

        image_id = hashlib.md5(p_image_id).hexdigest()
        image = model.image.get_image(repository, image_id)
        if image is None:
            print json.dumps(
                {"failed": False, "msg": "Image '%s' does not exist" % p_image_id}
            )
            sys.exit(1)

        registry_repository = registry_model.lookup_repository(p_project, p_repository)

        # tag = registry_model.get_repo_tag(registry_repository, p_name)
        matching = model.tag.list_repository_tags(p_project, p_repository, False, True)
        try:
            tag = matching.where(RepositoryTag.name == p_name).get()
        except RepositoryTag.DoesNotExist:
            tag = None

        if p_state == "absent":
            if tag is not None:
                response.append("XXXXX remove tag")
                return {"failed": False, "changed": changed, "meta": response}, 400
            else:
                response.append("Tag '%s' does not exist" % tag)
                return {"failed": False, "changed": changed, "meta": response}, 200
        else:  # present
            if tag is None:
                tag = model.tag.create_or_update_tag(
                    p_project, p_repository, p_name, image.docker_image_id
                )
                response.append("Tag '%s' created" % p_name)
            else:
                tag = model.tag.create_or_update_tag(
                    p_project, p_repository, p_name, image.docker_image_id
                )
                response.append("Tag '%s' exists" % p_name)

            tag.lifetime_end_ts = tag.lifetime_start_ts + 100000
            tag.save()

            storage_transformation = "squash"
            storage_location = "local_us"
            storage_metadata = None
            signature_kind = "gpg2"
            storage = model.image.find_derived_storage_for_image(
                tag, storage_transformation, storage_metadata
            )

            # if storage is None:
            #     storage = model.image.find_or_create_derived_storage(tag, storage_transformation, storage_location)
            #     model.storage.find_or_create_storage_signature(storage, signature_kind)
            #     response.append("Storage added to Tag")

            # ???? tmp?
            tmptag = registry_model.get_repo_tag(registry_repository, p_name)
            registry_model.backfill_manifest_for_tag(tmptag)

    return {"failed": False, "changed": changed, "meta": response}, 200
