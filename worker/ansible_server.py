import logging
import os
import sys

import trollius
from trollius.coroutines import From
import json
from threading import Event
from flask import Flask
from data import database
from autobahn.asyncio.wamp import RouterFactory, RouterSessionFactory
from autobahn.asyncio.websocket import WampWebSocketServerFactory
from aiowsgi import create_server as create_wsgi_server

from app import app

import routes.database
import routes.image
import routes.image_storage_location
import routes.login_service
import routes.organization
import routes.repository
import routes.role
import routes.service_key
import routes.skopeo
import routes.tag
import routes.team
import routes.team_role
import routes.user
import routes.visibility
import routes.work_queue


logger = logging.getLogger(__name__)

WORK_CHECK_TIMEOUT = int(os.environ.get("WORK_CHECK_TIMEOUT", 10))

class AnsibleServerStatus(object):
    STARTING = 'starting'
    RUNNING = 'running'
    SHUTDOWN = 'shutting_down'
    EXCEPTION = 'exception'


class AnsibleServer(object):
  def __init__(self, registry_hostname, queue):
    if os.environ.get('DEBUG_PYDEV', 'false') == 'true':
      import pydevd
      pydevd.settrace('192.168.123.1', port=23456, stdoutToServer=True, stderrToServer=True, suspend=False)
    self._current_status = AnsibleServerStatus.STARTING
    self._queue = queue

    self._session_factory = RouterSessionFactory(RouterFactory())

    self._shutdown_event = Event()
    self._current_status = AnsibleServerStatus.RUNNING

    self._register_controller()

  def _register_controller(self):
    controller_app = Flask('controller')
    server = self

    @controller_app.route('/status')
    def status():
      data = {
          'status': server._current_status
      }
      return json.dumps(data)

    @controller_app.route('/database', methods=['POST'])
    def database():
        response, status = routes.database.process()
        return json.dumps(response), status

    @controller_app.route('/image', methods=['POST'])
    def image():
        response, status = routes.image.process()
        return json.dumps(response), status

    @controller_app.route('/image_storage_location', methods=['POST'])
    def image_storage_location():
        response, status = routes.image_storage_location.process()
        return json.dumps(response), status

    @controller_app.route('/login_service', methods=['POST'])
    def login_service():
        response, status = routes.login_service.process()
        return json.dumps(response), status

    @controller_app.route('/organization', methods=['POST'])
    def organization():
        response, status = routes.organization.process()
        return json.dumps(response), status

    @controller_app.route('/repository', methods=['POST'])
    def repository():
        response, status = routes.repository.process()
        return json.dumps(response), status

    @controller_app.route('/role', methods=['POST'])
    def role():
        response, status = routes.role.process()
        return json.dumps(response), status

    @controller_app.route('/skopeo', methods=['POST'])
    def skopeo():
        response, status = routes.skopeo.process()
        return json.dumps(response), status

    @controller_app.route('/service_key', methods=['POST'])
    def service_key():
        response, status = routes.service_key.process()
        return json.dumps(response), status

    @controller_app.route('/team', methods=['POST'])
    def team():
        response, status = routes.team.process()
        return json.dumps(response), status

    @controller_app.route('/tag', methods=['POST'])
    def tag():
        response, status = routes.tag.process()
        return json.dumps(response), status

    @controller_app.route('/team_role', methods=['POST'])
    def team_role():
        response, status = routes.team_role.process()
        return json.dumps(response), status

    @controller_app.route('/user', methods=['POST'])
    def user():
        response, status = routes.user.process()
        return json.dumps(response), status

    @controller_app.route('/visibility', methods=['POST'])
    def visibility():
        response, status = routes.visibility.process()
        return json.dumps(response), status

    @controller_app.route('/work_queue', methods=['POST'])
    def work_queue():
        response, status = routes.work_queue.process()
        return json.dumps(response), status

    self._controller_app = controller_app

  def run(self, host, websocket_port, controller_port, ssl=None):
    logger.debug('Initializing all members of the event loop')
    loop = trollius.get_event_loop()

    logger.debug('Starting server on port %s, with controller on port %s', websocket_port,
                 controller_port)

    try:
      loop.run_until_complete(self._initialize(loop, host, websocket_port, controller_port, ssl))
    except KeyboardInterrupt:
      pass
    finally:
      loop.close()

  def close(self):
    logger.debug('Requested server shutdown')
    self._current_status = BuildServerStatus.SHUTDOWN
    self._shutdown_event.wait()
    logger.debug('Shutting down server')


  @trollius.coroutine
  def _work_checker(self):
    while self._current_status == AnsibleServerStatus.RUNNING:
      with database.CloseForLongOperation(app.config):
        yield From(trollius.sleep(WORK_CHECK_TIMEOUT))

      processing_time = 30  # seconds
      job_item = None
      try:
        job_item = self._queue.get(processing_time=processing_time, ordering_required=True)
      except Exception as ex:  # Case when database is uninitialized get a "programming error" in peewee
        logger.debug('Likely database not initialized')
        continue

      if job_item is None:
        logger.debug('No additional work found. Going to sleep for %s seconds', WORK_CHECK_TIMEOUT)
        continue

      logger.debug('Processing: %s', job_item)
      resource = json.loads(job_item.body)
      resource['work_queue'] = False
      result, status = getattr(sys.modules['routes.' + resource['task']], "process_resources")([resource])
      if status == 200:
        logger.debug('Processing complete: %s', result)
        self._queue.complete(job_item)
      else:
        logger.debug('Processing incomplete: %s', result)
        self._queue.incomplete(job_item, retry_after=WORK_CHECK_TIMEOUT)
      continue

  @trollius.coroutine
  def _initialize(self, loop, host, websocket_port, controller_port, ssl=None):
    self._loop = loop

    # Create the WAMP server.
    transport_factory = WampWebSocketServerFactory(self._session_factory, debug_wamp=False)
    transport_factory.setProtocolOptions(failByDrop=True)

    # Initialize the controller server and the WAMP server
    create_wsgi_server(self._controller_app, loop=loop, host=host, port=controller_port, ssl=ssl)
    yield From(loop.create_server(transport_factory, host, websocket_port, ssl=ssl))

    # Initialize the work queue checker.
    yield From(self._work_checker())
