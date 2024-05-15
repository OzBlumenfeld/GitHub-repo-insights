import os

import argparse
from typing import List

from gh_api_helper import GithubAPIHelper
from graph import create_branch_commits_graph
from logger import setup_logger
from rest_api_util import _get_request


def main() -> None:
    extract_gh_data(owner=gh_api_helper.organization, repo=gh_api_helper.repo)
    create_branch_commits_graph(logger=logger, gh_api_helper=gh_api_helper)


def extract_gh_data(owner: str, repo: str) -> None:
    _log_latest_releases(owner, repo)
    logger.debug(f'Getting the repository data from: {gh_api_helper.GH_REPO_API_URL}')
    response = _get_request(url=gh_api_helper.GH_REPO_API_URL, headers=headers)
    response_json = response.json()
    stars_counts = response_json['stargazers_count']
    forks_counts = response_json['forks_count']
    contributors_count, contributors_user_names = _extract_contributors(response_json['contributors_url'])
    pulls_count, contributors_prs_count_dict = _extract_pull_requests(gh_api_helper.GH_REPO_PULL_REQ_API_URL,
                                                                 contributors_user_names)

    '''
    I wasn't sure if the expectation was to return only the contributors names
    but I decided to return the count of PRs for each contributor as well for better insights
    '''
    sorted_contributors_prs_count = sorted(contributors_prs_count_dict.items(), key=lambda item: item[1], reverse=True)
    report = (f'Repo {owner}/{repo} has {stars_counts} stars, {forks_counts} forks, {contributors_count} contributors,'
              f' {pulls_count} pull requests,\n contributors_prs_count: {sorted_contributors_prs_count}.')
    logger.info(report)


def _log_latest_releases(owner: str, repo: str) -> None:
    releases_limit = os.getenv('GH_FETCH_REPO_RELEASES_COUNT', 3)
    url = f'{gh_api_helper.GH_REPO_RELEASES_API_URL}?per_page={releases_limit}'
    logger.debug(f'Getting the releases data from: {url}')

    def _process_release(release):
        logger.info(f"Release: {release['name']}, Published at: {release['published_at']}")

    logger.info(f'Logging {releases_limit} latest releases for {owner}/{repo}')
    gh_api_helper.read_pages_until_limit(url=url, process_page=_process_release, limit=releases_limit)


def _extract_contributors(contributors_url: str) -> (int, list[str]):
    contributors_user_names = []
    contributors_count = 0

    def _process_contributor(contributor) -> None:
        nonlocal contributors_count
        nonlocal contributors_user_names
        contributors_user_names.append(contributor['login'])
        contributors_count += 1

    gh_api_helper.read_pages_until_limit(url=contributors_url, process_page=_process_contributor)
    return contributors_count, contributors_user_names


def _extract_pull_requests(url: str, contributors_user_names: List[str]) -> (int, dict[str, int]):
    pulls_count = 0
    contributors_prs_count = {}

    def _process_pr(pr):
        nonlocal contributors_prs_count
        nonlocal pulls_count
        pulls_count += 1
        user = pr['user']['login']
        if user in contributors_user_names:  # Check if the user is a contributor of this repository
            if user in contributors_prs_count:
                contributors_prs_count[user] += 1
            else:
                contributors_prs_count[user] = 1

    gh_api_helper.read_pages_until_limit(url=url, process_page=_process_pr)
    return pulls_count, contributors_prs_count


if __name__ == "__main__":
    # Specifying the arguments that the CLI tool will accept
    parser = argparse.ArgumentParser(description='GitHub API data extraction.')
    parser.add_argument('token', help='GitHub token')
    parser.add_argument('owner', help='GitHub repository owner')
    parser.add_argument('repo', help='GitHub repository name')
    parser.add_argument('--stdout', action='store_true', help='Log to stdout')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    '''
    Few comments:
    I'm using tokens to grant more convenient rate limit of the API, most of them are open to public
    I wanted this tool to be generic as possible, because tomorrow our needs might change and we might
     need to use it for many other repositories
    So extended the input to be any owner and repo in GitHub
    '''

    logger = setup_logger(args.stdout, args.debug)
    headers = {'Authorization': f'token {args.token}'}
    gh_api_helper = GithubAPIHelper(logger=logger, headers=headers, organization=args.owner, repo=args.repo)
    main()
