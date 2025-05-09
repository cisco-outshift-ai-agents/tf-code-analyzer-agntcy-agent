# Copyright 2025 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import io
import logging
import os
import zipfile
from http import HTTPStatus
from urllib.parse import urlparse

import requests
from fastapi import HTTPException
from github import Github, GithubException
from pydantic import SecretStr

logger = logging.getLogger(__name__)


class GithubClient:
    """
    A client for interacting with GitHub, providing functionality for authentication
    and downloading repositories as zip files.
    Classes:
        GithubClient: A class to handle GitHub API interactions.
    Methods:
        __init__(github_token: SecretStr | None):
            Initializes the GithubClient with an optional GitHub token for authentication.
        _authenticate(github_token: SecretStr | None) -> Github:
            Authenticates with GitHub using the provided token or anonymous access if no token is provided.
        download_repo_zip(repo_url: str, branch: str, destination_folder: str) -> str:
            Downloads a zipball of the specified branch from a GitHub repository URL,
            extracts it into the destination folder, and returns the path to the extracted folder.
    """

    def __init__(self, github_token: SecretStr | None):
        self.token = github_token
        self.client = self._authenticate(github_token)

    def _authenticate(self, github_token: SecretStr | None) -> Github:
        try:
            if github_token is None:
                g = Github()
                logger.info("No GitHub token provided. Using anonymous access.")
            else:
                g = Github(github_token.get_secret_value())
                _ = g.get_rate_limit()
            return g
        except GithubException as e:
            logger.error(f"GitHub authentication failed: {e}")
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid GitHub token"
            ) from e

    def download_repo_zip(
        self, repo_url: str, branch: str, destination_folder: str
    ) -> str:
        """
        Downloads a zipball of the specified branch from the provided GitHub repository URL,
        unzips it into the destination folder, and returns the path to the extracted folder.

        :param repo_url: User-provided GitHub repository URL.
        :param branch: Branch name (e.g., "main", "master").
        :param destination_folder: Local folder where the repository should be extracted.
        :return: Full path to the extracted repository folder (destination_folder/folder_name).
        """
        try:
            # Parse the URL using urlparse
            parsed_url = urlparse(repo_url)
            if parsed_url.netloc.lower() != "github.com":
                raise ValueError("The provided URL is not a GitHub URL.")

            # Split the path into parts, filtering out empty parts
            path_parts = [part for part in parsed_url.path.split("/") if part]
            if len(path_parts) < 2:
                raise ValueError(
                    "Invalid GitHub repository URL format. Expected format: https://github.com/<owner>/<repo>"
                )

            # Extract owner and repository name
            owner, repo = path_parts[0], path_parts[1]
            logger.info(f"Extracted owner: {owner}, repo: {repo}")

            # Build the GitHub API URL to download the zipball for the
            # specified branch.
            api_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"
            logger.info("Downloading zipball from: %s", api_url)

            headers = {
                "Accept": "application/vnd.github.v3+json",
            }
            if self.token is not None:
                headers["Authorization"] = f"token {self.token.get_secret_value()}"

            # Make the GET request with stream enabled.
            response = requests.get(api_url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            # Read the response content into a BytesIO object.
            zip_data = io.BytesIO()
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    zip_data.write(chunk)
            zip_data.seek(0)

            # Open the zip file from memory and extract its contents.
            with zipfile.ZipFile(zip_data, "r") as zip_ref:
                file_list = zip_ref.namelist()
                if not file_list:
                    raise ValueError("Downloaded zip file is empty or corrupted.")

                # Assuming the first entry contains the root folder name.
                folder_name = file_list[0].split("/")[0]
                extract_path = os.path.join(destination_folder)
                zip_ref.extractall(extract_path)

            extracted_repo_path = os.path.join(destination_folder, folder_name)
            logger.info(
                "Repository extracted successfully to '%s'", extracted_repo_path
            )
            return extracted_repo_path

        except Exception as e:
            logger.exception(
                "Failed to download and extract GitHub repository %s", str(e)
            )
            raise
