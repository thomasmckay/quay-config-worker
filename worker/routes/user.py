import logging
from util.http import abort

from data.database import (Team, TeamMember, TeamRole, User)
from data import model

from decorators import task_resources

logger = logging.getLogger(__name__)

@task_resources
def process(resources):
  response = []
  changed = True

  for resource in resources:
    p_state = resource['state']
    p_username = resource['username']
    p_password = resource['password']
    p_email = resource['email']
    p_verified = resource['verified']

    user = model.user.get_user(p_username)
    if p_state == 'absent':
      if user is not None:
        user.delete_instance()
        response.append("User '%s' deleted" % p_username)
        changed = True
      else:
        response.append("User '%s' does not exist" % p_username)
      return {
        "failed": False,
        "changed": changed,
        "meta": response
      }, 200

    if user is None:
      changed = True
      user = model.user.create_user(p_username, p_password, p_email)
      response.append("User '%s' created" % p_username)
    else:
      response.append("User '%s' exists" % p_username)

    if user.email != p_email:
      changed = True
      user.email = p_email
      response.append("User '%s' email updated to '%s'" % (p_username, p_email))

    if user.verified != p_verified:
      changed = True
      user.verified = p_verified
      response.append("User '%s' verified updated to '%s'" % (p_username, p_verified))

    if changed:
      user.save()

    _user_teams(user, resource)

  return {
    "failed": False,
    "changed": changed,
    "meta": response
  }, 200

def _user_teams(user, resource):
    changed = False
    p_exact_teams = resource['exact_teams']
    p_add_teams = resource['add_teams']
    p_remove_teams = resource['remove_teams']

    team_names = (p_exact_teams or p_add_teams or p_remove_teams)
    if team_names is None:
      return False

    teams = []
    for name in team_names:
      try:
        teams.append(Team.get(Team.name == name))
      except model.InvalidTeamException:
        abort(400, message="Team '%s' does not exist" % name)
    teams = set(teams)

    current_teams = set(Team.select().join(TeamMember).join(User)).where(User.username == user.username)

    teams_to_add = teams - current_teams
    teams_to_remove = current_teams - teams
    if p_add_teams:
      teams_to_remove = []
    elif p_remove_teams:
      teams_to_add = []

    for team in teams_to_add:
      changed = True
      model.team.add_user_to_team(user, team)

    query = TeamMember.select().join(User).switch(TeamMember).join(Team).join(TeamRole)
    for team in teams_to_remove:
      changed = True
      found = list(query.where(User.username == user.username, Team.name == team.name))
      found[0].delete_instance()

    return changed
