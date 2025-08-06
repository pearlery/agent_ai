
import asyncio
import subprocess

AGENTS = [
    "agents/input_agent.py",
    "agents/attack_type_agent.py",
    "agents/context_agent.py",
    "agents/recommendation_agent.py"
]

async def run_agent(path):
    print(f"🚀 Starting {path}")
    process = await asyncio.create_subprocess_exec("python", path)
    await process.wait()

async def main():
    tasks = [asyncio.create_task(run_agent(agent)) for agent in AGENTS]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
