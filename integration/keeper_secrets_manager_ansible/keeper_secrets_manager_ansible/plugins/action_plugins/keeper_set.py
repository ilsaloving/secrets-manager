# -*- coding: utf-8 -*-
#  _  __
# | |/ /___ ___ _ __  ___ _ _ (R)
# | ' </ -_) -_) '_ \/ -_) '_|
# |_|\_\___\___| .__/\___|_|
#              |_|
#
# Keeper Secrets Manager
# Copyright 2021 Keeper Security Inc.
# Contact: ops@keepersecurity.com
#

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from keeper_secrets_manager_ansible import KeeperAnsible

DOCUMENTATION = r'''
---
module: keeper_set

short_description: Set value in an existing the record

version_added: "1.0.0"

description:
    - Allows updating a record in an existing record in the Keeper Vault
    - Currently cannot add files to the record.
author:
    - John Walstra
options:
  uid:
    description:
    - The UID of the Keeper Vault record.
    type: str
    required: no
  title:
    description:
    - The Title of the Keeper Vault record.
    type: str
    required: no
    version_added: '1.2.0'
  cache:
    description:
    - The cache registered by keeper_get_records_cache
    - Using keeper_set will not update the cache. Use the keeper_get_records_cache action again to get a new cache.
    type: str
    required: no
    version_added: '1.2.0'  
  field:
    description:
    - The label, or type, of the standard field in record that contains the value.
    - If the value has a complex value, use notation to get the specific value from the complex value.
    type: str
    required: no
  custom_field:
    description:
    - The label, or type, of the user added customer field in record that contains the value.
    - If the value has a complex value, use notation to get the specific value from the complex value.
    type: str
    required: no
  file:
    description:
    - The file name of the file that contains the value.
    type: str
    required: no
  value:
    description:
    - The Keeper notation to access record that contains the value.
    - Use notation when you want a specific value.
    - 
    - See https://docs.keeper.io/secrets-manager/secrets-manager/about/keeper-notation for more information/
    type: str
    required: no
    version_added: '1.0.1'  
'''

RETURN = r'''
updated:
  description: The record was updated.
  returned: success
  type: bool
  sample: True
  version_added: '1.0.1'  
'''


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        if task_vars is None:
            task_vars = {}

        keeper = KeeperAnsible(task_vars=task_vars, action_module=self)

        cache = self._task.args.get("cache")

        uid = self._task.args.get("uid")
        title = self._task.args.pop("title", None)
        if uid is None and title is None:
            raise AnsibleError("The uid and title are blank. keeper_set requires one to be set.")
        if uid is not None and title is not None:
            raise AnsibleError("The uid and title are both set. keeper_set requires one to be set, but not both.")

        # Try to get either the field, custom_field, or file name.
        field_type_enum, field_key = keeper.get_field_type_enum_and_key(args=self._task.args)

        value = self._task.args.get("value")

        try:
            keeper.set_value(uid=uid, title=title, field_type=field_type_enum, key=field_key, value=value, cache=cache)
        except Exception as err:
            raise AnsibleError("Cannot update record: {}".format(str(err)))

        return {
            "updated": True
        }
