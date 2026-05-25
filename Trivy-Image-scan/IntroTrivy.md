# Workshop: Security Scanning with Trivy

## 1. What is Trivy?
**Trivy** (`tri` pronounced like **trigger**, `vy` pronounced like **envy**) is a comprehensive and versatile open-source security scanner. Developed by Aqua Security, it is designed to be fast, stateless, and easy to integrate into CI/CD pipelines.

It is currently the most popular tool for finding vulnerabilities in container images and infrastructure-as-code (IaC).

---

## 2. Why is Trivy Used?
In modern cloud-native development, security shouldn't be a final step. Trivy is used to shift security "left" (earlier in the development process) for the following reasons:

* **Ease of Use:** It works out of the box with zero configuration. No database setup is required as it downloads its own vulnerability data.
* **High Accuracy:** It has low false-positive rates compared to other scanners.
* **Speed:** It can scan a container image in seconds, making it ideal for CI/CD.
* **CI/CD Friendly:** It supports multiple output formats (Table, JSON, HTML) and can exit with specific error codes to "break the build" if critical issues are found.



---

## 3. What Does Trivy Scan? (Primary Targets)
Trivy is not limited to just one area; it scans across the entire application stack:

### A. Container Images
Scans the OS packages (e.g., Alpine, Ubuntu) and language-specific dependencies (e.g., Maven/Java, NPM/Node) inside your Docker images.

### B. Filesystems & Git Repositories
Scans local code folders or remote Git repos to find vulnerabilities in your source code dependencies before you even build an image.

### C. Infrastructure as Code (IaC)
Finds misconfigurations in configuration files such as:
* **Dockerfiles** (e.g., running as root user).
* **Kubernetes** manifests.
* **Terraform** scripts.

### D. Secrets
Detects hardcoded "secrets" like AWS keys, passwords, and API tokens that might have been accidentally committed to your code.



---

## 4. Basic Command Syntax
During this workshop, we will primarily use the following structure:

```bash
# Scan a Docker Image
trivy image [IMAGE_NAME]

# Scan a local folder (Filesystem)
trivy fs /path/to/project


# Filter by Severity
trivy image --severity HIGH,CRITICAL [IMAGE_NAME]

trivy fs --severity HIGH,CRITICAL /path/to/project

```