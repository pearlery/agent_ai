"""
Tools status monitoring system for tracking security tools availability.
"""
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional
from enum import Enum
from .output_handler import get_output_handler

logger = logging.getLogger(__name__)


class ToolStatus(Enum):
    """Tool status options."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MISSING = "missing"
    ERROR = "error"


class SecurityTool:
    """Represents a security tool and its monitoring configuration."""
    
    def __init__(self, name: str, check_method: str = "ping", endpoint: Optional[str] = None):
        """
        Initialize a security tool.
        
        Args:
            name: Name of the security tool
            check_method: Method to check tool status ('ping', 'http', 'mock')
            endpoint: Endpoint URL for http checks
        """
        self.name = name
        self.check_method = check_method
        self.endpoint = endpoint
        self.status = ToolStatus.MISSING
        self.last_checked = None
        self.error_message = ""
    
    async def check_status(self) -> ToolStatus:
        """
        Check the current status of the tool.
        
        Returns:
            Current tool status
        """
        try:
            if self.check_method == "http" and self.endpoint:
                status = await self._check_http_endpoint()
            elif self.check_method == "ping":
                status = await self._check_ping()
            else:
                # Mock status for demonstration
                status = await self._mock_check()
            
            self.status = status
            self.error_message = ""
            logger.debug(f"Tool {self.name} status: {status.value}")
            
        except Exception as e:
            self.status = ToolStatus.ERROR
            self.error_message = str(e)
            logger.error(f"Error checking tool {self.name}: {e}")
        
        return self.status
    
    async def _check_http_endpoint(self) -> ToolStatus:
        """Check tool status via HTTP endpoint."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.endpoint, timeout=5) as response:
                    if response.status == 200:
                        return ToolStatus.ACTIVE
                    else:
                        return ToolStatus.INACTIVE
        except aiohttp.ClientError:
            return ToolStatus.INACTIVE
        except asyncio.TimeoutError:
            return ToolStatus.INACTIVE
    
    async def _check_ping(self) -> ToolStatus:
        """Check tool status via ping (mock implementation)."""
        # This is a simplified mock - in real implementation you'd use ping
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # Mock logic based on tool name
        if "suricata" in self.name.lower():
            return ToolStatus.ACTIVE
        elif "osquery" in self.name.lower():
            return ToolStatus.INACTIVE
        else:
            return ToolStatus.MISSING
    
    async def _mock_check(self) -> ToolStatus:
        """Mock check for demonstration purposes."""
        await asyncio.sleep(0.05)  # Simulate check delay
        
        # Mock status based on tool name for demo
        mock_statuses = {
            "Suricata IDS": ToolStatus.ACTIVE,
            "OSQuery": ToolStatus.INACTIVE,
            "YARA Scanner": ToolStatus.MISSING,
            "CrowdStrike Falcon": ToolStatus.ACTIVE,
            "Splunk SIEM": ToolStatus.ACTIVE,
            "Zscaler Web Gateway": ToolStatus.ACTIVE,
            "Windows Defender": ToolStatus.ACTIVE,
            "Sysmon": ToolStatus.INACTIVE
        }
        
        return mock_statuses.get(self.name, ToolStatus.MISSING)
    
    def to_dict(self) -> Dict[str, str]:
        """Convert tool to dictionary format for output."""
        return {
            "name": self.name,
            "status": self.status.value
        }


