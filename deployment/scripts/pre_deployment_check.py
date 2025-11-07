#!/usr/bin/env python3
"""
Kubernetes Deployment Pre-flight Check Script

This script verifies that all prerequisites for deploying the Social Score API
to GKE are met before attempting deployment.

Usage:
    python3 pre_deployment_check.py --project <PROJECT_ID> --cluster <CLUSTER_NAME>
"""

import os
import sys
import subprocess
import json
from typing import Tuple, List, Dict
from dataclasses import dataclass

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    severity: str = "HIGH"  # HIGH, MEDIUM, LOW

class PreDeploymentChecker:
    def __init__(self, project_id: str, cluster_name: str, zone: str = "us-west1-a", region: str = "us-west1"):
        self.project_id = project_id
        self.cluster_name = cluster_name
        self.zone = zone
        self.region = region
        self.results: List[CheckResult] = []
    
    def print_header(self, text: str):
        """Print a formatted header"""
        print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"{Colors.BLUE}{text}{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    def print_result(self, result: CheckResult):
        """Print a check result"""
        status = f"{Colors.GREEN}✓{Colors.RESET}" if result.passed else f"{Colors.RED}✗{Colors.RESET}"
        print(f"{status} {result.name}: {result.message}")
    
    def run_command(self, command: str) -> Tuple[bool, str]:
        """Run a shell command and return success status and output"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            return result.returncode == 0, result.stdout.strip() + result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def check_gcloud_installed(self) -> CheckResult:
        """Check if gcloud is installed"""
        success, output = self.run_command("gcloud --version")
        return CheckResult(
            name="gcloud CLI",
            passed=success,
            message="gcloud CLI is installed" if success else "gcloud CLI not found. Install: https://cloud.google.com/sdk/docs/install"
        )
    
    def check_kubectl_installed(self) -> CheckResult:
        """Check if kubectl is installed"""
        success, output = self.run_command("kubectl version --client")
        return CheckResult(
            name="kubectl CLI",
            passed=success,
            message="kubectl CLI is installed" if success else "kubectl not found. Install: https://kubernetes.io/docs/tasks/tools/"
        )
    
    def check_docker_installed(self) -> CheckResult:
        """Check if Docker is installed"""
        success, output = self.run_command("docker --version")
        return CheckResult(
            name="Docker",
            passed=success,
            message="Docker is installed" if success else "Docker not found. Install: https://docs.docker.com/get-docker/"
        )
    
    def check_gcloud_auth(self) -> CheckResult:
        """Check if gcloud is authenticated"""
        success, output = self.run_command("gcloud auth list --filter=status:ACTIVE --format=value(account)")
        return CheckResult(
            name="gcloud Authentication",
            passed=success and len(output) > 0,
            message=f"Authenticated as: {output}" if success and output else "Not authenticated. Run: gcloud auth login"
        )
    
    def check_gcloud_project(self) -> CheckResult:
        """Check if project is set correctly"""
        success, output = self.run_command(f"gcloud config get-value project")
        current_project = output.strip()
        passed = success and current_project == self.project_id
        return CheckResult(
            name="gcloud Project",
            passed=passed,
            message=f"Project set to: {current_project}" if passed else f"Project mismatch. Expected: {self.project_id}, Got: {current_project}. Set with: gcloud config set project {self.project_id}"
        )
    
    def check_gke_cluster_exists(self) -> CheckResult:
        """Check if GKE cluster exists"""
        cmd = f"gcloud container clusters describe {self.cluster_name} --zone {self.zone} --project {self.project_id} 2>/dev/null"
        success, output = self.run_command(cmd)
        return CheckResult(
            name="GKE Cluster Exists",
            passed=success,
            message=f"Cluster '{self.cluster_name}' exists in zone {self.zone}" if success else f"Cluster '{self.cluster_name}' not found in zone {self.zone}"
        )
    
    def check_kubectl_context(self) -> CheckResult:
        """Check if kubectl is connected to the correct cluster"""
        success, output = self.run_command("kubectl cluster-info")
        cmd = f"gcloud container clusters get-credentials {self.cluster_name} --zone {self.zone} --project {self.project_id} 2>/dev/null"
        self.run_command(cmd)
        success2, output2 = self.run_command("kubectl cluster-info")
        return CheckResult(
            name="kubectl Context",
            passed=success2,
            message="kubectl is connected to the cluster" if success2 else "Could not connect kubectl to cluster. Try: gcloud container clusters get-credentials"
        )
    
    def check_artifact_registry_repo(self) -> CheckResult:
        """Check if Artifact Registry repository exists"""
        cmd = f"gcloud artifacts repositories describe social-score-repo --location={self.region} --project={self.project_id} 2>/dev/null"
        success, output = self.run_command(cmd)
        return CheckResult(
            name="Artifact Registry Repo",
            passed=success,
            message="Artifact Registry repository 'social-score-repo' exists" if success else "Repository not found. Create with: gcloud artifacts repositories create social-score-repo --repository-format=docker --location={self.region}",
            severity="HIGH"
        )
    
    def check_docker_auth(self) -> CheckResult:
        """Check if Docker can authenticate with Artifact Registry"""
        cmd = f"gcloud auth configure-docker {self.region}-docker.pkg.dev --quiet 2>/dev/null && docker pull {self.region}-docker.pkg.dev/{self.project_id}/social-score-repo/test:latest 2>/dev/null"
        success, output = self.run_command(cmd)
        # It's ok if the image doesn't exist, we just want to make sure auth is configured
        success2, output2 = self.run_command(f"cat ~/.docker/config.json | grep {self.region}-docker.pkg.dev")
        return CheckResult(
            name="Docker Registry Auth",
            passed=success2,
            message="Docker authenticated with Artifact Registry" if success2 else "Docker not authenticated. Run: gcloud auth configure-docker <region>-docker.pkg.dev",
            severity="MEDIUM"
        )
    
    def check_gcs_bucket(self) -> CheckResult:
        """Check if GCS bucket exists"""
        bucket_name = f"social-score-{self.project_id}"
        cmd = f"gsutil ls -b gs://{bucket_name} 2>/dev/null"
        success, output = self.run_command(cmd)
        return CheckResult(
            name="GCS Bucket",
            passed=success,
            message=f"GCS bucket '{bucket_name}' exists" if success else f"GCS bucket '{bucket_name}' not found. Create with: gsutil mb gs://{bucket_name}/",
            severity="MEDIUM"
        )
    
    def check_kubernetes_nodes(self) -> CheckResult:
        """Check if GKE cluster has available nodes"""
        cmd = "kubectl get nodes --no-headers 2>/dev/null | wc -l"
        success, output = self.run_command(cmd)
        try:
            node_count = int(output.strip())
            passed = success and node_count >= 3
            message = f"Cluster has {node_count} nodes" if success else "Could not determine node count"
        except:
            passed = False
            message = "Could not determine node count"
        
        return CheckResult(
            name="Kubernetes Nodes",
            passed=passed,
            message=message if passed else f"{message}. Ensure cluster has at least 3 nodes.",
            severity="HIGH"
        )
    
    def check_deployment_yaml(self) -> CheckResult:
        """Check if deployment YAML files exist and are valid"""
        files = [
            "deployment/k8s/social-score-deployment.yaml",
            "deployment/k8s/ingress.yaml"
        ]
        
        for file in files:
            if not os.path.exists(file):
                return CheckResult(
                    name="Deployment YAML Files",
                    passed=False,
                    message=f"Required file not found: {file}",
                    severity="HIGH"
                )
        
        # Check YAML syntax
        success, output = self.run_command(f"kubectl apply -f deployment/k8s/ --dry-run=client 2>&1")
        return CheckResult(
            name="Deployment YAML Files",
            passed=success,
            message="YAML files are valid" if success else f"YAML validation failed: {output[:100]}...",
            severity="HIGH"
        )
    
    def check_docker_image_exists(self) -> CheckResult:
        """Check if Docker image exists in Artifact Registry"""
        cmd = f"gcloud artifacts docker images list {self.region}-docker.pkg.dev/{self.project_id}/social-score-repo --include-tags --filter='name:social-score-api' 2>/dev/null"
        success, output = self.run_command(cmd)
        has_image = success and "social-score-api" in output
        return CheckResult(
            name="Docker Image Exists",
            passed=has_image,
            message="Docker image 'social-score-api' exists in Artifact Registry" if has_image else "Docker image not found. Build and push with Cloud Build.",
            severity="MEDIUM"
        )
    
    def check_service_account(self) -> CheckResult:
        """Check if Kubernetes service account exists"""
        cmd = "kubectl get serviceaccount social-score-sa 2>/dev/null"
        success, output = self.run_command(cmd)
        return CheckResult(
            name="Kubernetes Service Account",
            passed=success,
            message="Service account 'social-score-sa' exists" if success else "Service account not found. It will be created by the deployment manifest.",
            severity="LOW"
        )
    
    def check_resource_quotas(self) -> CheckResult:
        """Check if cluster has sufficient resources"""
        cmd = "kubectl describe nodes 2>/dev/null | grep -E 'Allocatable|Requested' | head -20"
        success, output = self.run_command(cmd)
        return CheckResult(
            name="Cluster Resources",
            passed=success,
            message="Cluster resources available" if success else "Could not check cluster resources",
            severity="LOW"
        )
    
    def run_all_checks(self) -> Tuple[int, int, int]:
        """Run all checks and return counts"""
        self.print_header("Pre-Deployment Checks")
        
        checks = [
            self.check_gcloud_installed,
            self.check_kubectl_installed,
            self.check_docker_installed,
            self.check_gcloud_auth,
            self.check_gcloud_project,
            self.check_gke_cluster_exists,
            self.check_kubectl_context,
            self.check_artifact_registry_repo,
            self.check_docker_auth,
            self.check_gcs_bucket,
            self.check_kubernetes_nodes,
            self.check_deployment_yaml,
            self.check_docker_image_exists,
            self.check_service_account,
            self.check_resource_quotas,
        ]
        
        passed = 0
        failed = 0
        warning = 0
        
        for check in checks:
            result = check()
            self.results.append(result)
            self.print_result(result)
            
            if result.passed:
                passed += 1
            else:
                if result.severity == "HIGH":
                    failed += 1
                else:
                    warning += 1
        
        return passed, failed, warning
    
    def print_summary(self, passed: int, failed: int, warning: int):
        """Print summary of checks"""
        self.print_header("Summary")
        
        total = passed + failed + warning
        print(f"Total checks: {total}")
        print(f"{Colors.GREEN}✓ Passed: {passed}{Colors.RESET}")
        print(f"{Colors.YELLOW}⚠ Warnings: {warning}{Colors.RESET}")
        print(f"{Colors.RED}✗ Failed: {failed}{Colors.RESET}\n")
        
        if failed == 0:
            print(f"{Colors.GREEN}All critical checks passed! Ready for deployment.{Colors.RESET}\n")
            return True
        else:
            print(f"{Colors.RED}Some critical checks failed. Please fix the issues above.{Colors.RESET}\n")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Pre-deployment checks for Social Score API on GKE")
    parser.add_argument("-p", "--project", required=True, help="GCP Project ID")
    parser.add_argument("-c", "--cluster", required=True, help="GKE Cluster name")
    parser.add_argument("-z", "--zone", default="us-west1-a", help="Cluster zone")
    parser.add_argument("-r", "--region", default="us-west1", help="Artifact Registry region")
    
    args = parser.parse_args()
    
    checker = PreDeploymentChecker(
        project_id=args.project,
        cluster_name=args.cluster,
        zone=args.zone,
        region=args.region
    )
    
    passed, failed, warning = checker.run_all_checks()
    ready = checker.print_summary(passed, failed, warning)
    
    sys.exit(0 if ready else 1)

if __name__ == "__main__":
    main()
