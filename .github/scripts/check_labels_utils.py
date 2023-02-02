
import re
from typing import List, Pattern
from gitutils import (
    GitHubComment,
    gh_get_labels,
    gh_post_delete_comment
)


BOT_AUTHORS = ["github-actions", "pytorchmergebot", "pytorch-bot"]

CIFLOW_LABEL = re.compile(r"^ciflow/.+")
CIFLOW_TRUNK_LABEL = re.compile(r"^ciflow/trunk")

LABEL_ERR_MSG_TITLE = "This PR needs a label"
LABEL_ERR_MSG = f"""# {LABEL_ERR_MSG_TITLE}\n
    If your changes are user facing and intended to be a part of release notes, please use a label starting with `release notes:`.


    If not, please add the `topic: not user facing` label.
    For more information, see
    https://github.com/pytorch/pytorch/wiki/PyTorch-AutoLabel-Bot#why-categorize-for-release-notes-and-how-does-it-work.
"""


def has_label(labels: List[str], pattern: Pattern[str] = CIFLOW_LABEL) -> bool:
    return len(list(filter(pattern.match, labels))) > 0


def get_release_notes_labels(org: str, repo: str) -> List[str]:
    return [label for label in gh_get_labels(org, repo) if label.lstrip().startswith("release notes:")]


def has_required_labels(pr_labels: List[str], org: str, repo: str) -> bool:
    # Check if PR is not user facing
    is_not_user_facing_pr = any(label.strip() == "topic: not user facing" for label in pr_labels)
    return (
        is_not_user_facing_pr or
        any(label.strip() in get_release_notes_labels(org, repo) for label in pr_labels)
    )


def is_label_err_comment(comment: GitHubComment) -> bool:
    return comment.body_text.lstrip(" #").startswith(LABEL_ERR_MSG_TITLE) and comment.author_login in BOT_AUTHORS


def delete_all_label_err_comments(comments: List[GitHubComment], org: str, project: str) -> None:
    for comment in comments:
        if is_label_err_comment(comment):
            gh_post_delete_comment(org, project, comment.database_id)
