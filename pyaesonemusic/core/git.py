import asyncio
import os
import shlex
from typing import Tuple
from pathlib import Path

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

import config

from ..logging import LOGGER


def install_req(cmd: str) -> Tuple[str, str, int, int]:
    async def install_requirements():
        args = shlex.split(cmd)
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return (
            stdout.decode("utf-8", "replace").strip(),
            stderr.decode("utf-8", "replace").strip(),
            process.returncode,
            process.pid,
        )

    return asyncio.get_event_loop().run_until_complete(install_requirements())


def git():
    """Git operations for updating the application"""
    
    # Skip git operations if running in Docker without .git directory
    app_path = Path('/app')
    git_dir = app_path / '.git'
    
    # Check if .git directory exists
    if not git_dir.exists():
        LOGGER(__name__).info("No .git directory found. Running in container mode.")
        
        # In container mode, we should check if we need to install requirements
        # without doing git operations
        requirements_file = app_path / 'requirements.txt'
        if requirements_file.exists():
            LOGGER(__name__).info("Installing requirements from existing requirements.txt")
            install_req("pip3 install --no-cache-dir --upgrade -r requirements.txt")
        return
    
    # Proceed with git operations only if .git exists
    try:
        # Get upstream repo URL with token if available
        REPO_LINK = config.UPSTREAM_REPO
        if config.GIT_TOKEN:
            GIT_USERNAME = REPO_LINK.split("com/")[1].split("/")[0]
            TEMP_REPO = REPO_LINK.split("https://")[1]
            UPSTREAM_REPO = f"https://{GIT_USERNAME}:{config.GIT_TOKEN}@{TEMP_REPO}"
        else:
            UPSTREAM_REPO = config.UPSTREAM_REPO
        
        LOGGER(__name__).info(f"Attempting git operations with repo: {REPO_LINK}")
        
        # Try to initialize repo in current directory
        try:
            repo = Repo(str(app_path))
            LOGGER(__name__).info(f"Git repository found at {app_path}")
        except (InvalidGitRepositoryError, GitCommandError):
            LOGGER(__name__).warning(f"Not a valid git repository at {app_path}")
            # If this is a fresh container, we might want to clone the repo
            # But for now, just skip git operations
            return
        
        # Check if we have origin remote
        if "origin" not in [remote.name for remote in repo.remotes]:
            LOGGER(__name__).info(f"Adding origin remote: {UPSTREAM_REPO}")
            origin = repo.create_remote("origin", UPSTREAM_REPO)
        else:
            origin = repo.remote("origin")
            # Update remote URL if it's different
            if origin.url != UPSTREAM_REPO:
                LOGGER(__name__).info(f"Updating origin URL to: {UPSTREAM_REPO}")
                origin.set_url(UPSTREAM_REPO)
        
        # Try to fetch updates
        try:
            LOGGER(__name__).info(f"Fetching updates from {UPSTREAM_REPO}")
            origin.fetch()
        except GitCommandError as fetch_error:
            LOGGER(__name__).error(f"Fetch failed: {fetch_error}")
            
            # Check for authentication errors
            error_msg = str(fetch_error).lower()
            if "authentication" in error_msg or "username" in error_msg or "token" in error_msg:
                LOGGER(__name__).warning("Authentication failed. Using local code only.")
                # Continue with local code without updates
                return
            
            # For other errors, try to continue
            LOGGER(__name__).warning("Continuing with existing code despite fetch error")
        
        # Checkout the specified branch
        try:
            # Check if branch exists locally
            if config.UPSTREAM_BRANCH in repo.heads:
                branch = repo.heads[config.UPSTREAM_BRANCH]
            else:
                # Create tracking branch
                LOGGER(__name__).info(f"Creating tracking branch for {config.UPSTREAM_BRANCH}")
                branch = repo.create_head(
                    config.UPSTREAM_BRANCH,
                    origin.refs[config.UPSTREAM_BRANCH],
                )
                branch.set_tracking_branch(origin.refs[config.UPSTREAM_BRANCH])
            
            # Checkout the branch
            branch.checkout()
            LOGGER(__name__).info(f"Checked out branch: {config.UPSTREAM_BRANCH}")
            
        except Exception as branch_error:
            LOGGER(__name__).error(f"Branch checkout failed: {branch_error}")
            # Try to checkout main/master as fallback
            for fallback_branch in ['main', 'master']:
                if fallback_branch in repo.heads:
                    repo.heads[fallback_branch].checkout()
                    LOGGER(__name__).info(f"Fell back to {fallback_branch} branch")
                    break
        
        # Try to pull updates
        try:
            LOGGER(__name__).info("Pulling latest changes...")
            origin.pull(config.UPSTREAM_BRANCH)
        except GitCommandError as pull_error:
            LOGGER(__name__).error(f"Pull failed: {pull_error}")
            # Try reset to fetched head
            try:
                repo.git.reset("--hard", "FETCH_HEAD")
                LOGGER(__name__).info("Reset to FETCH_HEAD")
            except Exception as reset_error:
                LOGGER(__name__).error(f"Reset failed: {reset_error}")
        
        # Install/update requirements
        requirements_path = app_path / 'requirements.txt'
        if requirements_path.exists():
            LOGGER(__name__).info("Installing/updating requirements...")
            install_req("pip3 install --no-cache-dir --upgrade -r requirements.txt")
        else:
            LOGGER(__name__).warning("requirements.txt not found")
        
        LOGGER(__name__).info("Git operations completed")
        
    except Exception as e:
        LOGGER(__name__).error(f"Git operations failed: {e}")
        # Don't crash the app if git fails
        LOGGER(__name__).info("Continuing with existing codebase")
