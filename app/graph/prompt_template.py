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

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable
from pydantic import BaseModel, Field
from typing import List
"""
This function creates a prompt template for the static analyzer agent which is responsible for organizing Terraform related linter outputs.
"""

class StaticAnalyzerOutputIssues(BaseModel):
    file_name: str = Field(description="This is the filename which has terraform linter issues")
    full_issue_description: str = Field(description="This is the full description of terraform linter issue")


class StaticAnalyzerOutputList(BaseModel):
    issues: List[StaticAnalyzerOutputIssues] = Field(description="List of terraform linter issues found")


def create_static_analyzer_chain(model: RunnableSerializable) -> RunnableSerializable[
    dict, dict | StaticAnalyzerOutputList]:
    llm_with_structured_output = model.with_structured_output(StaticAnalyzerOutputList)
    system_message_content = wrap_prompt("""\
                                        Your are an experienced software engineer who's task is to organize Terraform related linter outputs.
                                        Remove ONLY the line numbers but keep everything else, don't remove any detail from the issue message.
                                        Remove the warnings, only keep the errors in the final list.
                                         """)

    user_message_content = wrap_prompt("""
                                   Input Format:
                                   The terraform linter output: {linter_outputs}
                                   """)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_message_content,
            ),
            "user", user_message_content,
        ]
    )

    return prompt | llm_with_structured_output


def wrap_prompt(*args):
    lines = []
    min_indent = 999999  # arbitrary large number

    for arg in args:
        for line in arg.split("\n"):
            if line.lstrip():
                indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, indent)
            lines.append(line)

    normalized_lines = []
    for line in lines:
        if line.lstrip():
            current_indent = len(line) - len(line.lstrip())
            relative_indent = current_indent - min_indent
            normalized_lines.append(" " * relative_indent + line.lstrip().rstrip())
        else:
            normalized_lines.append("")

    return "\n".join(normalized_lines)
