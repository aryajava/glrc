"""
GitLab API operations untuk GLRC Application
"""
import logging
import requests
from typing import List, Dict, Optional

logger = logging.getLogger("glrc")


def _separator_variants(path: str) -> list:
    """
    Generate all unique separator-swap variants of a project path.

    For each path segment, replaces '_' with '-' and vice versa, producing
    all combinations. The original path itself is excluded (already tried).

    Example:
        "group/msf_maintain_user" →
            ["group/msf-maintain-user", "group/msf_maintain-user", "group/msf-maintain_user"]
    """
    import itertools

    segments = path.split("/")

    def segment_variants(seg: str) -> list:
        """All unique underscore/hyphen swap combos for one segment."""
        chars = list(seg)
        sep_indices = [i for i, c in enumerate(chars) if c in ("_", "-")]
        if not sep_indices:
            return [seg]
        variants = set()
        for mask in itertools.product([False, True], repeat=len(sep_indices)):
            new_chars = chars[:]
            for swap, idx in zip(mask, sep_indices):
                if swap:
                    new_chars[idx] = "-" if chars[idx] == "_" else "_"
            variants.add("".join(new_chars))
        return list(variants)

    all_segment_options = [segment_variants(seg) for seg in segments]
    seen = {path}
    results = []
    for combo in itertools.product(*all_segment_options):
        candidate = "/".join(combo)
        if candidate not in seen:
            seen.add(candidate)
            results.append(candidate)
    return results


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

    def get_user_ssh_keys(self) -> List[Dict]:
        """
        Mengambil daftar SSH keys milik user dari GitLab.

        Returns:
            List of SSH key dictionaries, or empty list on failure.
        """
        try:
            resp = requests.get(
                f"{self.gitlab_url}/api/v4/user/keys",
                headers=self.headers,
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                return []
        except Exception as e:
            logger.warning("Error fetching SSH keys: %s", e)
            return []

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

    def validate_projects(self, project_paths: set) -> tuple:
        """
        Memvalidasi sekumpulan project path dengan melakukan ping ke GitLab API.

        Step 1: Exact endpoint hit.
        Step 2: Search fallback (match by path/name/path_with_namespace).
        Step 3: Fuzzy retry — swap '_' ↔ '-' in each segment and repeat steps 1+2.

        Args:
            project_paths: Set of project paths (e.g. 'group/subgroup/project' or 'project_name')

        Returns:
            Tuple of (valid_projects, invalid_projects, corrected_pairs)
            where corrected_pairs is a list of (original_input, matched_path_with_namespace).
        """
        import urllib.parse
        valid_projects = []
        invalid_projects = []
        corrected_pairs = []   # list of (original_input, matched_path_with_namespace)

        def _try_exact(path: str):
            """Try the direct projects/{encoded} endpoint. Returns project dict or None."""
            try:
                encoded = urllib.parse.quote_plus(path)
                resp = requests.get(
                    f"{self.gitlab_url}/api/v4/projects/{encoded}",
                    headers=self.headers,
                    timeout=10
                )
                if resp.status_code == 200:
                    return resp.json()
            except Exception as e:
                logger.warning(f"Exact lookup error for {path}: {e}")
            return None

        def _try_search(path: str):
            """Try the search endpoint and match by path/name/path_with_namespace. Returns project dict or None."""
            try:
                search_resp = requests.get(
                    f"{self.gitlab_url}/api/v4/projects"
                    f"?search={urllib.parse.quote(path)}&simple=true",
                    headers=self.headers,
                    timeout=10
                )
                if search_resp.status_code == 200:
                    name_only = path.split("/")[-1]
                    for proj in search_resp.json():
                        if (
                            proj.get("path") == name_only
                            or proj.get("name") == name_only
                            or proj.get("path_with_namespace") == path
                        ):
                            return proj
            except Exception as e:
                logger.warning(f"Search lookup error for {path}: {e}")
            return None

        for path in project_paths:
            # --- Step 1: Exact hit ---
            proj = _try_exact(path)
            if proj:
                valid_projects.append(proj)
                continue

            # --- Step 2: Search fallback ---
            proj = _try_search(path)
            if proj:
                valid_projects.append(proj)
                continue

            # --- Step 3: Fuzzy separator swap retry (_↔-) ---
            found_via_fuzzy = False
            for variant in _separator_variants(path):
                proj = _try_exact(variant)
                if not proj:
                    proj = _try_search(variant)
                if proj:
                    valid_projects.append(proj)
                    corrected_pairs.append((path, proj.get("path_with_namespace", variant)))
                    found_via_fuzzy = True
                    break

            if not found_via_fuzzy:
                invalid_projects.append(path)

        return valid_projects, invalid_projects, corrected_pairs
