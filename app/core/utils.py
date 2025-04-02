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

import logging
import shutil
import os
import zipfile
from pathlib import Path

from dotenv import find_dotenv, load_dotenv


def extract_zipfile(zip_path: str, extract_path: str):
    """
    Extract contents from a zipfile and store them in a local directory.

    Args:
    zip_path (str): Path to the zip file
    extract_path (str): Path to the directory where contents will be extracted

    Returns:
    None
    """
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)
    print(
        f"Extracted contents from '{os.path.basename(zip_path)}' to '{extract_path}' directory."
    )


def check_path_type(path: str) -> str:
    """
    Check if the given path is a zip file or a directory.

    Args:
    path (str): Path to check

    Returns:
    str: 'zip' if it's a zip file, 'directory' if it's a directory, 'other' otherwise
    """
    path_obj = Path(path)

    if path_obj.is_file() and path_obj.suffix.lower() == ".zip":
        return "zip"
    elif path_obj.is_dir():
        return "directory"
    else:
        return "other"


def load_environment_variables(env_file: str | None = None) -> None:
    """
    Load environment variables from a .env file safely.

    This function loads environment variables from a `.env` file, ensuring
    that critical configurations are set before the application starts.

    Args:
        env_file (str | None): Path to a specific `.env` file. If None,
                               it searches for a `.env` file automatically.

    Behavior:
    - If `env_file` is provided, it loads the specified file.
    - If `env_file` is not provided, it attempts to locate a `.env` file in the project directory.
    - Logs a warning if no `.env` file is found.

    Returns:
        None
    """
    env_path = env_file or find_dotenv()

    if env_path and os.path.exists(env_path):
        load_dotenv(env_path, override=True)
        logging.info(f".env file loaded from {env_path}")
    else:
        logging.info(".env file not found, assuming environment variables are already set (e.g. via Docker)")



def check_command_exists(command):
    """Check if a command exists on the system"""
    return shutil.which(command) is not None


def check_required_binaries():
    """Check if required binaries are installed"""
    required_binaries = ["terraform", "tflint"]
    missing_binaries = [
        binary for binary in required_binaries if not check_command_exists(binary)
    ]

    if missing_binaries:
        raise ValueError(f"Missing required binaries: {', '.join(missing_binaries)}")
