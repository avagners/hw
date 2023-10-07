from abc import ABC, abstractmethod

import json
from typing import List
import requests
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning


class AbsGitlabSession(ABC):

    # Конструктор
    # постусловие: создан endpoint к API /api/v4
    def __init__(self, host: str, access_token: str) -> None: ...

    # Запросы:
    # Получены данные по проектам gitlab из группы group_id
    @abstractmethod
    def get_projects(self, group_id: int) -> list: ...

    # Получены все коммиты из project_id за период start_date и end_date
    @abstractmethod
    def get_commits(self, project_id: int,
                    start_date: str, end_date: str) -> List[dict]: ...


class Parser(ABC):

    # Запросы:
    # Парсинг коммитов проекта и получение набора данных
    @abstractmethod
    def parse_data(self, commits: list, project: dict) -> List[dict]: ...

    # Получение итогового набора данных по всем проектам
    @abstractmethod
    def get_data(self, group_id: int,
                 start_date: str, end_date: str) -> List[dict]: ...


class GitlabSession(AbsGitlabSession):

    def __init__(self, host, access_token):
        self.access_token = access_token
        self.url = f'{host}/api/v4'
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

    def get_commits(self, project_id: int,
                    start_date: str, end_date: str) -> list:
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


class ParserAuthorsCommits(GitlabSession, Parser):

    def parse_data(self, commits: list, project: dict) -> List[dict]:
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

    def get_data(self, group_id: int,
                 start_date: str, end_date: str) -> List[dict]:
        projects = self.get_projects(group_id)
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
