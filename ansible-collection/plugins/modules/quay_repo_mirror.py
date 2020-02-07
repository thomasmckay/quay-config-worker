#!/usr/bin/python

import json
from ansible.module_utils.basic import AnsibleModule


def main():
    fields = {
        "user": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str"},
        "external_user": {"required": False, "type": "str"},
        "external_password": {"required": False, "type": "str"},
        "external_reference": {"required": True, "type": "str"},
        "external_tag": {"required": True, "type": "str"},
        "internal_robot": {"required": True, "type": "str"},
        "internal_namespace": {"required": True, "type": "str"},
        "internal_repository": {"required": True, "type": "str"},
        "sync_start_date": {"required": True, "type": "str"},
        "sync_interval": {"required": True, "type": "str"},
        "is_enabled": {"required": False, "type": "bool", "default": True},
        "state": {
            "default": "present",
            "choices": ["present", "absent"],
            "type": "str",
        },
    }
    module = AnsibleModule(argument_spec=fields)
    module.exit_json(changed=True, meta=json.dumps(module.params))


if __name__ == "__main__":
    main()
