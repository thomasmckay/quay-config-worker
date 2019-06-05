import logging
import json
from uuid import UUID
import hashlib
import subprocess

from ansible.module_utils.basic import AnsibleModule

from data.database import db
from data.database import (Repository, User)
from data import model
from app import (app, authentication, instance_keys)
from util.security.registry_jwt import generate_bearer_token

from decorators import task_resources

from work_queue import enqueue

logger = logging.getLogger(__name__)

@task_resources
def process(resources):
  return process_resources(resources)

def process_resources(resources):
  response = []
  changed = False

  for resource in resources:
    if resource['work_queue'] == True:
        resource['task'] = 'skopeo'
        enqueue('skopeo', resource)
        continue

    p_user = resource['user']
    p_password = resource['password']
    p_state = resource['state']
    p_project = resource['project']
    p_repository = resource['repository']
    p_tag = resource['tag']
    p_src_credentials = resource['src_credentials']
    p_src_image = resource['src_image']
    p_src_tag = resource['src_tag']
    p_src_tls_verify = resource['src_tls_verify']
    p_dest_credentials = resource['dest_credentials']
    p_dest_image = resource['dest_image']
    p_dest_tag = resource['dest_tag']
    p_dest_tls_verify = resource['dest_tls_verify']

    repository = model.repository.get_repository(p_project, p_repository)
    if repository is None:
      response.append("Repository '%s/%s' does not exist" % (p_project, p_repository))
      return {
        "failed": True,
        "msg": response
      }, 400

    ### auth_token = jwt_bearer_token(p_user, p_project, p_repository)

    if p_state == 'present':
      args = ["/usr/bin/skopeo", "copy",
              "--dest-creds", "%s:%s" % (p_user, authentication.encrypt_user_password(p_password)),
              "--src-tls-verify=%s" % p_src_tls_verify,
              "--dest-tls-verify=false",
              "docker://%s:%s" % (p_src_image, p_src_tag),
              "docker://%s/%s/%s:%s" % (app.config['SERVER_HOSTNAME'], p_project, p_repository, p_tag)
      ]
      if p_src_credentials:
        command = command + ["--src-creds", p_src_credentials]

      job = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      stdout_data, stderr_data = job.communicate()

      if job.returncode != 0:
        response.append("Source '%s:%s' failed to sync.\nSTDOUT: %s\nSTDERR: %s" %
                        (p_src_image, p_src_tag, stdout_data, stderr_data))
        return {
          "failed": True,
          "changed": changed,
          "msg": response
        }, 400
      else:
        changed = True
        response.append("Source '%s:%s' synced.\nSTDOUT: %s\nSTDERR: %s" %
                        (p_src_image, p_src_tag, stdout_data, stderr_data))

  return {
    "failed": False,
    "changed": changed,
    "meta": response
  }, 200

# util/security/registry_jwt.py
TOKEN_VALIDITY_LIFETIME_S = 60
def jwt_bearer_token(username, project, repository):
  CLAIM_TUF_ROOTS = 'com.apostille.roots'
  CLAIM_TUF_ROOT = 'com.apostille.root'
  DISABLED_TUF_ROOT = '$disabled'


  audience = app.config['SERVER_HOSTNAME']
  context = {}
  context.update({
    CLAIM_TUF_ROOTS: None,
    CLAIM_TUF_ROOT: DISABLED_TUF_ROOT
  })
  subject = username
  access = [{
    'type': 'repository',
    'name': "%s/%s" % (project, repository),
    'actions': ['push'],
  }]

  auth_token = generate_bearer_token(audience, subject, context, access,
                                     TOKEN_VALIDITY_LIFETIME_S, instance_keys)

  return auth_token
