#!/usr/bin/python

import json
from ansible.module_utils.basic import AnsibleModule

def main():
  fields = {
    "project": {"required": True, "type": "str"},
    "repository": {"required": True, "type": "str"},
    "image_id": {"required": True, "type": "str"},
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
