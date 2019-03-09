import logging

from data.database import (db, all_models)
from data import runmigration
from app import app
from decorators import task_resources

logger = logging.getLogger(__name__)

@task_resources
def process(resources):
  response = []
  changed = True
  expected_tables = ["accesstoken",
                     "accesstokenkind",
                     "alembic_version",
                     "apprblob",
                     "apprblobplacement",
                     "apprblobplacementlocation",
                     "apprmanifest",
                     "apprmanifestblob",
                     "apprmanifestlist",
                     "apprmanifestlistmanifest",
                     "apprtag",
                     "apprtagkind",
                     "appspecificauthtoken",
                     "blobupload",
                     "buildtriggerservice",
                     "deletednamespace",
                     "derivedstorageforimage",
                     "disablereason",
                     "emailconfirmation",
                     "externalnotificationevent",
                     "externalnotificationmethod",
                     "federatedlogin",
                     "image",
                     "imagestorage",
                     "imagestoragelocation",
                     "imagestorageplacement",
                     "imagestoragesignature",
                     "imagestoragesignaturekind",
                     "imagestoragetransformation",
                     "label",
                     "labelsourcetype",
                     "logentry",
                     "logentry2",
                     "logentrykind",
                     "loginservice",
                     "manifest",
                     "manifestblob",
                     "manifestchild",
                     "manifestlabel",
                     "manifestlegacyimage",
                     "mediatype",
                     "messages",
                     "namespacegeorestriction",
                     "notification",
                     "notificationkind",
                     "oauthaccesstoken",
                     "oauthapplication",
                     "oauthauthorizationcode",
                     "permissionprototype",
                     "quayregion",
                     "quayrelease",
                     "quayservice",
                     "queueitem",
                     "repository",
                     "repositoryactioncount",
                     "repositoryauthorizedemail",
                     "repositorybuild",
                     "repositorybuildtrigger",
                     "repositorykind",
                     "repositorynotification",
                     "repositorypermission",
                     "repositorysearchscore",
                     "repositorytag",
                     "robotaccountmetadata",
                     "role",
                     "servicekey",
                     "servicekeyapproval",
                     "star",
                     "tag",
                     "tagkind",
                     "tagmanifest",
                     "tagmanifestlabel",
                     "tagmanifestlabelmap",
                     "tagmanifesttomanifest",
                     "tagtorepositorytag",
                     "team",
                     "teammember",
                     "teammemberinvite",
                     "teamrole",
                     "teamsync",
                     "torrentinfo",
                     "user",
                     "userprompt",
                     "userpromptkind",
                     "userregion",
                     "visibility"]

  for resource in resources:
    p_state = resource['state']

    if p_state == 'reset':
      db.drop_tables(all_models)

      try:
        db_uri = app.config['DB_URI']
        runmigration.run_alembic_migration(db_uri, logger, setup_app=False)
      except Exception as ex:
        return {
          "failed": True,
          "msg": "Database migrations failed: %s" % ex
         }, 400
      changed = True

    # Always run 'present' state to confirm 'reset'
    tables = db.get_tables()
    if tables != expected_tables:
      extra_tables = list(set(expected_tables) - set(tables))
      missing_tables = list(set(tables) - set(expected_tables))
      return {
        "failed": True,
        "msg": "Database exists but has mismatched tables\nMissing tables: %s\nExtra tables: %s" % (extra_tables, missing_tables)
      }, 400

  return {
    "failed": False,
    "changed": changed,
    "meta": response
  }, 200
