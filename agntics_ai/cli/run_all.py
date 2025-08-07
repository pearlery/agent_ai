"""
CLI orchestrator to run all agents concurrently.
"""
import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import List
import yaml

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from ..utils.nats_handler import NATSHandler
from ..agents.input_agent import run_input_agent
from ..agents.analysis_agent import AnalysisAgent
from ..agents.recommendation_agent import RecommendationAgent
from ..control.control_app import create_app
from ..utils.graphql_publisher import init_graphql_publisher
import threading
import uvicorn

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates the execution of all agents in the cybersecurity pipeline.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the orchestrator with configuration.
        
        Args:
            config_path: Path to the configuration YAML file
        """
        self.config_path = Path(config_path)
        self.config = None
        self.nats_handler = None
        self.agents = []
        self.running = False
        self.control_agent_thread = None
        
    async def load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    async def setup_logging(self) -> None:
        """Setup logging based on configuration."""
        log_config = self.config.get('logging', {})
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
    
    async def initialize_nats(self) -> None:
        """Initialize and connect to NATS."""
        try:
            self.nats_handler = NATSHandler(self.config['nats'])
            # Try to connect with short timeout
            connect_task = asyncio.create_task(self.nats_handler.connect())
            await asyncio.wait_for(connect_task, timeout=5.0)
            logger.info("NATS connection established")
        except asyncio.TimeoutError:
            logger.warning("NATS connection timeout - running without NATS")
            self.nats_handler = None
        except Exception as e:
            logger.warning(f"Failed to initialize NATS: {e}")
            logger.info("Running without NATS - some features may be limited")
            self.nats_handler = None
        
        # Initialize GraphQL Publisher
        graphql_topic = self.config.get('nats', {}).get('subjects', {}).get('graphql_mutation', 'agentAI.graphql.mutation')
        init_graphql_publisher(self.nats_handler, graphql_topic)
        logger.info(f"GraphQL Publisher initialized with topic: {graphql_topic}")
    
    def start_control_agent(self) -> None:
        """Start the Control Agent API server in a separate thread."""
        def run_control_server():
            try:
                app = create_app()
                logger.info("Starting Control Agent API server on port 9004...")
                uvicorn.run(app, host="0.0.0.0", port=9004, log_level="info")
            except Exception as e:
                logger.error(f"Control Agent server failed: {e}")
        
        # Start control agent in daemon thread
        self.control_agent_thread = threading.Thread(
            target=run_control_server,
            daemon=True,
            name="ControlAgentServer"
        )
        self.control_agent_thread.start()
        logger.info("Control Agent API server started in background")
    
    def start_web_app(self) -> None:
        """Start the Web App in a separate thread."""
        def run_web_server():
            try:
                from ..webapp.app import run_webapp
                logger.info("Starting Web App on port 5000...")
                run_webapp(host="0.0.0.0", port=5000, debug=False)
            except Exception as e:
                logger.error(f"Web App server failed: {e}")
        
        # Start web app in daemon thread
        web_thread = threading.Thread(
            target=run_web_server,
            daemon=True,
            name="WebAppServer"
        )
        web_thread.start()
        logger.info("Web App server started in background")
    
    async def run_input_phase(self) -> None:
        """
        Run the input agent to load and publish alerts.
        This runs once at startup to populate the pipeline.
        """
        try:
            if self.nats_handler is None:
                logger.info("Skipping input phase - NATS not available")
                return
                
            alert_file_path = Path(__file__).parent.parent / "data" / "test.json"
            logger.info("Starting input phase...")
            output_file_path = Path(__file__).parent.parent.parent / "output.json"
            await run_input_agent(self.nats_handler, str(alert_file_path), str(output_file_path))
            logger.info("Input phase completed")
        except Exception as e:
            logger.error(f"Input phase failed: {e}")
            # Don't raise exception, continue without input phase
    
    async def run_processing_agents(self) -> None:
        """
        Run the analysis and recommendation agents concurrently.
        These agents run continuously to process alerts.
        """
        try:
            if self.nats_handler is None:
                logger.info("Skipping processing agents - NATS not available")
                logger.info("Control Agent API is available for manual processing")
                # Keep the main process alive
                while self.running:
                    await asyncio.sleep(1)
                return
            
            # Create agent instances  
            output_file = str(Path(__file__).parent.parent.parent / "output.json")
            analysis_agent = AnalysisAgent(self.nats_handler, self.config['llm'], output_file)
            recommendation_agent = RecommendationAgent(self.nats_handler, self.config['llm'], output_file)
            
            # Store agent references for cleanup
            self.agents = [analysis_agent, recommendation_agent]
            
            # Run agents concurrently
            logger.info("Starting processing agents...")
            await asyncio.gather(
                analysis_agent.run(),
                recommendation_agent.run(),
                return_exceptions=True
            )
            
        except Exception as e:
            logger.error(f"Processing agents failed: {e}")
            # Don't raise exception, continue running
    
    async def run(self) -> None:
        """
        Main orchestrator execution method.
        """
        try:
            # Load configuration and setup
            await self.load_config()
            await self.setup_logging()
            await self.initialize_nats()
            
            self.running = True
            logger.info("Agntics AI system starting up...")
            
            # Start Control Agent API server first
            self.start_control_agent()
            
            # Small delay to let Control Agent start
            await asyncio.sleep(2)
            
            # Phase 1: Load and publish alerts
            await self.run_input_phase()
            
            # Small delay to ensure messages are published before processing starts
            await asyncio.sleep(2)
            
            # Phase 2: Run processing agents continuously
            await self.run_processing_agents()
            
        except KeyboardInterrupt:
            logger.info("System interrupted by user")
        except Exception as e:
            logger.error(f"System execution failed: {e}")
            # Don't raise exception, allow cleanup to run
        finally:
            await self.cleanup()
    
    async def run_docker_mode(self) -> None:
        """
        Docker-specific run method that also starts the web app.
        """
        try:
            # Load configuration and setup
            await self.load_config()
            await self.setup_logging()
            await self.initialize_nats()
            
            self.running = True
            logger.info("Agntics AI system starting up in Docker mode...")
            
            # Start Control Agent API server first
            self.start_control_agent()
            
            # Start Web App in separate thread
            self.start_web_app()
            
            # Small delay to let services start
            await asyncio.sleep(5)
            
            # Phase 1: Load and publish alerts
            await self.run_input_phase()
            
            # Small delay to ensure messages are published before processing starts
            await asyncio.sleep(2)
            
            # Phase 2: Run processing agents continuously
            await self.run_processing_agents()
            
        except KeyboardInterrupt:
            logger.info("System interrupted by user")
        except Exception as e:
            logger.error(f"System execution failed: {e}")
            # Don't raise exception, allow cleanup to run
        finally:
            await self.cleanup()
    
    async def cleanup(self) -> None:
        """Cleanup resources and connections."""
        self.running = False
        
        # Stop agents gracefully
        for agent in self.agents:
            if hasattr(agent, 'stop'):
                agent.stop()
        
        # Close NATS connection
        if self.nats_handler:
            await self.nats_handler.close()
        
        logger.info("System cleanup completed")
    
    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, initiating graceful shutdown...")
            # Create a task to handle cleanup
            asyncio.create_task(self.cleanup())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """
    Main entry point for the CLI orchestrator.
    """
    # Determine config path
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    
    # Create and run orchestrator
    orchestrator = AgentOrchestrator(str(config_path))
    orchestrator.setup_signal_handlers()
    
    try:
        await orchestrator.run()
    except Exception as e:
        logger.error(f"Orchestrator failed: {e}")
        sys.exit(1)


async def run_demo_mode():
    """
    Run a quick demonstration with Control Agent only.
    """
    print("Starting Agntics AI Demo Mode...")
    
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    orchestrator = AgentOrchestrator(str(config_path))
    
    try:
        await orchestrator.load_config()
        await orchestrator.setup_logging()
        await orchestrator.initialize_nats()
        
        orchestrator.running = True
        
        # Start Control Agent
        print("Starting Control Agent API server...")
        orchestrator.start_control_agent()
        
        # Wait a bit for server to start
        await asyncio.sleep(3)
        
        print("Demo running with Control Agent API on http://127.0.0.1:9004")
        print("Press Ctrl+C to stop...")
        
        # Keep running for demo
        try:
            while orchestrator.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Demo stopped by user")
        
        print("Demo completed successfully!")
        
    except Exception as e:
        print(f"Demo failed: {e}")
    finally:
        await orchestrator.cleanup()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Run in demo mode with timeout
        asyncio.run(run_demo_mode())
    elif len(sys.argv) > 1 and sys.argv[1] == "--docker":
        # Run in Docker mode with both Control Agent and Web App
        print("Starting Agntics AI in Docker mode...")
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        orchestrator = AgentOrchestrator(str(config_path))
        orchestrator.setup_signal_handlers()
        
        try:
            asyncio.run(orchestrator.run_docker_mode())
        except Exception as e:
            logger.error(f"Docker mode failed: {e}")
            sys.exit(1)
    else:
        # Run in full mode
        asyncio.run(main())