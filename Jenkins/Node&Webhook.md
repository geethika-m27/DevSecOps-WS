# Comprehensive Jenkins Master-Slave Architecture & Automation Guide

This document provides the complete, production-ready blueprint for establishing an AWS-native Jenkins Master-Slave architecture, configuring global build tools, bypassing resource-level constraints, and implementing automated Git Webhook triggers.

---

## 🛠️ Phase 1: Prepare the Slave Node

Log into your **Slave machine (`172.31.14.101`)** via SSH as the `ubuntu` user. These steps prepare your runner for agent operations and containerization tasks.

### 1. Resolve Linux `/tmp` Storage Cap (Bypass Low Disk Threshold)

By default, certain cloud environments mount `/tmp` as a restricted RAM drive (`tmpfs`) capped at ~455 MiB. Because this falls below Jenkins' default 1.00 GiB safety trigger, Jenkins will automatically mark the node offline.

To solve this permanently without repartitioning, create a dedicated directory on the root partition (which has 11 GiB of free space available):

```bash
mkdir -p /home/ubuntu/jenkins_tmp

```

### 2. Install Run-Time Packages

Install Java 21 (required to run the Jenkins background remoting agent and compile modern frameworks) and the core Docker engine:

```bash
sudo apt update -y
sudo apt install openjdk-21-jdk docker.io -y

```

### 3. Grant Containerization Permissions

Add the `ubuntu` execution user to the Docker system group so your CI/CD pipelines can run Docker commands smoothly without needing administrative `sudo` prefixes:

```bash
sudo usermod -aG docker ubuntu

# Force apply the new group membership to your current terminal session
newgrp docker 

```

---

## 🔑 Phase 2: SSH Security Setup (Using AWS Key Pair)

Since both your Jenkins Master and Slave instances were launched using the same AWS Key Pair, they already trust each other on the OS level. AWS automatically injects the corresponding public key into the `ubuntu` user's `~/.ssh/authorized_keys` file at boot time. **No manual `ssh-keygen` execution is required.**

All you need to do is retrieve the contents of your existing AWS private key (`.pem` file) so you can hand it over to the Jenkins credential vault.

### 1. View and Copy Your AWS Private Key Content

Locate the `.pem` file you use to log into your EC2 instances. Open it on your local machine using any text editor (like Notepad or VS Code), or view it via your Master terminal if it is hosted there:

```bash
cat /path/to/your-aws-key.pem

```

Copy the entire block of text exactly as shown, ensuring you include the header and footer lines:

```text
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA0Y...
...
-----END RSA PRIVATE KEY-----

```

---

## 🖥️ Phase 3: Configure Node in Jenkins UI

Now, map this existing AWS Key directly into the Jenkins UI credential manager so the Master can securely authenticate with `slave1`.

1. Navigate to **Dashboard** ➡️ **Manage Jenkins** ➡️ **Nodes** ➡️ **New Node**.
2. **Node Name:** `slave1` | Select **Permanent Agent** | Click **Create**.
3. Configure the primary agent parameters:

| Configuration Field | Target Value Setup |
| --- | --- |
| **Description** | Production Slave for Building Spring Boot Containers |
| **Number of executors** | `1` |
| **Remote root directory** | `/home/ubuntu` |
| **Labels** | `slave1` *(Must match the agent block in your Jenkinsfile)* |
| **Usage** | Only build jobs with label expressions matching this node |
| **Launch method** | Launch agents via SSH |
| **Host** | `172.31.14.101` *(Your Slave Private IP)* |
| **Host Key Verification Strategy** | Non verifying Verification Strategy |

4. **Credentials Setup:** Next to the *Credentials* dropdown, click **Add** ➡️ **Jenkins**.
* **Kind:** Select `SSH Username with private key`
* **Scope:** Global (Jenkins, nodes, items, etc)
* **ID:** `aws-ec2-key`
* **Username:** `ubuntu` *(Must be exactly `ubuntu` to match the AWS default user)*
* **Private Key:** Select **Enter directly** ➡️ Click **Add** ➡️ Paste the entire text block of your `.pem` file copied during Phase 2.
* Click **Add**.


