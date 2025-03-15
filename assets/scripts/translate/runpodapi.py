import http.client
import json
from typing import Dict, List, Optional, Any
import time

class RunPodClient:
    """A comprehensive utility class for interacting with the RunPod API."""
    
    def __init__(self, api_key: str, base_url: str = "rest.runpod.io", api_version: str = "v1"):
        """
        Initialize the RunPod client.
        
        Args:
            api_key (str): Your RunPod API key
            base_url (str): Base URL for the RunPod API (default: rest.runpod.io)
            api_version (str): API version to use (default: v1)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.api_version = api_version
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, payload: Optional[Dict] = None) -> Dict:
        """
        Make an HTTP request to the RunPod API.
        
        Args:
            method (str): HTTP method (GET, POST, PATCH, DELETE)
            endpoint (str): API endpoint
            payload (Optional[Dict]): Request payload for POST/PATCH requests
            
        Returns:
            Dict: Response data
            
        Raises:
            Exception: If request fails
            
        # Output: Varies based on endpoint, typically JSON object or empty dict for DELETE/POST actions
        """
        conn = http.client.HTTPSConnection(self.base_url)
        url = f"/{self.api_version}{endpoint}"
        
        try:
            if payload:
                conn.request(method, url, body=json.dumps(payload), headers=self.headers)
            else:
                conn.request(method, url, headers=self.headers)
                
            res = conn.getresponse()
            data = res.read().decode("utf-8")
            
            if res.status not in (200, 201):
                raise Exception(f"Request failed with status {res.status}: {data}")
                
            return json.loads(data) if data else {}
        finally:
            conn.close()

    # Pod Management Methods
    def create_pod(self, pod_config: Dict) -> Dict:
        """Create a new Pod with the specified configuration.
        
        # Output: Dict containing pod details including 'id', 'name', 'image', 'desiredStatus', etc.
        # Example keys: 'id', 'adjustedCostPerHr', 'containerDiskInGb', 'gpu', 'machine', 'ports'
        """
        return self._make_request("POST", "/pods", pod_config)

    def create_pod_from_template(self, template_id: str, name: str = "Pod from template",
                               additional_config: Optional[Dict] = None) -> Dict:
        """Create a new Pod based on a template.
        
        # Output: Dict containing pod details inherited from template plus overrides
        # Example keys: 'id', 'templateId', 'name', 'image', 'ports', 'env'
        """
        pod_config = {
            "templateId": template_id,
            "name": name
        }
        if additional_config:
            pod_config.update(additional_config)
        return self.create_pod(pod_config)

    def get_pods(self, filters: Optional[Dict] = None) -> List[Dict]:
        """List all Pods with optional filters.
        
        # Output: List of Dict, each containing pod details
        # Example keys per pod: 'id', 'name', 'desiredStatus', 'image', 'gpu', 'ports'
        """
        endpoint = "/pods"
        if filters:
            query_params = "&".join(f"{k}={v}" for k, v in filters.items())
            endpoint += f"?{query_params}"
        return self._make_request("GET", endpoint)

    def get_pod(self, pod_id: str, include_details: bool = False) -> Dict:
        """Get details for a specific Pod.
        
        # Output: Dict containing detailed pod information
        # Example keys: 'id', 'name', 'desiredStatus', 'machine', 'networkVolume', 'savingsPlans', 'template'
        # Additional keys with include_details=True: 'machine', 'networkVolume', 'savingsPlans'
        """
        endpoint = f"/pods/{pod_id}"
        if include_details:
            endpoint += "?includeMachine=true&includeNetworkVolume=true&includeSavingsPlans=true&includeTemplate=true"
        return self._make_request("GET", endpoint)

    def update_pod(self, pod_id: str, pod_config: Dict) -> Dict:
        """Update an existing Pod.
        
        # Output: Dict containing updated pod details
        # Example keys: 'id', 'name', 'containerDiskInGb', 'env', 'imageName', 'ports'
        """
        return self._make_request("PATCH", f"/pods/{pod_id}", pod_config)

    def delete_pod(self, pod_id: str) -> None:
        """Delete a Pod.
        
        # Output: Empty dict (no content on successful deletion)
        """
        self._make_request("DELETE", f"/pods/{pod_id}")

    def start_pod(self, pod_id: str) -> None:
        """Start or resume a Pod.
        
        # Output: Empty dict (no content on successful start)
        """
        self._make_request("POST", f"/pods/{pod_id}/start")

    def stop_pod(self, pod_id: str) -> None:
        """Stop a Pod.
        
        # Output: Empty dict (no content on successful stop)
        """
        self._make_request("POST", f"/pods/{pod_id}/stop")

    def reset_pod(self, pod_id: str) -> None:
        """Reset a Pod.
        
        # Output: Empty dict (no content on successful reset)
        """
        self._make_request("POST", f"/pods/{pod_id}/reset")

    # Template Management Methods
    def create_template(self, template_config: Dict) -> Dict:
        """Create a new template.
        
        # Output: Dict containing template details
        # Example keys: 'id', 'name', 'imageName', 'containerDiskInGb', 'env', 'ports'
        """
        return self._make_request("POST", "/templates", template_config)

    def get_templates(self) -> List[Dict]:
        """List all templates.
        
        # Output: List of Dict, each containing template details
        # Example keys per template: 'id', 'name', 'imageName', 'isPublic', 'isServerless', 'ports'
        """
        return self._make_request("GET", "/templates")

    def get_template(self, template_id: str) -> Dict:
        """Get details for a specific template.
        
        # Output: Dict containing detailed template information
        # Example keys: 'id', 'name', 'imageName', 'containerDiskInGb', 'env', 'ports', 'readme'
        """
        return self._make_request("GET", f"/templates/{template_id}")

    def update_template(self, template_id: str, template_config: Dict) -> Dict:
        """Update an existing template.
        
        # Output: Dict containing updated template details
        # Example keys: 'id', 'name', 'imageName', 'containerDiskInGb', 'env', 'ports'
        """
        return self._make_request("PATCH", f"/templates/{template_id}", template_config)

    def delete_template(self, template_id: str) -> None:
        """Delete a template.
        
        # Output: Empty dict (no content on successful deletion)
        """
        self._make_request("DELETE", f"/templates/{template_id}")

    # Network Volume Management Methods
    def create_network_volume(self, volume_config: Dict) -> Dict:
        """Create a new network volume.
        
        # Output: Dict containing network volume details
        # Example keys: 'id', 'name', 'size', 'dataCenterId'
        """
        return self._make_request("POST", "/networkvolumes", volume_config)

    def get_network_volumes(self) -> List[Dict]:
        """List all network volumes.
        
        # Output: List of Dict, each containing network volume details
        # Example keys per volume: 'id', 'name', 'size', 'dataCenterId'
        """
        return self._make_request("GET", "/networkvolumes")

    def get_network_volume(self, volume_id: str) -> Dict:
        """Get details for a specific network volume.
        
        # Output: Dict containing detailed network volume information
        # Example keys: 'id', 'name', 'size', 'dataCenterId'
        """
        return self._make_request("GET", f"/networkvolumes/{volume_id}")

    def update_network_volume(self, volume_id: str, volume_config: Dict) -> Dict:
        """Update an existing network volume.
        
        # Output: Dict containing updated network volume details
        # Example keys: 'id', 'name', 'size', 'dataCenterId'
        """
        return self._make_request("PATCH", f"/networkvolumes/{volume_id}", volume_config)

    def delete_network_volume(self, volume_id: str) -> None:
        """Delete a network volume.
        
        # Output: Empty dict (no content on successful deletion)
        """
        self._make_request("DELETE", f"/networkvolumes/{volume_id}")

    # Endpoint Management Methods
    def create_endpoint(self, endpoint_config: Dict) -> Dict:
        """Create a new serverless endpoint.
        
        # Output: Dict containing endpoint details
        # Example keys: (specific keys depend on endpoint configuration, typically includes 'id')
        """
        return self._make_request("POST", "/endpoints", endpoint_config)

    def get_endpoints(self) -> List[Dict]:
        """List all endpoints.
        
        # Output: List of Dict, each containing endpoint details
        # Example keys per endpoint: (specific keys depend on endpoint type, typically includes 'id')
        """
        return self._make_request("GET", "/endpoints")

    def get_endpoint(self, endpoint_id: str) -> Dict:
        """Get details for a specific endpoint.
        
        # Output: Dict containing detailed endpoint information
        # Example keys: (specific keys depend on endpoint type, typically includes 'id')
        """
        return self._make_request("GET", f"/endpoints/{endpoint_id}")

    def update_endpoint(self, endpoint_id: str, endpoint_config: Dict) -> Dict:
        """Update an existing endpoint.
        
        # Output: Dict containing updated endpoint details
        # Example keys: (specific keys depend on endpoint type, typically includes 'id')
        """
        return self._make_request("PATCH", f"/endpoints/{endpoint_id}", endpoint_config)

    def delete_endpoint(self, endpoint_id: str) -> None:
        """Delete an endpoint.
        
        # Output: Empty dict (no content on successful deletion)
        """
        self._make_request("DELETE", f"/endpoints/{endpoint_id}")

# Example usage
if __name__ == "__main__":
    # Initialize client
    client = RunPodClient(api_key="xxxxx")
    
    try:
        # Step 1: Get or create a template
        print("Fetching available templates...")
        templates = client.get_templates()
        
        if not templates:
            print("No templates available, creating a new one...")
            template_config = {
                "name": "Default PyTorch Template",
                "imageName": "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
                "containerDiskInGb": 50,
                "env": {"MY_ENV_VAR": "default_value"},
                "ports": ["8888/http", "22/tcp"],
                "isServerless": False,
                "isPublic": False
            }
            new_template = client.create_template(template_config)
            template_id = new_template["id"]
            template_name = new_template["name"]
            print(f"Created new template: {template_name} (ID: {template_id})")
        else:
            # Use the first template if available
            template_id = templates[0]["id"]
            template_name = templates[0]["name"]
            print(f"Using existing template: {template_name} (ID: {template_id})")

        # Step 2: Configure and create the Pod
        pod_config = {
            "gpuCount": 1,
            "containerDiskInGb": 100,
            "ports": ["8888/http", "22/tcp"],
            "imageName": "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
            "volumeInGb": 50,
            "env": {"MY_ENV_VAR": "test_value"},
            "supportPublicIp": True
        }
        
        print("Creating Pod from template...")
        pod = client.create_pod_from_template(
            template_id=template_id,
            name="My Test Pod",
            additional_config=pod_config
        )
        pod_id = pod["id"]
        print(f"Pod created successfully with ID: {pod_id}")

        # Step 3: Start the Pod
        print("Starting Pod...")
        client.start_pod(pod_id)

        # Step 4: Monitor Pod status until running
        max_attempts = 80
        attempt = 1
        while attempt <= max_attempts:
            pod_details = client.get_pod(pod_id, include_details=True)
            status = pod_details.get("desiredStatus", "UNKNOWN")
            print(f"Attempt {attempt}/{max_attempts}: Pod status - {status}")
            
            if status == "RUNNING":
                print("Pod is now running!")
                print(f"Public IP: {pod_details.get('publicIp', 'Not available')}")
                print(f"Ports: {pod_details.get('ports', [])}")
                break
                
            time.sleep(10)  # Wait 10 seconds between checks
            attempt += 1
        
        if attempt > max_attempts:
            print("Pod failed to start within timeout period")

        # Step 5: Display detailed Pod information
        print("\nFull Pod Details:")
        print(json.dumps(pod_details, indent=2))

        # Step 6: Clean up (stop and delete the Pod)
        print("\nCleaning up...")
        client.stop_pod(pod_id)
        print("Pod stopped")
        
        # Wait briefly to ensure stop completes
        time.sleep(5)
        
        client.delete_pod(pod_id)
        print("Pod deleted successfully")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        # Attempt cleanup if pod_id exists
        if 'pod_id' in locals():
            try:
                client.stop_pod(pod_id)
                client.delete_pod(pod_id)
                print("Cleanup completed despite error")
            except:
                print("Cleanup failed")