import logging
import json
import features
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

    repository = model.repository.get_repository(user.username, p_name)
    if p_state == 'absent':
      if repository is not None:
        changed = True
        model.repository.purge_repository(p_user, p_name)
      else:
        return {
          "failed": False,
          "msg": "Repository '%s/%s' exists" % (user.username, p_name)
        }, 400
    else:
      if repository is None:
        changed = True
        repository = model.repository.create_repository(user.username, "%s" % p_name, user)
        response.append("Repository '%s' created" % p_name)

      if repository.visibility.name == 'public' and p_public == False:
        changed = True
        model.repository.set_repository_visibility(repository, 'private')
        response.append("Repository visibility set to 'private'")
      elif repository.visibility.name == 'private' and p_public == True:
        changed = True
        model.repository.set_repository_visibility(repository, 'public')
        response.append("Repository visibility set to 'public'")

      if p_description and repository.description != p_description:
        changed = True
        repository.description = p_description
        response.append("Description updated")

  return {
    "failed": False,
    "changed": changed,
    "meta": response
  }, 200
