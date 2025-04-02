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
from typing import Any, Dict, List, Optional, Union

from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import RunnableSerializable
from langgraph.graph import END, Graph, MessageGraph

from app.graph.static_analyzer import StaticAnalyzer


class StaticAnalyzerWorkflow:
    def __init__(self, chain: RunnableSerializable):
        """
        Initialize the StaticAnalyzerWorkflow as a LangGraph workflow.

        Args:
            chain (RunnableSerializable): A callable LLM chain that runs the static analysis.
        """
        self.chain = chain
        self.graph = self.build_graph()

    def build_graph(self):
        """
        Build a LangGraph instance of the Static Analysis workflow.

        Returns:
            CompiledGraph: A compiled LangGraph instance.
        """
        graph = Graph()

        # Create the StaticAnalyzer node
        analyzer = StaticAnalyzer(self.chain)

        # Wrapper function to handle LangGraph input and ensure correct return
        # format
        def review_node(input_data):
            """
            Node function for running the static analysis.

            Args:
                input_data (dict): Input data containing `context_files`.

            Returns:
                dict: Output data containing `results` as structured linter results.
            """

            try:
                result = analyzer(input_data["file_path"])
            except Exception as e:
                raise Exception(f"Failed to process analysis: {e}")
            return result

        # Add the StaticAnalyzer node to the graph
        graph.add_node("static_analyzer", review_node)

        # Set Graph edges
        graph.set_entry_point("static_analyzer")
        graph.add_edge("static_analyzer", END)

        return graph.compile()

    def analyze(self, context_files: str):
        """
        Runs the LangGraph workflow for static analysis on Terraform files.

        Args:
            context_files str: Path to folder or zip file containing Terraform files.

        Returns:
            dict: Output data containing `static_analyzer_output` as structured linter results.
        """
        try:
            result = self.graph.invoke({"file_path": context_files})
        except Exception as e:
            raise Exception(f"Terraform analysis failed: {e}")

        return result
