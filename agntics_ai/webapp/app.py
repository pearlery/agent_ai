"""
Flask web application for displaying cybersecurity analysis reports.
"""
import asyncio
import json
import logging
import threading
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from flask import Flask, render_template, jsonify, Response, request
from nats.aio.client import Client as NATS

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from ..utils.nats_handler import NATSHandler

logger = logging.getLogger(__name__)

# Global variables for storing latest reports and NATS handler
latest_reports = []
nats_handler = None
background_task = None
app_config = None
control_agent_url = None
latest_output_data = {}
connected_clients = []


def create_app(config_path: Optional[str] = None) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config_path: Path to configuration file (optional)
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    if not config_path:
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    
    with open(config_path, 'r') as f:
        global app_config, control_agent_url
        app_config = yaml.safe_load(f)
        
        # Set Control Agent URL
        import os
        control_agent_url = os.getenv('CONTROL_AGENT_URL', 'http://localhost:8000')
    
    # Setup logging
    log_config = app_config.get('logging', {})
    logging.basicConfig(
        level=getattr(logging, log_config.get('level', 'INFO')),
        format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Configure Flask
    webapp_config = app_config.get('webapp', {})
    app.config['DEBUG'] = webapp_config.get('debug', False)
    
    return app


app = create_app()


class NATSBackgroundListener:
    """
    Background listener for NATS messages in a separate thread.
    """
    
    def __init__(self, nats_config: Dict[str, Any]):
        self.nats_config = nats_config
        self.running = False
        self.loop = None
        
    def start(self):
        """Start the background listener thread."""
        if self.running:
            return
        
        self.thread = threading.Thread(target=self._run_thread, daemon=True)
        self.thread.start()
        logger.info("NATS background listener started")
    
    def stop(self):
        """Stop the background listener."""
        self.running = False
        if self.loop:
            self.loop.call_soon_threadsafe(self._stop_loop)
    
    def _run_thread(self):
        """Thread entry point for running the asyncio event loop."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._listen_for_reports())
    
    def _stop_loop(self):
        """Stop the asyncio event loop."""
        for task in asyncio.all_tasks(self.loop):
            task.cancel()
        self.loop.stop()
    
    async def _listen_for_reports(self):
        """
        Listen for reports on the NATS output subject.
        """
        global latest_reports, nats_handler
        
        try:
            nats_handler = NATSHandler(self.nats_config)
            await nats_handler.connect()
            
            # Subscribe to output subject
            psub = await nats_handler.subscribe_pull(
                subject=nats_handler.subjects['output'],
                durable_name='webapp_consumer'
            )
            
            self.running = True
            logger.info("Background listener subscribed to output subject")
            
            while self.running:
                try:
                    # Fetch messages with timeout
                    msgs = await psub.fetch(batch=1, timeout=5.0)
                    
                    for msg in msgs:
                        try:
                            # Decode and process the message
                            payload = json.loads(msg.data.decode('utf-8'))
                            
                            # Add timestamp for sorting
                            payload['web_received_at'] = asyncio.get_event_loop().time()
                            
                            # Add to latest reports (keep only last 10)
                            latest_reports.append(payload)
                            if len(latest_reports) > 10:
                                latest_reports.pop(0)
                            
                            logger.info(f"Received report: {payload.get('alert_id', 'unknown')}")
                            
                            # Acknowledge the message
                            await msg.ack()
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to decode message: {e}")
                            await msg.ack()
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                
                except asyncio.TimeoutError:
                    # No messages available, continue polling
                    continue
                except Exception as e:
                    logger.error(f"Error in background listener: {e}")
                    await asyncio.sleep(1)
        
        except Exception as e:
            logger.error(f"Background listener failed to start: {e}")
        finally:
            if nats_handler:
                await nats_handler.close()


# Global background listener instance
background_listener = None


@app.route("/")
def index():
    """
    Main page displaying the latest incident report.
    """
    global latest_reports
    
    # Get the most recent report
    latest_report = None
    if latest_reports:
        # Sort by received timestamp and get the latest
        latest_reports.sort(key=lambda x: x.get('web_received_at', 0), reverse=True)
        latest_report = latest_reports[0]
    
    # Extract data for template
    if latest_report:
        report_data = {
            'alert_id': latest_report.get('alert_id', 'Unknown'),
            'incident_report': latest_report.get('incident_report', 'No report available'),
            'mitre_analysis': latest_report.get('mitre_analysis', {}),
            'raw_log_data': latest_report.get('raw_log_data', {}),
            'processing_timestamp': latest_report.get('processing_timestamp', 0)
        }
    else:
        report_data = {
            'alert_id': 'No alerts processed yet',
            'incident_report': 'No reports available. Please run the agents to generate incident reports.',
            'mitre_analysis': {},
            'raw_log_data': {},
            'processing_timestamp': 0
        }
    
    from datetime import datetime
    report_data['current_time'] = datetime.now()
    return render_template('index.html', **report_data)


@app.route("/api/reports")
def api_reports():
    """
    API endpoint to get all available reports as JSON.
    """
    global latest_reports
    
    # Sort reports by received timestamp (newest first)
    sorted_reports = sorted(latest_reports, key=lambda x: x.get('web_received_at', 0), reverse=True)
    
    return jsonify({
        'count': len(sorted_reports),
        'reports': sorted_reports
    })


@app.route("/api/latest")
def api_latest():
    """
    API endpoint to get the latest report as JSON.
    """
    global latest_reports
    
    if latest_reports:
        # Sort by received timestamp and get the latest
        latest_reports.sort(key=lambda x: x.get('web_received_at', 0), reverse=True)
        return jsonify(latest_reports[0])
    else:
        return jsonify({'error': 'No reports available'})


@app.route("/health")
def health():
    """
    Health check endpoint.
    """
    # Check Control Agent health
    control_agent_healthy = False
    try:
        response = requests.get(f'{control_agent_url}/health', timeout=2)
        control_agent_healthy = response.status_code == 200
    except:
        control_agent_healthy = False
    
    return jsonify({
        'status': 'healthy',
        'reports_count': len(latest_reports),
        'nats_connected': nats_handler is not None,
        'control_agent_healthy': control_agent_healthy,
        'control_agent_url': control_agent_url
    })


@app.route("/api/output")
def api_output():
    """
    Get current output.json data.
    """
    try:
        output_file = Path(__file__).parent.parent.parent / "output.json"
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        else:
            return jsonify({'error': 'No output file found'})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route("/api/control/status")
def control_status():
    """
    Get Control Agent status via API call.
    """
    try:
        response = requests.get(f'{control_agent_url}/status', timeout=5)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': f'Control Agent returned {response.status_code}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/control/start", methods=['POST'])
def control_start():
    """
    Start processing via Control Agent.
    """
    try:
        data = request.json or {}
        response = requests.post(f'{control_agent_url}/start', json=data, timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': f'Control Agent returned {response.status_code}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/events")
def events():
    """
    Server-Sent Events endpoint for real-time updates.
    """
    def event_generator():
        global latest_output_data, connected_clients
        
        # Add client to connected clients list
        client_id = f"client_{int(time.time() * 1000)}"
        connected_clients.append(client_id)
        
        try:
            # Send initial data
            output_file = Path(__file__).parent.parent.parent / "output.json"
            if output_file.exists():
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    yield f"data: {json.dumps({'type': 'initial', 'data': data})}\n\n"
                except:
                    pass
            
            # Send periodic updates
            last_modified = 0
            while True:
                try:
                    # Check if output.json has been modified
                    if output_file.exists():
                        current_modified = output_file.stat().st_mtime
                        if current_modified > last_modified:
                            last_modified = current_modified
                            with open(output_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            yield f"data: {json.dumps({'type': 'update', 'data': data})}\n\n"
                    
                    # Send heartbeat
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': time.time()})}\n\n"
                    
                    time.sleep(3)  # Update every 3 seconds
                    
                except Exception as e:
                    logger.error(f"Error in event generator: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Event generator error: {e}")
        finally:
            # Remove client from connected clients
            if client_id in connected_clients:
                connected_clients.remove(client_id)
    
    return Response(
        event_generator(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )


@app.route("/dashboard")
def dashboard():
    """
    Real-time dashboard page.
    """
    return render_template('dashboard.html')


@app.route("/api/system/info")
def system_info():
    """
    Get comprehensive system information.
    """
    try:
        # Get Control Agent status
        control_status_data = {}
        try:
            response = requests.get(f'{control_agent_url}/status', timeout=3)
            if response.status_code == 200:
                control_status_data = response.json()
        except:
            control_status_data = {'error': 'Control Agent unavailable'}
        
        # Get output data
        output_data = {}
        try:
            output_file = Path(__file__).parent.parent.parent / "output.json"
            if output_file.exists():
                with open(output_file, 'r', encoding='utf-8') as f:
                    output_data = json.load(f)
        except:
            output_data = {'error': 'Output file unavailable'}
        
        return jsonify({
            'webapp': {
                'status': 'running',
                'connected_clients': len(connected_clients),
                'reports_cached': len(latest_reports)
            },
            'control_agent': control_status_data,
            'nats': {
                'connected': nats_handler is not None,
                'handler_status': 'active' if nats_handler else 'inactive'
            },
            'output': {
                'available': bool(output_data and 'error' not in output_data),
                'sections': len(output_data) if 'error' not in output_data else 0
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def start_background_listener():
    """Start the background NATS listener if not already running."""
    global background_listener, app_config
    
    if not background_listener:
        background_listener = NATSBackgroundListener(app_config['nats'])
        background_listener.start()


def stop_background_listener():
    """Stop the background NATS listener."""
    global background_listener
    
    if background_listener:
        background_listener.stop()
        background_listener = None


# Flask lifecycle hooks - Updated for Flask 3.x
def before_first_request():
    """Initialize background services before first request."""
    start_background_listener()

# Register the before_first_request function for Flask 3.x
@app.before_request
def init_background():
    """Initialize background services on first request."""
    if not hasattr(app, '_background_started'):
        app._background_started = True
        before_first_request()


def run_webapp(host: str = None, port: int = None, debug: bool = None):
    """
    Run the Flask web application.
    
    Args:
        host: Host to bind to (default from config)
        port: Port to bind to (default from config) 
        debug: Debug mode (default from config)
    """
    global app_config
    
    # Get configuration
    webapp_config = app_config.get('webapp', {})
    
    # Use provided values or fall back to config
    host = host or webapp_config.get('host', '0.0.0.0')
    port = port or webapp_config.get('port', 5000)
    debug = debug if debug is not None else webapp_config.get('debug', False)
    
    logger.info(f"Starting web application on {host}:{port}")
    
    try:
        # Start background listener before running the app
        start_background_listener()
        
        # Run the Flask application
        app.run(host=host, port=port, debug=debug, use_reloader=False)
        
    except KeyboardInterrupt:
        logger.info("Web application interrupted by user")
    finally:
        stop_background_listener()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Agntics AI Web Application')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    run_webapp(host=args.host, port=args.port, debug=args.debug)