5. Back on the main configuration page, select your newly created `aws-ec2-key` from the **Credentials** dropdown menu.
6. **Environment Variable Override (Redirect Java Temp Directory):**
* Scroll down to **Node Properties** and check the box for **Environment variables**.
* Click **Add**:
* **Name:** `java.io.tmpdir`
* **Value:** `/home/ubuntu/jenkins_tmp` *(Points Jenkins to the root disk instead of the 455MB RAM drive)*




7. Click **Save**. Select `slave1` from the nodes list and click **Launch Agent** (or **Bring this node back online**) to establish the connection.

---

## ⚙️ Phase 4: Define Global Tools & System Monitors

Map your global tools within the primary controller interface so Jenkins knows how to dynamically provision software binaries during pipeline runtimes.

### 1. Global Monitor Tuning

1. Go to **Manage Jenkins** ➡️ **Nodes**.
2. Click **Configure Monitors** on the left-hand menu sidebar.
3. Scroll down to **Free Temp Space Threshold** and **Free Disk Space Threshold**.
4. Adjust the safety thresholds down to `100MiB` or `200MiB` to prevent overly aggressive, automated node lockouts. Click **Save**.

### 2. Java and Build Ecosystem Mapping

1. Navigate to **Manage Jenkins** ➡️ **Tools**.
2. Scroll down to **JDK Installations** and click **Add JDK**:
* **Name:** `jdk21`
* **JAVA_HOME:** `/usr/lib/jvm/java-21-openjdk-amd64`
* *Uncheck* **Install automatically** (This tells Jenkins to utilize the high-performance local binary we installed via apt).


3. Scroll down to **Maven Installations** and click **Add Maven**:
* **Name:** `m3`
* *Check* **Install automatically** *(Jenkins will automatically download and unpack the official Apache Maven binaries onto the slave workspace on demand)*.


4. Click **Save**.

---

## 🌐 Phase 5: Git Automated Webhook Infrastructure

Automate execution triggers so that code check-ins directly baseline pipeline execution phases without human intervention.

### 1. Configure the Provider Repository (e.g., GitHub)

1. Open your Git provider platform and navigate to your specific code repository.
2. Select **Settings** ➡️ **Webhooks** ➡️ Click **Add webhook**.
3. Populate the integration matrix exactly as follows:
* **Payload URL:** `http://<YOUR_JENKINS_MASTER_PUBLIC_IP>:8080/github-webhook/` *(Ensure trailing slash is included)*
* **Content type:** `application/json`
* **Which events:** `Just the push event`


4. Click **Add webhook** to save the configuration.

### 2. Configure the Pipeline Job Trigger

1. Open your pipeline job configuration inside the Jenkins Master user interface.
2. Under the **Build Triggers** section block, select the checkbox for **GitHub hook trigger for GITScm polling**.
3. Click **Save**.

### 3. Pipeline Blueprint Reference File (`Jenkinsfile`)

Ensure your repository contains a declarative tracking file matching the design format below to invoke tools and targets cleanly across your architecture:

```groovy
pipeline {
    agent { label 'slave1' }
    
    tools {
        jdk 'jdk21'
        maven 'm3'
    }
    
    environment {
        // Force Docker to use BuildKit for faster, modern image construction
        DOCKER_BUILDKIT = '1' 
    }
    
    stages {
        stage('Validation') {
            steps {
                echo "Running execution on node: ${env.NODE_NAME}"
                sh 'java -version'
                sh 'mvn -version'
                sh 'docker ps' // Validates passwordless group socket access
            }
        }
        
        stage('Compile & Package') {
            steps {
                sh 'mvn clean package -DskipTests'
            }
        }
        
        stage('Container Construction') {
            steps {
                sh 'docker build -t springboot:1.0 .'
            }
        }
    }
}

```

### 4. Validation Workflow

* **Initial Bootstrap Execution:** Execute the first run **manually** inside Jenkins by clicking **Build Now**. This registers and baselines internal repository tracking indices.
* **Automatic Integration Verification:** Modify a file in your repository locally, push a commit to the remote tracking branch, and verify that the automation webhook immediately registers and schedules a build on `slave1`.</YOUR_JENKINS_MASTER_PUBLIC_IP>