class ToolsMonitor:
    """Monitors the status of security tools."""
    
    def __init__(self):
        """Initialize the tools monitor with default security tools."""
        self.tools: Dict[str, SecurityTool] = {}
        self._initialize_default_tools()
    
    def _initialize_default_tools(self) -> None:
        """Initialize with common security tools."""
        default_tools = [
            SecurityTool("Suricata IDS", "mock"),
            SecurityTool("OSQuery", "mock"),
            SecurityTool("YARA Scanner", "mock"),
            SecurityTool("CrowdStrike Falcon", "mock"),
            SecurityTool("Splunk SIEM", "mock"),
            SecurityTool("Zscaler Web Gateway", "mock"),
            SecurityTool("Windows Defender", "mock"),
            SecurityTool("Sysmon", "mock")
        ]
        
        for tool in default_tools:
            self.tools[tool.name] = tool
    
    def add_tool(self, tool: SecurityTool) -> None:
        """
        Add a new tool to monitor.
        
        Args:
            tool: SecurityTool instance to add
        """
        self.tools[tool.name] = tool
        logger.info(f"Added tool to monitor: {tool.name}")
    
    def remove_tool(self, tool_name: str) -> None:
        """
        Remove a tool from monitoring.
        
        Args:
            tool_name: Name of the tool to remove
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Removed tool from monitor: {tool_name}")
    
    async def check_all_tools(self) -> Dict[str, ToolStatus]:
        """
        Check the status of all monitored tools.
        
        Returns:
            Dictionary mapping tool names to their status
        """
        results = {}
        
        # Check all tools concurrently
        tasks = []
        for tool_name, tool in self.tools.items():
            tasks.append(tool.check_status())
        
        # Wait for all checks to complete
        statuses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for (tool_name, tool), status in zip(self.tools.items(), statuses):
            if isinstance(status, Exception):
                tool.status = ToolStatus.ERROR
                tool.error_message = str(status)
                results[tool_name] = ToolStatus.ERROR
            else:
                results[tool_name] = status
        
        logger.info(f"Checked {len(self.tools)} tools")
        return results
    
    def get_tools_for_output(self) -> List[Dict[str, str]]:
        """
        Get tools status in the format required for output.
        
        Returns:
            List of tool dictionaries for output
        """
        return [tool.to_dict() for tool in self.tools.values()]
    
    async def update_output(self, session_id: str, output_file_path: str = "output.json") -> None:
        """
        Update the output file with current tools status.
        
        Args:
            session_id: Session ID to update
            output_file_path: Path to output file
        """
        try:
            # Check all tools first
            await self.check_all_tools()
            
            # Get output handler and update tools status
            output_handler = get_output_handler(output_file_path)
            tools_data = self.get_tools_for_output()
            
            output_handler.update_tools_status(session_id, tools_data)
            output_handler.save_to_file()
            
            logger.info(f"Updated tools status for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to update tools status: {e}")
    
    def get_active_tools(self) -> List[str]:
        """Get list of active tool names."""
        return [
            tool.name for tool in self.tools.values() 
            if tool.status == ToolStatus.ACTIVE
        ]
    
    def get_inactive_tools(self) -> List[str]:
        """Get list of inactive tool names."""
        return [
            tool.name for tool in self.tools.values() 
            if tool.status == ToolStatus.INACTIVE
        ]
    
    def get_missing_tools(self) -> List[str]:
        """Get list of missing tool names."""
        return [
            tool.name for tool in self.tools.values() 
            if tool.status == ToolStatus.MISSING
        ]
    
    def get_error_tools(self) -> List[str]:
        """Get list of tools with errors."""
        return [
            tool.name for tool in self.tools.values() 
            if tool.status == ToolStatus.ERROR
        ]
    
    def get_tool_status_summary(self) -> Dict[str, int]:
        """
        Get summary of tool statuses.
        
        Returns:
            Dictionary with counts for each status
        """
        summary = {
            "active": len(self.get_active_tools()),
            "inactive": len(self.get_inactive_tools()),
            "missing": len(self.get_missing_tools()),
            "error": len(self.get_error_tools())
        }
        return summary


# Global tools monitor instance
_tools_monitor = None

def get_tools_monitor() -> ToolsMonitor:
    """Get the global tools monitor instance."""
    global _tools_monitor
    if _tools_monitor is None:
        _tools_monitor = ToolsMonitor()
    return _tools_monitor