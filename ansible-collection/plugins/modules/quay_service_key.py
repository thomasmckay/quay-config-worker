#!/usr/bin/python

import json
from ansible.module_utils.basic import AnsibleModule


def main():
    fields = {
        "name": {"required": True, "type": "str"},
        "key": {"required": True, "type": "str"},
        "service": {"required": False, "type": "str"},
        "jwk": {"required": False, "type": "str"},
        "expiration": {"required": False, "type": "str"},
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
