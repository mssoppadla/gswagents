#src/api/core/foundryagent.py
import asyncio
from typing import Optional, Dict
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder
from azure.appconfiguration.provider.aio import load
from azure.appconfiguration.provider import AzureAppConfigurationKeyVaultOptions

async def run_agent_task(
    business_tenant_id: str,  # Now used as a unique business owner identifier
    org_id: str,
    domain: str,
    instructions: str,
    description: str,
    task: str,
    thread_id: Optional[str] = None
) -> Dict:
    """
    Executes a task using Azure AI Agents with custom business-level multitenancy.
    The business_tenant_id is persisted in the thread's metadata.
    """
    APP_CONFIG_ENDPOINT = "https://xappconfig.azconfig.io"
    
    # Authenticate to Azure using your primary service identity
    async with DefaultAzureCredential() as credential:
        config = None
        try:
            # 1. Fetch System Configuration
            kv_options = AzureAppConfigurationKeyVaultOptions(credential=credential)
            config = await load(
                endpoint=APP_CONFIG_ENDPOINT,
                credential=credential,
                key_vault_options=kv_options,
            )

            project_endpoint = config.get("azure-existing-aiproject-endpoint")
            agent_id = config.get("azure-existing-agent-id")

            async with AIProjectClient(credential=credential, endpoint=project_endpoint) as project:
                
                # 2. Handle Memory & Custom Business Context
                if thread_id:
                    # Retrieve existing thread and verify business_tenant_id matches if needed
                    thread = await project.agents.threads.get_thread(thread_id)
                else:
                    # Create new thread and tag it with the Business Owner's ID in metadata
                    # Metadata allows up to 16 key/value pairs
                    thread = await project.agents.threads.create(
                        metadata={
                            "business_tenant_id": business_tenant_id,
                            "org_id": org_id,
                            "domain": domain
                        }
                    )
                
                # 3. Add Message with Dynamic Instructions
                # Note: Instructions and Description are passed here to steer the agent for this specific call
                formatted_prompt = (
                    f"Agent Profile: {description}\n"
                    f"Behavior Instructions: {instructions}\n\n"
                    f"Current Task: {task}"
                )
                
                await project.agents.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=formatted_prompt
                )

                # 4. Execute the Run
                run = await project.agents.runs.create_and_process(
                    thread_id=thread.id,
                    agent_id=agent_id
                )

                if run.status == "failed":
                    return {"thread_id": thread.id, "error": str(run.last_error), "status": "failed"}

                # 5. Retrieve Final Response
                response_text = ""
                messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
                
                async for message in messages:
                    if message.role == "assistant" and message.text_messages:
                        response_text = message.text_messages[-1].text.value

                return {
                    "thread_id": thread.id,
                    "business_tenant_id": business_tenant_id,
                    "response": response_text,
                    "status": "success"
                }

        except Exception as e:
            return {"error": str(e), "status": "error"}
        finally:
            if config:
                await config.close()

# --- Example Usage for a Business Owner ---
async def example():
    result = await run_agent_task(
        business_tenant_id=str(org_id), # force string
        org_id=str(org_id), # force string
        domain="Inventory",
        instructions="Format the output as a bulleted list.",
        description="Inventory Management Specialist",
        task=message,
        thread_id=None
    )
    print(f"Result for {result['business_tenant_id']}: {result.get('response')}")

if __name__ == "__main__":
    asyncio.run(example())
