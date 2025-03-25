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

from setuptools import find_packages, setup

setup(
    name="static_analyzer_agent",
    version="1.0.0",  # ✅ Required for dirctl version detection
    python_requires=">=3.8",  # ✅ Required for dirctl to detect Python version
    packages=find_packages(),
    install_requires=[],  # Add dependencies if needed
)
