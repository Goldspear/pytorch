#!/usr/bin/env python3

from typing import Any
from gitutils import (
    get_git_remote_name,
    get_git_repo_dir,
    GitRepo,
)
from trymerge import (
    gh_post_pr_comment,
    GitHubPR,
)
from check_labels_utils import (
    LABEL_ERR_MSG,
    has_required_labels,
    is_label_err_comment,
    delete_all_label_err_comments,
)

def parse_args() -> Any:
    from argparse import ArgumentParser
    parser = ArgumentParser("Check PR labels")
    parser.add_argument("pr_num", type=int)

    return parser.parse_args()

def add_label_err_comment(pr: GitHubPR) -> None:
    # Only make a comment if one doesn't exist already
    if not any(is_label_err_comment(comment) for comment in pr.get_comments()):
        gh_post_pr_comment(pr.org, pr.project, pr.pr_num, LABEL_ERR_MSG)

def main() -> None:
    args = parse_args()
    repo = GitRepo(get_git_repo_dir(), get_git_remote_name())
    org, project = repo.gh_owner_and_name()
    pr = GitHubPR(org, project, args.pr_num)

    try:
        if not has_required_labels(pr.get_labels(), pr.org, pr.project):
            print(LABEL_ERR_MSG)
            add_label_err_comment(pr)
        else:
            delete_all_label_err_comments(pr.get_comments(), pr.org, pr.project)
    except Exception as e:
        pass


if __name__ == "__main__":
    main()
