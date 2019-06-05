import app as app

from data.queue import WorkQueue

ansible_queue = WorkQueue('ansible', app.tf, has_namespace=False, metric_queue=app.metric_queue)

