#!/usr/bin/python

import json
from ansible.module_utils.basic import AnsibleModule

def main():
  fields = {
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
  module.exit_json(changed=True, meta=json.dumps(module.params))

if __name__ == '__main__':
    main()
