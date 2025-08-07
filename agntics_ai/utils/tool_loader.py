"""
Tool configuration loader for security tools data.
"""
import json
import logging
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ToolLoader:
    """Loads and manages security tools configuration from JSON files."""
    
    def __init__(self, tools_directory: str = None):
        """
        Initialize the ToolLoader.
        
        Args:
            tools_directory: Path to directory containing tool JSON files
        """
        if tools_directory is None:
            # Default to data/tool directory relative to this file
            current_dir = Path(__file__).parent.parent
            tools_directory = current_dir / "data" / "tool"
        
        self.tools_directory = Path(tools_directory)
        self._tools_cache = {}
        self._load_tools()
    
    def _load_tools(self) -> None:
        """Load all tool configuration files from the directory."""
        if not self.tools_directory.exists():
            logger.warning(f"Tools directory not found: {self.tools_directory}")
            return
        
        for tool_file in self.tools_directory.glob("*.json"):
            try:
                with open(tool_file, 'r', encoding='utf-8') as f:
                    tool_data = json.load(f)
                
                # Extract customer/organization name from the data
                customer_name = self._extract_customer_name(tool_data)
                if customer_name:
                    self._tools_cache[customer_name.lower()] = {
                        'file': tool_file.name,
                        'data': tool_data
                    }
                    logger.info(f"Loaded tools for customer: {customer_name}")
                
            except Exception as e:
                logger.error(f"Failed to load tool file {tool_file}: {e}")
    
    def _extract_customer_name(self, tool_data: Any) -> Optional[str]:
        """Extract customer name from tool data structure."""
        if isinstance(tool_data, list) and tool_data:
            # Handle list format
            first_item = tool_data[0]
            if isinstance(first_item, dict):
                # Try to find customer info in objectMarking
                object_marking = first_item.get('data', {}).get('onBoarding', {}).get('objectMarking', [])
                if object_marking:
                    customer_info = object_marking[0].get('customer_info', {})
                    return customer_info.get('name', '')
        
        elif isinstance(tool_data, dict):
            # Handle dict format
            object_marking = tool_data.get('data', {}).get('onBoarding', {}).get('objectMarking', [])
            if object_marking:
                customer_info = object_marking[0].get('customer_info', {})
                return customer_info.get('name', '')
        
        return None
    
    def get_tools_for_customer(self, customer_name: str) -> Optional[Dict[str, Any]]:
        """
        Get tools configuration for a specific customer.
        
        Args:
            customer_name: Name of the customer/organization
            
        Returns:
            Dictionary containing tools data or None if not found
        """
        return self._tools_cache.get(customer_name.lower())
    
    def get_current_technologies(self, customer_name: str) -> List[Dict[str, str]]:
        """
        Get list of current security technologies for a customer.
        
        Args:
            customer_name: Name of the customer/organization
            
        Returns:
            List of technology dictionaries with 'technology' and 'product' keys
        """
        tools_data = self.get_tools_for_customer(customer_name)
        if not tools_data:
            return []
        
        data = tools_data['data']
        if isinstance(data, list) and data:
            onboarding = data[0].get('data', {}).get('onBoarding', {})
        else:
            onboarding = data.get('data', {}).get('onBoarding', {})
        
        return onboarding.get('currentTechnologies', [])
    
    def get_monitor_assets(self, customer_name: str) -> List[Dict[str, Any]]:
        """
        Get list of monitored assets for a customer.
        
        Args:
            customer_name: Name of the customer/organization
            
        Returns:
            List of asset dictionaries
        """
        tools_data = self.get_tools_for_customer(customer_name)
        if not tools_data:
            return []
        
        data = tools_data['data']
        if isinstance(data, list) and data:
            onboarding = data[0].get('data', {}).get('onBoarding', {})
        else:
            onboarding = data.get('data', {}).get('onBoarding', {})
        
        return onboarding.get('monitorAssets', [])
    
    def find_relevant_tools(self, attack_technique: str, customer_name: str) -> List[Dict[str, Any]]:
        """
        Find tools relevant to a specific MITRE ATT&CK technique.
        
        Args:
            attack_technique: MITRE ATT&CK technique ID (e.g., "T1059.001")
            customer_name: Name of the customer/organization
            
        Returns:
            List of relevant tools and assets
        """
        current_tech = self.get_current_technologies(customer_name)
        monitor_assets = self.get_monitor_assets(customer_name)
        
        relevant_tools = []
        
        # Map common MITRE techniques to relevant tool types
        technique_mapping = {
            'T1059': ['EDR', 'ANTIVIRUS', 'ENDPOINT_PROTECTION'],  # Command and Scripting Interpreter
            'T1548': ['EDR', 'PAM', 'ENDPOINT_PROTECTION'],        # Abuse Elevation Control
            'T1112': ['EDR', 'ENDPOINT_PROTECTION'],               # Modify Registry
            'T1055': ['EDR', 'ANTIVIRUS'],                         # Process Injection
            'T1083': ['EDR', 'ENDPOINT_PROTECTION'],               # File and Directory Discovery
            'T1135': ['NIDS_NIPS', 'NDR'],                         # Network Share Discovery
            'T1016': ['NIDS_NIPS', 'NDR', 'NETWORKMONITORING'],   # System Network Configuration
            'T1021': ['NIDS_NIPS', 'NAC', 'PAM'],                 # Remote Services
            'T1190': ['WAF', 'NIDS_NIPS', 'VULNERABILITYASSESSMENT'], # Exploit Public-Facing
            'T1566': ['EMAILGATEWAY', 'SANDBOX'],                 # Phishing
        }
        
        # Extract technique ID (remove sub-technique if present)
        base_technique = attack_technique.split('.')[0] if '.' in attack_technique else attack_technique
        relevant_tech_types = technique_mapping.get(base_technique, [])
        
        # Find matching tools
        for tech in current_tech:
            if tech.get('technology', '').upper() in relevant_tech_types:
                relevant_tools.append({
                    'type': 'security_technology',
                    'technology': tech.get('technology'),
                    'product': tech.get('product'),
                    'purpose': f'Detection and prevention of {attack_technique}'
                })
        
        # Find relevant monitoring assets
        for asset in monitor_assets:
            asset_purpose = asset.get('purpose', '').lower()
            if any(tech_type.lower().replace('_', ' ') in asset_purpose or 
                   asset_purpose in tech_type.lower().replace('_', ' ') 
                   for tech_type in relevant_tech_types):
                relevant_tools.append({
                    'type': 'monitoring_asset',
                    'purpose': asset.get('purpose'),
                    'product': asset.get('productName'),
                    'hostname': asset.get('hostname'),
                    'ip_address': asset.get('ipAddress'),
                    'version': asset.get('version'),
                    'in_production': asset.get('inProduction')
                })
        
        return relevant_tools
    
    def get_available_customers(self) -> List[str]:
        """Get list of available customer names."""
        return list(self._tools_cache.keys())


# Global instance
_tool_loader = None

def get_tool_loader(tools_directory: str = None) -> ToolLoader:
    """Get the global ToolLoader instance."""
    global _tool_loader
    if _tool_loader is None:
        _tool_loader = ToolLoader(tools_directory)
    return _tool_loader