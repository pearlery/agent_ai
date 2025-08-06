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

from utils.nats_handler import NATSHandler
from agents.input_agent import run_input_agent
from agents.analysis_agent import AnalysisAgent
from agents.recommendation_agent import RecommendationAgent

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
        
    async def load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
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
            await self.nats_handler.connect()
            logger.info("NATS connection established")
        except Exception as e:
            logger.error(f"Failed to initialize NATS: {e}")
            raise
    
    async def run_input_phase(self) -> None:
        """
        Run the input agent to load and publish alerts.
        This runs once at startup to populate the pipeline.
        """
        try:
            alert_file_path = Path(__file__).parent.parent / "data" / "test.json"
            logger.info("Starting input phase...")
            await run_input_agent(self.nats_handler, str(alert_file_path))
            logger.info("Input phase completed")
        except Exception as e:
            logger.error(f"Input phase failed: {e}")
            raise
    
    async def run_processing_agents(self) -> None:
        """
        Run the analysis and recommendation agents concurrently.
        These agents run continuously to process alerts.
        """
        try:
            # Create agent instances
            analysis_agent = AnalysisAgent(self.nats_handler, self.config['llm'])
            recommendation_agent = RecommendationAgent(self.nats_handler, self.config['llm'])
            
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
            raise
    
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
            raise
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
    Run a quick demonstration with limited alerts processing.
    """
    print("🚀 Starting Agntics AI Demo Mode...")
    
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    orchestrator = AgentOrchestrator(str(config_path))
    
    try:
        await orchestrator.load_config()
        await orchestrator.setup_logging()
        await orchestrator.initialize_nats()
        
        # Run input phase
        print("📥 Publishing test alerts...")
        await orchestrator.run_input_phase()
        
        # Run processing for a limited time
        print("🔄 Processing alerts...")
        
        analysis_agent = AnalysisAgent(orchestrator.nats_handler, orchestrator.config['llm'])
        recommendation_agent = RecommendationAgent(orchestrator.nats_handler, orchestrator.config['llm'])
        
        # Run for 30 seconds or until all alerts are processed
        processing_task = asyncio.gather(
            analysis_agent.run(),
            recommendation_agent.run(),
            return_exceptions=True
        )
        
        try:
            await asyncio.wait_for(processing_task, timeout=30.0)
        except asyncio.TimeoutError:
            print("⏰ Demo timeout reached")
        
        print("✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    finally:
        await orchestrator.cleanup()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Run in demo mode with timeout
        asyncio.run(run_demo_mode())
    else:
        # Run in full mode
        asyncio.run(main())