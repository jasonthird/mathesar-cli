# Mathesar RPC Methods

This list was discovered from `http://localhost` with:

```sh
mathesar methods list
```

Use any method with:

```sh
mathesar call METHOD.NAME --params-json '{}'
mathesar call METHOD NAME -p key=value
```

## Methods

- `analytics.disable`
- `analytics.get_state`
- `analytics.initialize`
- `analytics.upload_feedback`
- `analytics.view_report`
- `collaborators.add`
- `collaborators.delete`
- `collaborators.list`
- `collaborators.set_role`
- `columns.add`
- `columns.add_primary_key_column`
- `columns.delete`
- `columns.list`
- `columns.list_with_metadata`
- `columns.metadata.list`
- `columns.metadata.set`
- `columns.patch`
- `columns.reset_mash`
- `constraints.add`
- `constraints.delete`
- `constraints.list`
- `data_modeling.add_foreign_key_column`
- `data_modeling.add_mapping_table`
- `data_modeling.change_primary_key_column`
- `data_modeling.move_columns`
- `data_modeling.split_table`
- `data_modeling.suggest_types`
- `databases.configured.disconnect`
- `databases.configured.list`
- `databases.configured.patch`
- `databases.delete`
- `databases.get`
- `databases.privileges.list_direct`
- `databases.privileges.replace_for_roles`
- `databases.privileges.transfer_ownership`
- `databases.setup.connect_existing`
- `databases.setup.create_new`
- `databases.upgrade_sql`
- `explorations.add`
- `explorations.delete`
- `explorations.get`
- `explorations.list`
- `explorations.replace`
- `explorations.run`
- `forms.add`
- `forms.delete`
- `forms.get`
- `forms.get_source_info`
- `forms.list`
- `forms.list_related_records`
- `forms.patch`
- `forms.regenerate_token`
- `forms.set_publish_public`
- `forms.submit`
- `records.add`
- `records.delete`
- `records.get`
- `records.list`
- `records.list_summaries`
- `records.patch`
- `records.search`
- `roles.add`
- `roles.configured.add`
- `roles.configured.delete`
- `roles.configured.list`
- `roles.configured.set_password`
- `roles.delete`
- `roles.get_current_role`
- `roles.list`
- `roles.set_members`
- `schemas.add`
- `schemas.delete`
- `schemas.get`
- `schemas.list`
- `schemas.patch`
- `schemas.privileges.list_direct`
- `schemas.privileges.replace_for_roles`
- `schemas.privileges.transfer_ownership`
- `servers.configured.list`
- `servers.configured.patch`
- `system.listMethods`
- `system.methodHelp`
- `system.methodSignature`
- `tables.add`
- `tables.delete`
- `tables.get`
- `tables.get_import_preview`
- `tables.get_with_metadata`
- `tables.import`
- `tables.list`
- `tables.list_joinable`
- `tables.list_with_metadata`
- `tables.metadata.list`
- `tables.metadata.set`
- `tables.patch`
- `tables.privileges.list_direct`
- `tables.privileges.replace_for_roles`
- `tables.privileges.transfer_ownership`
- `users.add`
- `users.delete`
- `users.get`
- `users.list`
- `users.password.replace_own`
- `users.password.revoke`
- `users.patch_other`
- `users.patch_self`
