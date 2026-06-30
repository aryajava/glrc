"""
Git operations untuk GLRC Application
"""
import subprocess
import os
from typing import Optional
from urllib.parse import urlparse, quote


class GitOperations:
    """
    Class untuk handle semua operasi Git (clone, pull, checkout).
    """

    @staticmethod
    def clone_repository(
        repo_url: str,
        dest_folder: str,
        branch_name: str,
        api_token: str,
        clone_method: str = "HTTPS",
        log_callback=None,
        ssh_key_path: str = None
    ) -> bool:
        """
        Clone repository dari GitLab.

        Args:
            repo_url: URL repository
            dest_folder: Folder tujuan clone
            branch_name: Branch yang akan di-clone
            api_token: Personal Access Token
            clone_method: Method cloning ("HTTPS" atau "SSH")
            log_callback: Function untuk logging output
            ssh_key_path: Path ke custom SSH key

        Returns:
            Boolean indicating success
        """
        # Tentukan nama folder repo
        repo_folder_name = repo_url.rstrip("/").split("/")[-1]
        if repo_folder_name.endswith(".git"):
            repo_folder_name = repo_folder_name[:-4]
        repo_local_path = os.path.join(dest_folder, repo_folder_name)

        # Build authenticated URL
        parsed = urlparse(repo_url)
        if clone_method == "SSH":
            host = parsed.netloc
            path = parsed.path.lstrip('/')
            auth_url = f"git@{host}:{path}"
        else:
            auth_url = parsed._replace(
                netloc=f"oauth2:{quote(api_token)}@{parsed.netloc}"
            ).geturl()

        clone_command = ["git", "clone", "-b", branch_name, auth_url]

        # Setup creationflags for Windows to hide the terminal
        creationflags = 0
        if os.name == 'nt' or sys.platform == 'win32':
            creationflags = 0x08000000  # CREATE_NO_WINDOW

        env = os.environ.copy()
        if clone_method == "SSH" and ssh_key_path and os.path.exists(ssh_key_path):
            # Normalise path for git bash / Windows compat
            normalized_key_path = ssh_key_path.replace("\\", "/")
            env["GIT_SSH_COMMAND"] = f"ssh -i '{normalized_key_path}' -o IdentitiesOnly=yes"

        try:
            process = subprocess.Popen(
                clone_command,
                cwd=dest_folder,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=creationflags,
                env=env
            )

            for line in process.stdout:
                if log_callback:
                    log_callback(f"    {line.strip()}")

            process.wait()
            
            # Set custom SSH key config in local repo
            if process.returncode == 0 and clone_method == "SSH" and ssh_key_path and os.path.exists(ssh_key_path):
                normalized_key_path = ssh_key_path.replace("\\", "/")
                subprocess.run(
                    ["git", "config", "core.sshCommand", f"ssh -i '{normalized_key_path}' -o IdentitiesOnly=yes"],
                    cwd=repo_local_path,
                    creationflags=creationflags
                )

            return process.returncode == 0

        except Exception as e:
            if log_callback:
                log_callback(f"[-] Error during clone: {e}")
            return False

    @staticmethod
    def pull_repository(
        repo_local_path: str,
        branch_name: str,
        log_callback=None,
        ssh_key_path: str = None
    ) -> bool:
        """
        Pull latest changes dari repository yang sudah ada.

        Args:
            repo_local_path: Path ke repository lokal
            branch_name: Branch yang akan di-pull
            log_callback: Function untuk logging output
            ssh_key_path: Path ke custom SSH key

        Returns:
            Boolean indicating success
        """
        # Setup creationflags for Windows to hide the terminal
        creationflags = 0
        if os.name == 'nt' or sys.platform == 'win32':
            creationflags = 0x08000000  # CREATE_NO_WINDOW

        env = os.environ.copy()
        if ssh_key_path and os.path.exists(ssh_key_path):
            normalized_key_path = ssh_key_path.replace("\\", "/")
            env["GIT_SSH_COMMAND"] = f"ssh -i '{normalized_key_path}' -o IdentitiesOnly=yes"

        try:
            process = subprocess.Popen(
                ["git", "pull", "origin", branch_name],
                cwd=repo_local_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=creationflags,
                env=env
            )

            for line in process.stdout:
                if log_callback:
                    log_callback(f"    {line.strip()}")

            process.wait()
            return process.returncode == 0

        except Exception as e:
            if log_callback:
                log_callback(f"[-] Error during pull: {e}")
            return False

    @staticmethod
    def create_new_branch(
        repo_local_path: str,
        new_branch_name: str,
        log_callback=None
    ) -> bool:
        """
        Membuat branch baru di repository lokal.

        Args:
            repo_local_path: Path ke repository lokal
            new_branch_name: Nama branch baru
            log_callback: Function untuk logging output

        Returns:
            Boolean indicating success
        """
        # Setup creationflags for Windows to hide the terminal
        creationflags = 0
        if os.name == 'nt' or sys.platform == 'win32':
            creationflags = 0x08000000  # CREATE_NO_WINDOW

        try:
            # Checkout ke branch baru
            process = subprocess.Popen(
                ["git", "checkout", "-b", new_branch_name],
                cwd=repo_local_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=creationflags
            )

            output, _ = process.communicate()
            if log_callback:
                log_callback(f"    {output.strip()}")

            return process.returncode == 0

        except Exception as e:
            if log_callback:
                log_callback(f"[-] Error creating new branch: {e}")
            return False

    @staticmethod
    def is_git_repository(path: str) -> bool:
        """
        Check apakah path adalah git repository.

        Args:
            path: Path yang akan di-check

        Returns:
            Boolean indicating if path is a git repository
        """
        return os.path.isdir(path) and os.path.isdir(os.path.join(path, ".git"))
