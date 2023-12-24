import os
from unittest.mock import patch, Mock

import git
from git.exc import InvalidGitRepositoryError
import pytest

from pond.metadata.git import git_repo_name, GitMetadataSource


@patch("git.Remote")
@patch("git.Repo")
def test_git_repo_name_with_origin(MockRepo, MockRemote):
    repo = MockRepo()
    origin = MockRemote()

    # with '.git' extension
    origin.url = 'git@gitserver.com:author/pond.git'
    repo.remote = Mock(return_value=origin)
    name = git_repo_name(repo)
    assert name == 'pond'

    # without '.git' extension
    origin.url = 'git@gitserver.com:author/pond'
    repo.remote = Mock(return_value=origin)
    name = git_repo_name(repo)
    assert name == 'pond'


@patch("git.Repo")
def test_git_repo_name_no_remote(MockRepo):
    repo = MockRepo()
    repo.remote = Mock(side_effect=KeyError)
    repo.working_tree_dir = '/blah/foo/pond'
    name = git_repo_name(repo)
    assert name == 'pond'


@patch("git.Remote")
@patch("git.Repo")
def test_explicit_repo(MockRepo, MockRemote):
    origin = MockRemote()
    origin.url = 'git@gitserver.com:author/pond.git'

    repo = MockRepo()
    repo.remote = Mock(return_value=origin)
    repo.remote = Mock(return_value=origin)
    repo.head.object.hexsha = 'bcd'
    repo.active_branch.name = 'fix'

    source = GitMetadataSource(git_repo=MockRepo())
    assert source.section_name() == 'git'

    metadata = source.collect()
    assert metadata['sha'] == 'bcd'
    assert metadata['name'] == 'pond'
    assert metadata['branch'] == 'fix'


def test_missing_git_repository_default(tmp_path):
    """ Raise exception if the repository does not exist. """
    # Passing path with no git repository
    with pytest.raises(InvalidGitRepositoryError):
        GitMetadataSource(git_repo=git.Repo(tmp_path))

    # Path is left to current directory
    old_path = os.getcwd()
    try:
        # Move to a place with no git repositories
        os.chdir(tmp_path)
        with pytest.raises(InvalidGitRepositoryError):
            GitMetadataSource(git_repo=None)
    finally:
        # Restore the old path
        os.chdir(old_path)
