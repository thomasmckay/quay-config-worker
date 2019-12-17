import logging

from data import model

from decorators import task_resources

logger = logging.getLogger(__name__)


@task_resources
def process(resources):
    response = []
    changed = True

    for resource in resources:
        p_state = resource["state"]
        p_name = resource["name"]
        p_user = resource["user"]
        p_organization = resource["organization"]
        p_role = resource["role"]
        p_description = resource["description"]

        user = model.user.get_user(p_user)
        if user is None:
            return {"failed": True, "msg": "User '%s' does not exist" % (p_user)}, 400

        try:
            organization = model.organization.get_organization(p_organization)
        except model.InvalidOrganizationException:
            return (
                {
                    "failed": True,
                    "msg": "Organization '%s' does not exist" % (p_organization),
                },
                400,
            )

        try:
            team = model.team.get_organization_team(p_organization, p_name)
        except model.InvalidTeamException:
            team = None
        if p_state == "absent":
            if team is not None:
                model.team.remove_team(p_organization, p_name, p_user)
                response.append("Team '%s' deleted" % p_name)
                changed = True
            else:
                response.append("Team '%s' does not exist" % p_name)
        else:
            if team is None:
                changed = True
                team = model.team.create_team(
                    p_name, organization, p_role, p_description
                )
                response.append("Team '%s' created" % p_name)
            else:
                response.append("Team '%s' exists" % p_name)

            role = model.team.get_team_org_role(team)
            if role.name != p_role:
                changed = True
                team = model.team.set_team_org_permission(team, p_role, user.username)
                response.append("Team '%s' Role updated" % p_name)

    return {"failed": False, "changed": changed, "meta": response}, 200
