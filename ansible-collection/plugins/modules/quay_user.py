#!/usr/bin/python

import json
from ansible.module_utils.basic import AnsibleModule


def main():
    fields = {
        "username": {"required": True, "type": "str"},
        "password": {"required": False, "type": "str"},
        "email": {"required": False, "type": "str"},
        "verified": {"required": False, "type": "bool", "default": True},
        "exact_teams": {"required": False, "type": "list"},
        "add_teams": {"required": False, "type": "list"},
        "remove_teams": {"required": False, "type": "list"},
        "state": {
            "default": "present",
            "choices": ["present", "absent"],
            "type": "str",
        },
    }
    mutually_exclusive = [["exact_teams", "add_teams", "remove_teams"]]
    # NOTE: http://mobygeek.net/blog/2016/02/16/ansible-module-development-parameters/
    module = AnsibleModule(argument_spec=fields, mutually_exclusive=mutually_exclusive)
    module.exit_json(changed=True, meta=json.dumps(module.params))


if __name__ == "__main__":
    main()
