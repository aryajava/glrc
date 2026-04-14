"""
GitLab API operations untuk GLRC Application
"""
import logging
import requests
from typing import List, Dict, Optional

logger = logging.getLogger("glrc")


class GitLabAPI:
    """
    Class untuk handle semua operasi dengan GitLab API.
    """

    def __init__(self, gitlab_url: str, api_token: str):
        """
        Initialize GitLab API client.

        Args:
            gitlab_url: Base URL of GitLab instance
            api_token: Personal Access Token
        """
        self.gitlab_url = gitlab_url.rstrip('/')
        self.api_token = api_token
        self.headers = {"PRIVATE-TOKEN": self.api_token}

    def test_connection(self) -> tuple[bool, Optional[Dict]]:
        """
        Test koneksi ke GitLab API dan ambil informasi user.

        Returns:
            Tuple (success: bool, user_data: dict or None)
        """
        try:
            resp = requests.get(
                f"{self.gitlab_url}/api/v4/user",
                headers=self.headers,
                timeout=10
            )
            if resp.status_code == 200:
                return True, resp.json()
            else:
                return False, None
        except Exception as e:
            logger.warning("Connection test failed: %s", e)
            return False, None

    def fetch_all_projects(self) -> List[Dict]:
        """
        Mengambil semua projects dari GitLab instance (dengan pagination).

        Returns:
            List of project dictionaries
        """
        all_projects = []
        page = 1
        per_page = 100

        while True:
            try:
                resp = requests.get(
                    f"{self.gitlab_url}/api/v4/projects",
                    headers=self.headers,
                    params={
                        "membership": "true",
                        "per_page": per_page,
                        "page": page,
                        "archived": "false"
                    },
                    timeout=30
                )
                if resp.status_code != 200:
                    break

                projects = resp.json()
                if not projects:
                    break

                all_projects.extend(projects)

                # Check if there are more pages
                if len(projects) < per_page:
                    break

                page += 1

            except Exception as e:
                logger.warning("Error fetching projects: %s", e)
                break

        return all_projects

    def get_repository_branches(self, project_id: int) -> List[Dict]:
        """
        Mengambil daftar branches untuk repository tertentu.

        Args:
            project_id: GitLab project ID

        Returns:
            List of branch dictionaries
        """
        try:
            resp = requests.get(
                f"{self.gitlab_url}/api/v4/projects/{project_id}/repository/branches",
                headers=self.headers,
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                return []
        except Exception as e:
            logger.warning("Error fetching branches for project %s: %s", project_id, e)
            return []
