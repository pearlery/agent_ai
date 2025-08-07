import ipaddress
import re
from typing import List, Dict, Optional, Union, Any


def expand_ip_ranges(ip_field: str) -> List[ipaddress._BaseNetwork]:
    ip_field = ip_field.replace(" ", "").replace("–", "-")
    parts = re.split(r",", ip_field)
    result = []

    for part in parts:
        if "-" in part:
            match = re.match(r"(\d+\.\d+)\.(\d+)-(\d+)\.(\d+)(/\d+)?", part)
            if match:
                base1, start, end, base2, cidr = match.groups()
                cidr = cidr or "/24"
                for i in range(int(start), int(end) + 1):
                    try:
                        net = ipaddress.ip_network(f"{base1}.{i}.{base2}{cidr}", strict=False)
                        result.append(net)
                    except Exception:
                        continue
        else:
            try:
                net = ipaddress.ip_network(part, strict=False)
                result.append(net)
            except Exception:
                continue
    return result


def find_in_network_infos(input_ip: str, network_infos: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    ip_obj = ipaddress.ip_address(input_ip)
    best_match = None
    longest_prefix = -1

    for net_info in network_infos:
        ip_field = net_info.get("ip", "")
        networks = expand_ip_ranges(ip_field)

        for net in networks:
            if ip_obj in net and net.prefixlen > longest_prefix:
                best_match = net_info
                longest_prefix = net.prefixlen

    return best_match


def find_in_monitor_assets(input_ip: str, monitor_assets: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    for asset in monitor_assets:
        ip_addr = asset.get("ipAddress")
        if not ip_addr:
            continue
        try:
            if ipaddress.ip_address(input_ip) == ipaddress.ip_address(ip_addr):
                return asset
        except Exception:
            continue
    return None


async def search_ip_context(input_ip: str, onboarding_data: Dict[str, any]) -> Dict[str, Union[str, Dict]]:
    monitor_assets = onboarding_data["monitorAssets"]
    network_infos = onboarding_data["networkInfos"]

    match_asset = find_in_monitor_assets(input_ip, monitor_assets)
    match_net = find_in_network_infos(input_ip, network_infos)

    result = {}

    if match_asset:
        result["monitorAsset"] = match_asset

    if match_net:
        result["networkInfo"] = match_net

    if not result:
        result["message"] = "No match found"

    return result



async def search_multiple_ip_contexts(src_ips: List[str], onboarding_data: Dict[str, Any]) -> List[Dict[str, Union[str, Dict]]]:
    results = []
    for ip in src_ips:
        try:
            match_result = await search_ip_context(ip, onboarding_data)
            match_result["ip"] = ip
            results.append(match_result)
        except Exception as e:
            results.append({"ip": ip, "error": str(e)})
    return results


