"""
Subpackage for the integrated homework services

Each service must consist of the following:

- a template `services/menu/{service_name}.html` - will be included in the service menu page

- a javascript file `static/services/main_page/{service_name}.js`

  - function to render data of a homework saved by the given service, must be then
    added to `service_task_renderers` dictionary with the service name as key

  - anything else used on the main page with the list of tasks

- a javascript file `static/services/menu/{service_name}.js`, containing anything needed
  to support the service menu html

- a css file `static/services/css/{service_name}.css` for the menu page

- a python module `homework_fml.services.{service_name}` (`.py` file in this folder),
  containing the following:

  - function `import_data`, which takes `user_id` as an argument, to import any new tasks
    for the given user, must return created task objects (but not add them to db)

  - optionally a blueprint named `bp`, if the service needs endpoints for e.g. the
    OAuth dance

All data a service needs about a user (auth tokens etc.) should be saved in
`User.services_data[{service_name}]`. Data under the key `_frontend` is available on
the menu page

All the tasks are stored in the tasks table, and have some required values (see the file
db.py; one of them is `service_name`, which must be exactly `{service_name}`), anything
additional shall be stored in the `data` JSON.
"""
