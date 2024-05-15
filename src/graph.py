import logging

import pydot

from gh_api_helper import GithubAPIHelper

OUTPUT_FILE_NAME = '../graph.dot'


def _get_merge_commit_and_branch_commits(logger: logging.Logger, gh_api_helper: GithubAPIHelper, branch_name: str):
    master_commits = {}
    url = f'{gh_api_helper.GH_REPO_BRANCH_COMMITS}?sha=master'

    def _append_master_commit(commit) -> None:
        nonlocal master_commits
        master_commits[commit['sha']] = commit

    gh_api_helper.read_pages_until_limit(url=url, process_page=_append_master_commit)

    url = f'{gh_api_helper.GH_REPO_BRANCH_COMMITS}?sha={branch_name}'
    branch_commits = {}

    def _append_commit(commit) -> None:
        nonlocal branch_commits
        branch_commits[commit['sha']] = commit

    gh_api_helper.read_pages_until_limit(url=url, process_page=_append_commit)
    branch_commits_list = list(branch_commits.values())
    branch_commits_list.reverse()

    # Finding the first merge commit, the one that has two parents by the commit date order
    merge_commit = None
    for commit in branch_commits_list:
        parents = commit['parents']

        if len(parents) == 2:
            if parents[0]['sha'] in master_commits:  # the first parent belongs to the branch that it was merged to,
                # and if the commit sha is in master commits, then it means it's  a merge to master
                merge_commit = commit
                break

    if merge_commit is None:
        logger.error(f"No merge commit found for branch {branch_name}")
        exit(1)

    logger.info(f'Merge commit found: {merge_commit["sha"]} for branch {branch_name}')
    return merge_commit, branch_commits


def create_branch_commits_graph(logger: logging.Logger, gh_api_helper: GithubAPIHelper) -> None:
    # Defining the graph to be directional
    graph = pydot.Dot(graph_type='digraph')

    '''
    I did this part not generic due to lack of time, I validated the branch appears in pull requests that were 
    merged into master, the idea was to find an existing branch that was merged into master, and then find the first 
    commit
    '''
    branch_name = 'update-core-beta'
    merge_commit, branch_commits = _get_merge_commit_and_branch_commits(logger, gh_api_helper, branch_name)

    # Building the graph
    logger.debug(f'Building the graph for branch: {branch_name}')
    child = pydot.Node(merge_commit['sha'], label=f'{merge_commit["sha"]}\nmaster')
    graph.add_node(child)  # the commit to master
    branch_parent_sha = merge_commit['parents'][1]['sha']  # this will lead to the first commit of the branch I chose
    master_base_commit_sha = merge_commit['parents'][0]['sha']

    # Unless it's not the base commit of the master which this branch was created on, keep iterating
    while branch_parent_sha != master_base_commit_sha:
        parent = pydot.Node(branch_parent_sha, label=f'{branch_parent_sha}\n{branch_name}')
        graph.add_node(parent)
        graph.add_edge(pydot.Edge(parent, child))
        child = parent
        branch_parent_sha = branch_commits[branch_parent_sha]['parents'][0]['sha']

    base_commit_node = pydot.Node(master_base_commit_sha, label=f'{master_base_commit_sha}\nmaster')
    graph.add_node(base_commit_node)
    graph.add_edge(pydot.Edge(base_commit_node, child))

    graph.write(OUTPUT_FILE_NAME)
    logger.info(f'Graph created successfully check graph .dot file')
