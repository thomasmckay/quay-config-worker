#!/usr/bin/python

import json
from ansible.module_utils.basic import AnsibleModule


def main():
    fields = {
        "state": {
            "default": "present",
            "choices": ["present", "reset", "migrate"],
            "type": "str",
        },
    }
    module = AnsibleModule(argument_spec=fields)
    module.exit_json(changed=True, meta=json.dumps(module.params))


if __name__ == "__main__":
    main()
