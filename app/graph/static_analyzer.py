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

import logging as log
import os
import shutil
from subprocess import PIPE, CalledProcessError, run
from typing import Any, List
from langchain_core.runnables import RunnableSerializable
from app.core.utils import check_path_type, extract_zipfile

from app.graph.prompt_template import create_static_analyzer_chain, wrap_prompt
from pydantic import BaseModel, Field


def checkTofuFiles(output_folder) -> list[str]:
    # Check for tofu files in the output folder
    if os.path.isdir(output_folder):
        files_with_extension = [f for f in os.listdir(output_folder) if f.endswith(".tofu") or f.endswith(".tofuvars")]
        return files_with_extension
    return []


def convertFileExtension(output_folder, tofu_files) -> dict:
    # Convert the extension from .tofu/.tofuvars to .tf/.tfvars
    file_rename_map = {}
    new_filename = ""
    for files in tofu_files:
        if files.endswith(".tofu"):
            old_path = os.path.join(output_folder, files)
            new_filename = "modified_" + os.path.splitext(files)[0] + ".tf"
            new_path = os.path.join(output_folder, new_filename)
            os.rename(old_path, new_path)
        elif files.endswith(".tofuvars"):
            old_path = os.path.join(output_folder, files)
            new_filename = "modified_" + os.path.splitext(files)[0] + ".tfvars"
            new_path = os.path.join(output_folder, new_filename)
            os.rename(old_path, new_path)
        file_rename_map[files] = new_filename
    return file_rename_map


def modifyResponse(file_rename_map, response) -> str:
    modified_output = ""
    if response == "":
        return ""
    for old_filename, new_filename in file_rename_map.items():
        if not modified_output:
            modified_output = response.replace(new_filename, old_filename)
        else:
            modified_output = modified_output.replace(new_filename, old_filename)
    return modified_output


class StaticAnalyzer:
    """
    Terraform Static Analyzer.
    """

    def __init__(self, chain: RunnableSerializable, name: str = "static_analyzer"):
        """
        Initializes the Terraform Static Analyzer.

        Args:
            chain (RunnableSerializable): LLM model pipeline.
        """
        self.chain = chain
        self.name = name

    def __call__(self, context_files: str) -> dict[str, Any]:
        """
        Runs linting and validation on Terraform code.

        Args:
            context_Files (str): List of Terraform files (file paths or inline content).

        Returns:
            dict[str, Any]: Static analysis output.

        """
        log.info(f"{self.name} called")

        if not self.chain:
            raise ValueError(f"{self.name}: Chain is not set in the context")

        if not context_files:
            raise ValueError(f"{self.name}: Context files are not passed in")

        # Check if the context_files is a zip file or a directory
        path_type = check_path_type(context_files)
        if path_type == "zip":
            # Extract the zip file to a temporary directory if it's a zip file
            tmp_dir = os.getenv("TMP_DIR", ".")
            output_folder = os.path.join(tmp_dir, "repo_copy")
            extract_zipfile(context_files, output_folder)
        elif path_type == "directory":
            output_folder = context_files
        else:
            raise ValueError(
                f"'{context_files}' is neither a zip file nor a directory."
            )

        try:
            file_rename_map = {}
            # Check for the tofu files in the repo
            tofu_files = checkTofuFiles(output_folder)
            if tofu_files:
                file_rename_map = convertFileExtension(output_folder, tofu_files)
            tf_validate_out = run(
                ["terraform", "validate", "-no-color"],
                cwd=output_folder,
                stdout=PIPE,
                stderr=PIPE,
                text=True,
            )
            lint_stdout, lint_stderr = "", ""
            # If terraform validate passes, run tflint
            if tf_validate_out.returncode == 0:
                # Need tf init to download the necessary third party
                # dependencies, otherwise most linters would fail
                run(
                    ["terraform", "init", "-backend=false"],
                    check=True,
                    cwd=output_folder,
                    capture_output=True,
                    text=True,
                )

                tflint_out = run(
                    ["tflint", "--format=compact", "--recursive"],
                    cwd=output_folder,
                    stdout=PIPE,
                    stderr=PIPE,
                    text=True,
                )
                lint_stdout = tflint_out.stdout
                lint_stderr = tflint_out.stderr
        except CalledProcessError as e:
            log.error(f"Error while running static checks: {e.stderr}")
            return {}

        # Remove the local copy of the repo
        if path_type == "zip":
            try:
                shutil.rmtree(output_folder)
                log.debug("Repo deleted successfully")
            except Exception as e:
                log.error(
                    f"An error occured while removing the local copy of the repo: {e}"
                )
                return {}

        try:
            if file_rename_map:
                # Replace all the modified file names in  tf_validate output, error, lint output
                tf_validate_output = modifyResponse(file_rename_map, tf_validate_out.stdout)
                tf_validate_error = modifyResponse(file_rename_map, tf_validate_out.stderr)
                tf_lint_output = modifyResponse(file_rename_map, lint_stdout)
                tf_lint_error = modifyResponse(file_rename_map, lint_stderr)
            else:
                tf_validate_output = tf_validate_out.stdout
                tf_validate_error = tf_validate_out.stderr
                tf_lint_output = lint_stdout
                tf_lint_error = lint_stderr
            prompt_template = create_static_analyzer_chain(self.chain)
            response = prompt_template.invoke({
                "linter_outputs": wrap_prompt(
                    "terraform validate output:",
                    f"{tf_validate_error}",
                    f"{tf_validate_output}",
                    "",
                    "tflint output:",
                    f"{tf_lint_error}",
                    f"{tf_lint_output}",
                )}
            )
            static_analyzer_response = []
            static_analyzer_response = [f"{res.file_name}: {res.full_issue_description}" for res in
                                            response.issues]
        except Exception as e:
            log.error(
                f"Error in {self.name} while running the static analyzer chain: {e}"
            )
            raise e

        return {"static_analyzer_output": ",".join(static_analyzer_response)}
