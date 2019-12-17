import app as app

from data.queue import WorkQueue

ansible_queue = WorkQueue(
    "ansible", app.tf, has_namespace=False
)
