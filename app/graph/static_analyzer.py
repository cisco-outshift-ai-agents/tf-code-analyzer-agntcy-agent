import logging as log
import os
import shutil
from subprocess import PIPE, CalledProcessError, run
from typing import Any

from langchain_core.runnables import RunnableSerializable

from core.utils import check_path_type, extract_zipfile

from graph.prompt_template import create_static_analyzer_prompt_template, wrap_prompt


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
            prompt_template = create_static_analyzer_prompt_template()
            prompt = prompt_template.invoke(
                {
                    "linter_outputs": wrap_prompt(
                        "terraform validate output:",
                        f"{tf_validate_out.stderr}",
                        f"{tf_validate_out.stdout}",
                        "",
                        "tflint output:",
                        f"{lint_stderr}",
                        f"{lint_stdout}",
                    )
                }
            )
            response = self.chain.invoke(prompt)
            log.info(f"Static analyzer output: {response}")

        except Exception as e:
            log.error(
                f"Error in {self.name} while running the static analyzer chain: {e}"
            )
            raise e

        return {"static_analyzer_output": response.content}
