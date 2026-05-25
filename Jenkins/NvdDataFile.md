# OWASP Dependency-Check Data Migration Guide

This guide explains how to move the OWASP Dependency-Check data directory from a user home folder to a shared Jenkins-accessible location. This ensures the Jenkins service has the correct permissions to read the vulnerability database during scans.

## Prerequisites

* Access to the Jenkins host terminal.
* `sudo` privileges to modify directory ownership.

---

## Step 1: Move the Data to a Shared Location
Instead of keeping the data in the `ubuntu` home folder, move it to a location that Jenkins can natively access, such as `/var/lib/jenkins/`.

```bash
# Move the folder to the Jenkins library directory
sudo mkdir -p /var/lib/jenkins/.m2/repository/org/owasp
sudo cp -r /home/ubuntu/.m2/repository/org/owasp/dependency-check-data /var/lib/jenkins/.m2/repository/org/owasp

```

## Step 2: Update Permissions

Jenkins runs as its own user. You must transfer ownership of the data folder so the pipeline can access the files.

```bash
# Change ownership to the jenkins user and group
sudo chown -R jenkins:jenkins /var/lib/jenkins/.m2

```

## Step 3: Update Jenkins Pipeline Stage

Update the `-DdataDirectory` path in your Jenkinsfile to point to the new location. Since we disabled `autoUpdate`, ensure the path points to the specific version folder (e.g., `12.0`).

```groovy
stage("OWASP Dependency Check Scan") {
    steps {

        sh "mvn dependency-check:check"
        // or
        // sh "mvn clean verify"
// or overrides
        // sh "mvn dependency-check:check -DautoUpdate=false -DdataDirectory=/var/lib/jenkins/dependency-check-data/12.0"
    }
    post {
        always {
            dependencyCheckPublisher pattern: '**/dependency-check-report.xml'
        }
    }
}
Important

Also update your pom.xml formats section to include XML:

<formats>
    <format>HTML</format>
    <format>JSON</format>
    <format>XML</format>
</formats>
Install Jenkins Plugin

Install:

OWASP Dependency-Check Plugin

from:

Manage Jenkins → Plugins
Your pipeline structure should become
SCM-checkout
Git-Leaks
Build
OWASP-Dependency-Check
DockerImage
Trivy-scan
DockerPush
Deploy

Then Jenkins dashboard will display:

separate OWASP stage
vulnerability trends
severity counts
report links
}

```

---

## Troubleshooting

* **Permission Denied:** If the scan still fails, verify the permissions by running `ls -ld /var/lib/jenkins/dependency-check-data`.
* **Data Updates:** Since `autoUpdate` is set to `false`, remember to manually update this directory periodically or create a separate Jenkins job to sync the NVD data.


---

### Key Improvements made:
* **Added Context:** Explained *why* you are moving the files (permissions).
* **Code Blocks:** Used specific language identifiers (`bash`, `groovy`) for better syntax highlighting.
* **Troubleshooting:** Added a section to help if things don't work immediately.

Would you like me to create a separate script to automate the periodic update of that data folder?

