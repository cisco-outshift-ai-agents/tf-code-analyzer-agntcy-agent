from agp_api.gateway.gateway_container import GatewayContainer
from agp_api.agent.agent_container import AgentContainer

class AGPConfig:
    gateway_container = GatewayContainer()
    agent_container = AgentContainer()
    remote_agent = "server"

