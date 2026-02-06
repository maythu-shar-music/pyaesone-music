import asyncio
import shlex
import os
from typing import Tuple

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
    REPO_LINK = config.UPSTREAM_REPO
    if config.GIT_TOKEN:
        GIT_USERNAME = REPO_LINK.split("com/")[1].split("/")[0]
        TEMP_REPO = REPO_LINK.split("https://")[1]
        UPSTREAM_REPO = f"https://{GIT_USERNAME}:{config.GIT_TOKEN}@{TEMP_REPO}"
    else:
        UPSTREAM_REPO = config.UPSTREAM_REPO
    
    current_dir = os.getcwd()
    LOGGER(__name__).info(f"Current directory: {current_dir}")
    
    try:
        # Check if current directory is a git repo
        repo = Repo(current_dir)
        LOGGER(__name__).info(f"Git Client Found [VPS DEPLOYER]")
        
        # Check if origin exists
        if "origin" not in repo.remotes:
            LOGGER(__name__).info("Creating origin remote...")
            origin = repo.create_remote("origin", UPSTREAM_REPO)
        else:
            origin = repo.remote("origin")
            # Update origin URL if needed
            origin.set_url(UPSTREAM_REPO)
        
        # Try to fetch updates
        try:
            origin.fetch()
            LOGGER(__name__).info("Successfully fetched from origin")
        except GitCommandError as fetch_error:
            LOGGER(__name__).error(f"Fetch error: {fetch_error}")
            # Handle fetch errors gracefully
        
    except InvalidGitRepositoryError:
        LOGGER(__name__).info(f"Current directory is not a git repository. Initializing...")
        
        try:
            # Clone the repository instead of init
            LOGGER(__name__).info(f"Cloning repository from {UPSTREAM_REPO}")
            
            # First check if we should clone or init
            if os.listdir(current_dir):
                # Directory is not empty, we need to handle this carefully
                LOGGER(__name__).warning(f"Directory {current_dir} is not empty")
                
                # Try to init and setup remote
                repo = Repo.init(current_dir)
                
                if "origin" not in repo.remotes:
                    origin = repo.create_remote("origin", UPSTREAM_REPO)
                else:
                    origin = repo.remote("origin")
                    origin.set_url(UPSTREAM_REPO)
                
                # Try to fetch and pull
                try:
                    origin.fetch()
                    # Try to checkout if branch exists
                    if config.UPSTREAM_BRANCH in origin.refs:
                        repo.create_head(
                            config.UPSTREAM_BRANCH,
                            origin.refs[config.UPSTREAM_BRANCH],
                        )
                        repo.heads[config.UPSTREAM_BRANCH].set_tracking_branch(
                            origin.refs[config.UPSTREAM_BRANCH]
                        )
                        repo.heads[config.UPSTREAM_BRANCH].checkout(True)
                except GitCommandError as e:
                    LOGGER(__name__).error(f"Error during git operations: {e}")
                    
            else:
                # Directory is empty, we can clone
                Repo.clone_from(UPSTREAM_REPO, current_dir, branch=config.UPSTREAM_BRANCH)
                repo = Repo(current_dir)
                LOGGER(__name__).info(f"Successfully cloned repository")
                
        except Exception as e:
            LOGGER(__name__).error(f"Error initializing git repository: {e}")
            return
    
    except GitCommandError as e:
        LOGGER(__name__).error(f"Git Command Error: {e}")
        return
    
    # Install requirements if needed
    try:
        requirements_file = os.path.join(current_dir, "requirements.txt")
        if os.path.exists(requirements_file):
            LOGGER(__name__).info("Installing requirements...")
            install_req("pip3 install --no-cache-dir -r requirements.txt")
        else:
            LOGGER(__name__).warning("requirements.txt not found")
    except Exception as e:
        LOGGER(__name__).error(f"Error installing requirements: {e}")
