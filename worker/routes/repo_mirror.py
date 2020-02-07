from datetime import datetime
import logging
import json
import features
from flask import request

from data.database import (
    Repository,
    User,
    RepoMirrorRule,
    RepoMirrorConfig,
    RepoMirrorRuleType,
    RepoMirrorStatus,
    RepositoryState,
)
from data import model

from decorators import task_resources


logger = logging.getLogger(__name__)


@task_resources
def process(resources):
    response = []
    changed = False

    for resource in resources:
        p_state = resource["state"]

        p_user = resource["user"]
        p_external_user = resource["external_user"]
        p_external_password = resource["external_password"]
        p_external_reference = resource["external_reference"]
        p_external_tag = resource["external_tag"]
        p_internal_robot = resource["internal_robot"]
        p_internal_namespace = resource["internal_namespace"]
        p_internal_repository = resource["internal_repository"]
        p_sync_start_date = resource["sync_start_date"]
        p_sync_interval = resource["sync_interval"]
        p_is_enabled = resource["is_enabled"]

        if p_sync_start_date == "now":
            p_sync_start_date = datetime.now()
        else:
            p_sync_start_date = datetime.strptime(p_sync_start_date, "%Y-%m-%d %H:%M")

        user = model.user.get_user(p_user)
        if user is None:
            return {"failed": True, "msg": "User '%s' does not exist" % (p_user)}, 400

        name = "%s/%s" % (p_internal_namespace, p_internal_repository)
        repository = model.repository.get_repository(
            p_internal_namespace, p_internal_repository
        )
        if repository is None:
            return (
                {
                    "failed": True,
                    "msg": "Destination repository '%s/%s' does not exist"
                    % (p_internal_namespace, p_internal_repository),
                },
                400,
            )

        robot = model.user.lookup_robot(p_internal_robot)
        if robot is None:
            return (
                {
                    "failed": True,
                    "msg": "Robot '%s' does not exist" % (p_internal_robot),
                },
                400,
            )

        # TODO: Move this to repository
        repository.state = RepositoryState.MIRROR
        repository.save()

        if p_state == "present":
            try:
                rule = RepoMirrorRule.get(repository=repository)
            except RepoMirrorRule.DoesNotExist:
                rule = None
            try:
                config = RepoMirrorConfig.get(repository=repository)
            except RepoMirrorConfig.DoesNotExist:
                config = None

            if rule is None or config is None:
                changed = True

                rule = RepoMirrorRule.create(
                    repository=repository,
                    rule_type=RepoMirrorRuleType.TAG_GLOB_CSV,
                    rule_value=p_external_tag,
                )
                config = RepoMirrorConfig.create(
                    repository=repository,
                    root_rule=rule,
                    internal_robot=robot,
                    external_reference=p_external_reference,
                    external_registry_username=p_external_user,
                    external_registry_password=p_external_password,
                    external_registry_config={},
                    sync_start_date=p_sync_start_date,
                    sync_interval=30,
                    sync_retries_remaining=3,
                    sync_status=RepoMirrorStatus.NEVER_RUN,
                    is_enabled=p_is_enabled,
                )
                response.append("Repository mirror '%s' created" % name)
            else:
                rule_changed = False
                config_changed = False

                if rule.rule_value != p_external_tag:
                    rule_changed = True
                    rule.rule_value = p_external_tag
                    response.append(
                        "Repository mirror '%s' source tag updated to '%s'"
                        % (name, p_external_tag)
                    )

                if config.internal_robot != robot:
                    config_changed = True
                    config.internal_robot = robot
                    response.append(
                        "Repository mirror '%s' robot updated to '%s'"
                        % (name, p_internal_robot)
                    )

                if config.external_reference != p_external_reference:
                    config_changed = True
                    config.external_reference = p_external_reference
                    response.append(
                        "Repository mirror '%s' source registry reference updated to '%s'"
                        % (name, p_external_reference)
                    )
                if config.external_namespace != p_external_namespace:
                    config_changed = True
                    config.external_namespace = p_external_namespace
                    response.append(
                        "Repository mirror '%s' source namespace updated to '%s'"
                        % (name, p_external_namespace)
                    )
                if config.external_repository != p_external_repository:
                    config_changed = True
                    config.external_repository = p_external_repository
                    response.append(
                        "Repository mirror '%s' source repository updated to '%s'"
                        % (name, p_external_repository)
                    )
                if config.external_registry_username != p_external_user:
                    config_changed = True
                    config.external_registry_username = p_external_user
                    response.append(
                        "Repository mirror '%s' source username updated to '%s'"
                        % (name, p_external_user)
                    )
                if config.external_registry_password != p_external_password:
                    config_changed = True
                    config.external_registry_password = p_external_password
                    response.append(
                        "Repository mirror '%s' source password updated" % (name)
                    )
                if p_sync_start_date:
                    if config.sync_start_date != p_sync_start_date:
                        config_changed = True
                        config.sync_start_date = p_sync_start_date
                    response.append(
                        "Repository mirror '%s' sync start date updated" % (name)
                    )
                if config.is_enabled != p_is_enabled:
                    config_changed = True
                    config.is_enabled = p_is_enabled
                    response.append(
                        "Repository mirror '%s' enabled flag updated" % (name)
                    )

                config.sync_status = RepoMirrorStatus.NEVER_RUN
                config.sync_interval = p_sync_interval
                config.external_registry_config = {}
                config_changed = True

                if rule_changed:
                    rule.save()
                    changed = True
                if config_changed:
                    config.save()
                    changed = True

    return {"failed": False, "changed": changed, "meta": response}, 200
