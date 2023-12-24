import os
from typing import Optional

import git

from pond.metadata.metadata_source import MetadataSource


def git_repo_name(repo):
    """ Try to infer the name of a git repository.

    Use the "origin" remote repository if defined, or else the name of the local working
    directory.
    """
    try:
        origin = repo.remote('origin')
        name = os.path.splitext(os.path.basename(origin.url))[0]
    except Exception:
        workdir = repo.working_tree_dir
        name = os.path.splitext(os.path.basename(workdir))[0]
    return name


class GitMetadataSource(MetadataSource):

    def __init__(self, git_repo: Optional[git.Repo] = None):
        """ Metadata about a git repository.

        The section name for this source is "git".

        The collected metadata is the current SHA in the repository.

        Parameters
        ----------
        git_repo: git.Repo
            Object representing the git repository. If None, an Repo object is created searching
            for a git repository in a parent directory.

        Raises
        ------
        InvalidGitRepositoryError
            If no git repository is found
        """
        if git_repo is None:
            git_repo = git.Repo(search_parent_directories=True)
        self.repo = git_repo

    def section_name(self):
        return 'git'

    def collect(self):
        sha = self.repo.head.object.hexsha
        name = git_repo_name(self.repo)
        active_branch_name = self.repo.active_branch.name
        metadata = {
            'sha': sha,
            'name': name,
            'branch': active_branch_name
        }
        return metadata
