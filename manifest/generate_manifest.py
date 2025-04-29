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
import os
import sys
from pathlib import Path
from pydantic import AnyUrl
from agntcy_acp.manifest import (
    AgentManifest,
    AgentDeployment,
    DeploymentOptions,
    LangGraphConfig,
    EnvVar,
    AgentMetadata,
    AgentACPSpec,
    AgentRef,
    Capabilities,
    SourceCodeDeployment,
    AgentDependency
)
# Get the absolute path of the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "./.."))
sys.path.insert(0, parent_dir)
from app.models.ap.models import RunCreateStateless, RunCreateStatelessOutput, Config

manifest = AgentManifest(
    metadata=AgentMetadata(
        ref=AgentRef(name="org.agntcy.tf-code-analyzer", version="0.0.1", url=None),
        description="The Terraform Static Analyzer AI Agent  performs static analysis on Terraform code to detect security risks, misconfigurations, and anti-patterns."),
    specs=AgentACPSpec(
        input=RunCreateStateless.model_json_schema(),
        output=RunCreateStatelessOutput.model_json_schema(),
        config=Config.model_json_schema(),
        capabilities=Capabilities(
            threads=None,
            callbacks=None,
            interrupts=None,
            streaming=None
        ),
        custom_streaming_update=None,
        thread_state=None,
        interrupts=None
    ),
    deployment=AgentDeployment(
        deployment_options=[
            DeploymentOptions(
                root = SourceCodeDeployment(
                    type="source_code",
                    name="src",
                    url="https://github.com/cisco-outshift-ai-agents/tf-code-analyzer-agntcy-agent", 
                    framework_config=LangGraphConfig(
                        framework_type="langgraph",
                        graph="client.agp.agp_client:build_graph"
                    )
                )
            )
        ],
        env_vars=[EnvVar(name="OPENAI_API_KEY", desc="Open AI API Key"),
                EnvVar(name="OPENAI_MODEL_NAME", desc="Open AI Model Name"),
                EnvVar(name="OPENAI_TEMPERATURE", desc="Open AI Temperature"),
                EnvVar(name="AZURE_OPENAI_API_KEY", desc="AZURE Open AI API Key"),
                EnvVar(name="AZURE_OPENAI_ENDPOINT", desc="AZURE Open AI Endpoint"),
                EnvVar(name="AZURE_OPENAI_DEPLOYMENT_NAME", desc="AZURE Open AI Deployment Name"),
                EnvVar(name="AZURE_OPENAI_API_VERSION", desc="AZURE Open AI API Version"),
                EnvVar(name="AGP_GATEWAY_ENDPOINT", desc="AGP Gateway Endpoint"),],
        dependencies=[]
    )
)

with open(f"{Path(__file__).parent}/code_analyzer_manifest.json", "w") as f:
    f.write(manifest.model_dump_json(
        exclude_unset=True,
        exclude_none=True,
        indent=2
    ))
