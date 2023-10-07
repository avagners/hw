import json
import requests
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning


class GitlabSession:

    def __init__(self, host, access_token):
        self.access_token = access_token
        self.url = f'{host}/api/v4'
        self.group_id = 1045
        # Отключение предупреждений
        disable_warnings(InsecureRequestWarning)

    def _api_get(self, endpoint: str, params={}):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(endpoint, headers=headers,
                                params=params, verify=False)
        response.raise_for_status()
        return response.json()

    def get_projects(self, group_id: int) -> list:
        group_endpoint = f'{self.url}/groups/{group_id}'
        projects_endpoint = group_endpoint + '/projects'
        # получаем данные о проектах в группе
        response = self._api_get(projects_endpoint)
        projects = []
        projects.extend(response)
        # рекурсивно проходим по сабгруппам и получаем данные о проектах
        endpoint = group_endpoint + "/subgroups"
        response = self._api_get(endpoint)

        for subgroup in response:
            subgroup_id = subgroup['id']
            projects.extend(self.get_projects(subgroup_id))
        return projects

    def get_commits(self, project_id: int, start_date: str, end_date: str) -> list:
        endpoint = f'{self.url}/projects/{project_id}/repository/commits'
        all_commits = []
        num_page = 1
        while True:
            params = {'since': start_date, "until": end_date,
                      "per_page": 100, "page": num_page}
            response = self._api_get(endpoint, params)
            if not response:
                break
            all_commits += response
            num_page += 1
        return all_commits

    def parse_data(self, commits: list, project: dict) -> list:
        data = []
        for commit in commits:
            commit_id = commit['id']
            endpoint = f'{self.url}/projects/{project["id"]}/repository/commits/{commit_id}/diff'
            response = self._api_get(endpoint)
            data_commit = {
                "project_id": project['id'],
                "project_name": project['name'],
                "short_id": commit['short_id'],
                "created_at": commit['created_at'],
                "author_name": commit['author_name'],
                "author_email": commit['author_email'],
                "committer_name": commit['committer_name'],
                "committer_email": commit['committer_email'],
                "diffs": json.dumps(response)
            }
            data.append(data_commit)
        return data

    def get_data(self, start_date: str, end_date: str):
        projects = self.get_projects(self.group_id)
        data = []
        for i, project in enumerate(projects):
            print(i, project['id'], '-', project['name'])
            commits = self.get_commits(project['id'], start_date, end_date)
            data_project = self.parse_data(commits, project)
            if not data_project:
                continue
            print("Получено коммитов:", len(data_project))
            data += data_project
        return data
