import logging

from rest_api_util import _get_request

'''
GitHub API Helper class to extract data from GitHub API
'''
class GithubAPIHelper:
    headers: dict
    logger: logging.Logger
    # Class state per repository, could be made more generic but kept it this way for simplicity
    organization: str
    repo: str

    def __init__(self, logger, headers, organization, repo):
        self.logger = logger
        self.headers = headers
        self.organization = organization
        self.repo = repo

        # GH API Constants
        self.GH_REPO_API_URL = f'https://api.github.com/repos/{organization}/{repo}'
        self.GH_REPO_PULL_REQ_API_URL = f'https://api.github.com/repos/{organization}/{repo}/pulls'
        self.GH_REPO_RELEASES_API_URL = f'https://api.github.com/repos/{organization}/{repo}/releases'
        self.GH_REPO_BRANCH_COMMITS = f'https://api.github.com/repos/{organization}/{repo}/commits'

    def read_pages_until_limit(self, url: str, process_page, limit: int = -1):
        count = 0
        keep_reading_next_page = url if limit < 0 else url and count < limit
        while keep_reading_next_page:
            self.logger.debug(f'Getting the page from: {url}')
            response = _get_request(url=url, headers=self.headers)
            data = response.json()
            for item in data:
                if 0 <= limit <= count:
                    break
                process_page(item)
                count += 1
            url = response.links.get('next', None)
            if url:
                url = url.get('url', None)
            keep_reading_next_page = url if limit < 0 else url and count < limit
