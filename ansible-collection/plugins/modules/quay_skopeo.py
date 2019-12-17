#!/usr/bin/python

import json
from ansible.module_utils.basic import AnsibleModule


def main():
    fields = {
        "work_queue": {"required": False, "type": "bool", "default": False},
        "user": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str"},
        "project": {"required": True, "type": "str"},
        "repository": {"required": True, "type": "str"},
        "tag": {"required": True, "type": "str"},
        "src_image": {"required": True, "type": "str"},
        "src_tag": {"required": True, "type": "str"},
        "src_credentials": {"required": False, "type": "str"},
        "src_tls_verify": {"required": False, "type": "bool", "default": True},
        "dest_image": {"required": False, "type": "str"},
        "dest_tag": {"required": False, "type": "str"},
        "dest_credentials": {"required": False, "type": "str"},
        "dest_tls_verify": {"required": False, "type": "bool", "default": True},
        "state": {"default": "present", "choices": ["present"], "type": "str"},
    }
    module = AnsibleModule(argument_spec=fields)
    module.exit_json(changed=True, meta=json.dumps(module.params))


if __name__ == "__main__":
    main()
