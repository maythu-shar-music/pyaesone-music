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
    
    try:
        # ပြင်ဆင်ချက်: Current directory ကို အတိအကျပေးပါ
        repo = Repo(os.getcwd())
        LOGGER(__name__).info(f"Git Client Found [VPS DEPLOYER]")
        
        # Check if origin exists
        if "origin" in repo.remotes:
            origin = repo.remote("origin")
            # Update origin URL if needed
            try:
                if origin.url != UPSTREAM_REPO:
                    origin.set_url(UPSTREAM_REPO)
            except:
                pass
        else:
            origin = repo.create_remote("origin", UPSTREAM_REPO)
        
        # Fetch updates
        try:
            origin.fetch()
            LOGGER(__name__).info("Successfully fetched updates")
        except GitCommandError as e:
            LOGGER(__name__).warning(f"Could not fetch: {e}")
        
    except InvalidGitRepositoryError:
        LOGGER(__name__).info(f"Initializing new git repository...")
        repo = Repo.init(os.getcwd())
        
        if "origin" in repo.remotes:
            origin = repo.remote("origin")
            origin.set_url(UPSTREAM_REPO)
        else:
            origin = repo.create_remote("origin", UPSTREAM_REPO)
        
        try:
            origin.fetch()
        except GitCommandError as e:
            LOGGER(__name__).error(f"Failed to fetch: {e}")
            # If fetch fails, try to set up tracking branch differently
            return
        
        # Set up tracking branch
        try:
            repo.create_head(
                config.UPSTREAM_BRANCH,
                origin.refs[config.UPSTREAM_BRANCH],
            )
            repo.heads[config.UPSTREAM_BRANCH].set_tracking_branch(
                origin.refs[config.UPSTREAM_BRANCH]
            )
            repo.heads[config.UPSTREAM_BRANCH].checkout(True)
        except Exception as e:
            LOGGER(__name__).error(f"Failed to set up branch: {e}")
            return
        
        # Pull updates
        try:
            origin.pull(config.UPSTREAM_BRANCH)
        except GitCommandError:
            try:
                repo.git.reset("--hard", "FETCH_HEAD")
            except:
                LOGGER(__name__).error("Failed to reset to FETCH_HEAD")
        
        # Install requirements
        try:
            install_req("pip3 install --no-cache-dir -r requirements.txt")
        except Exception as e:
            LOGGER(__name__).error(f"Failed to install requirements: {e}")
        
        LOGGER(__name__).info(f"Fetching updates from upstream repository...")
    
    except GitCommandError as e:
        LOGGER(__name__).info(f"Git Command Error: {e}")
    except Exception as e:
        LOGGER(__name__).error(f"Unexpected error: {e}")
