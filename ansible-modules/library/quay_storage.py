#!/usr/bin/python

import json

from ansible.module_utils.basic import AnsibleModule

from data.database import db
from data.database import (Repository, User)
from data import model
from app import app as store

def main():
    fields = {
        "uri": {"required": True, "type": "str"},
        "user": {"required": True, "type": "str"},
        "name": {"required": True, "type": "str"},
        "description": {"required": False, "type": "str"},
        "public": {"default": False, "type": "bool"},
        "state": {
            "default": "present",
            "choices": ["present", "absent"],
            "type": "str"
        },
    }
    module = AnsibleModule(argument_spec=fields)
    changed = False
    p_name = module.params['name']

    user = model.user.get_user(module.params['user'])
    if user is None:
        print json.dumps({
            "failed": True,
            "msg": "User '%s' does not exist" % (module.params['user'])
        })
        sys.exit(1)

    repository = model.repository.get_repository(user.username, p_name)
    if module.params['state'] == 'absent':
        if repository is not None:
            changed = True
            print "???? delete repos"
            sys.exit(1)
        else:
            response = {
                "failed": False,
                "msg": "Repository '%s/%s' exists" % (user.username, p_name)
            }
    else:
        if repository is None:
            changed = True
            repository = model.repository.create_repository(user.username, "%s" % p_name, user)
        if module.params['public']:
            changed = True
            model.repository.set_repository_visibility(repository, 'public')

        if module.params['description'] and repository.description != description:
            changed = True
            repository.description = description
            repository.save()
        response = {
            "failed": False,
            "msg": "Repository '%s/%s' present" % (user.username, p_name)
        }

    module.exit_json(changed=changed, meta=response)

if __name__ == '__main__':
    main()
