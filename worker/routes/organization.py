import logging

from app import app as store
from data import model

from decorators import task_resources

logger = logging.getLogger(__name__)

@task_resources
def process(resources):
  response = []
  changed = True

  for resource in resources:
    p_state = resource['state']
    p_name = resource['name']
    p_user = resource['user']
    p_email = resource['email']

    user = model.user.get_user(p_user)
    if user is None:
      return {
        "failed": True,
        "msg": "User '%s' does not exist" % (p_user)
      }, 400

    try:
      organization = model.organization.get_organization(p_name)
    except model.InvalidOrganizationException:
      organization = None
    if p_state == 'absent':
      if organization is not None:
        model.user.mark_namespace_for_deletion(organization, store.all_queues, store.namespace_gc_queue)
        changed = True
        response.append("Organization '%s' scheduled for removal" % p_name)
      else:
        response.append("Organization '%s' does not exist" % p_name)
    else:  # present
      if organization is None:
        changed = True
        organization = model.organization.create_organization(p_name, p_email, user)
        response.append("Organization '%s' created" % p_name)
      else:
        response.append("Organization '%s' exists" % p_name)
        # ???? update email if different

  return {
    "failed": False,
    "changed": changed,
    "meta": response
  }, 200
