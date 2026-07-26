"""
Cloud Environments — Provider catalog and job config helpers.
"""

from pathlib import Path
from typing import Any

import yaml

# All environment types supported by Harbor (from EnvironmentType enum)
ENVIRONMENT_TYPES: dict[str, dict[str, str]] = {
    "docker": {
        "description": "Local Docker containers",
        "category": "Local",
        "setup": "Docker Desktop installed and running",
    },
    "daytona": {
        "description": "Daytona cloud development environments",
        "category": "Cloud",
        "setup": "Daytona account + API key (DAYTONA_API_KEY)",
    },
    "e2b": {
        "description": "E2B cloud sandboxes",
        "category": "Cloud",
        "setup": "E2B account + API key (E2B_API_KEY)",
    },
    "modal": {
        "description": "Modal serverless containers",
        "category": "Cloud",
        "setup": "Modal account + `modal token new`",
    },
    "runloop": {
        "description": "Runloop cloud sandboxes",
        "category": "Cloud",
        "setup": "Runloop account + API key",
    },
    "langsmith": {
        "description": "LangSmith evaluation sandboxes",
        "category": "Cloud",
        "setup": "LangSmith account + API key",
    },
    "ec2": {
        "description": "AWS EC2 instances",
        "category": "Cloud",
        "setup": "AWS credentials configured",
    },
    "gke": {
        "description": "Google Kubernetes Engine pods",
        "category": "Cloud",
        "setup": "GCP project + GKE cluster configured",
    },
    "ack": {
        "description": "Alibaba Cloud Container Service",
        "category": "Cloud",
        "setup": "Alibaba Cloud credentials configured",
    },
    "openshift": {
        "description": "Red Hat OpenShift pods",
        "category": "Cloud",
        "setup": "OpenShift cluster + kubeconfig",
    },
    "novita": {
        "description": "Novita AI cloud sandboxes",
        "category": "Cloud",
        "setup": "Novita account + API key",
    },
    "apple-container": {
        "description": "Apple containerization (macOS)",
        "category": "Local",
        "setup": "macOS with container support",
    },
    "singularity": {
        "description": "Singularity/Apptainer containers",
        "category": "Local/HPC",
        "setup": "Singularity/Apptainer installed",
    },
    "islo": {
        "description": "Islo cloud sandboxes",
        "category": "Cloud",
        "setup": "Islo account + API key",
    },
    "tensorlake": {
        "description": "TensorLake cloud environments",
        "category": "Cloud",
        "setup": "TensorLake account + API key",
    },
    "cwsandbox": {
        "description": "CW sandbox environments",
        "category": "Cloud",
        "setup": "CWSandbox account + API key",
    },
    "wandb": {
        "description": "Weights & Biases sandboxes",
        "category": "Cloud",
        "setup": "W&B account + API key (WANDB_API_KEY)",
    },
    "use-computer": {
        "description": "Desktop computer-use environments",
        "category": "Specialized",
        "setup": "Computer-use provider configured",
    },
    "cua-cloud": {
        "description": "Cloud computer-use environments",
        "category": "Cloud",
        "setup": "CUA cloud provider configured",
    },
    "blaxel": {
        "description": "Blaxel cloud sandboxes",
        "category": "Cloud",
        "setup": "Blaxel account + API key",
    },
    "opensandbox": {
        "description": "OpenSandbox cloud environments",
        "category": "Cloud",
        "setup": "OpenSandbox account + API key",
    },
    "beam": {
        "description": "Beam cloud containers",
        "category": "Cloud",
        "setup": "Beam account + API key",
    },
}


def get_job_configs() -> dict[str, dict[str, Any]]:
    """Return example job configs for Docker, Daytona, and Modal."""
    docker_config: dict[str, Any] = {
        "datasets": [{"name": "harbor-framework/hello-world"}],
        "agents": [{"name": "oracle"}],
        "environment": {"type": "docker", "delete": True},
        "n_concurrent_trials": 4,
        "quiet": False,
    }

    daytona_config: dict[str, Any] = {
        "datasets": [{"name": "harbor-framework/hello-world"}],
        "agents": [
            {
                "name": "claude-code",
                "model_name": "anthropic/claude-sonnet-4-5-20250929",
            }
        ],
        "environment": {"type": "daytona", "delete": True},
        "n_concurrent_trials": 32,
        "quiet": False,
    }

    modal_config: dict[str, Any] = {
        "datasets": [{"name": "harbor-framework/hello-world"}],
        "agents": [
            {
                "name": "claude-code",
                "model_name": "anthropic/claude-sonnet-4-5-20250929",
            }
        ],
        "environment": {"type": "modal", "delete": True},
        "n_concurrent_trials": 16,
        "quiet": False,
    }

    return {
        "docker-job.yaml": docker_config,
        "daytona-job.yaml": daytona_config,
        "modal-job.yaml": modal_config,
    }


def write_job_config(configs_dir: Path, filename: str, config: dict[str, Any]) -> None:
    """Write a single job config YAML file."""
    filepath = configs_dir / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
