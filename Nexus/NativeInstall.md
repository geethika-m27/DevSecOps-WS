# README: Sonatype Nexus 3 & Java 21 Spring Boot Setup on AWS `t3.medium`

This guide explains how to deploy:

* **Sonatype Nexus Repository Manager 3** using **Java 11**
* **Spring Boot Application** using **Java 21**

on a single AWS `t3.medium` EC2 instance.

A `t3.medium` provides:

* **2 vCPUs**
* **4 GB RAM**

This configuration is sufficient for stable production-style deployment without aggressive JVM downsizing or heavy swap dependency.

---

# 1. Infrastructure Prerequisites

Before starting installation, ensure your environment matches the following requirements.

## 1.1 EC2 Instance Requirements

| Component     | Requirement                  |
| ------------- | ---------------------------- |
| Instance Type | `t3.medium`                  |
| CPU           | 2 vCPUs                      |
| RAM           | 4 GB                         |
| Storage       | Minimum 30 GB                |
| EBS Type      | `gp3` Recommended            |
| OS            | Ubuntu 22.04 LTS Recommended |

---

# 2. Java Runtime Strategy

To avoid Java version conflicts:

| Application              | Java Version |
| ------------------------ | ------------ |
| Nexus Repository Manager | OpenJDK 11   |
| Spring Boot Application  | OpenJDK 21   |

We intentionally avoid setting a global system-wide `JAVA_HOME` for Nexus.

---

# 3. Update System Packages

```bash
sudo apt update && sudo apt upgrade -y
```

---

# 4. Install Java 11 for Nexus

Modern Nexus 3 versions require Java 11.

```bash
sudo apt install openjdk-11-jdk-headless -y
```

Verify installation:

```bash
java -version
```

---

# 5. Install Java 21 for Spring Boot

```bash
sudo apt install openjdk-21-jdk -y
```

Verify installation:

```bash
/usr/lib/jvm/java-21-openjdk-amd64/bin/java -version
```

---

# 6. Download and Extract Nexus Repository Manager

Move into `/opt`:

```bash
cd /opt
```

Download Nexus:

```bash
sudo wget https://download.sonatype.com/nexus/3/nexus-3.92.2-01-linux-x86_64.tar.gz
```

Extract package:

```bash
sudo tar -zxvf nexus-3.92.2-01-linux-x86_64.tar.gz
```

Rename extracted directory:

```bash
sudo mv /opt/nexus-3.92.2-01 /opt/nexus
```

---

# 7. Create Dedicated Nexus User

Running Nexus as `root` is not recommended.

Create a dedicated service user:

```bash
sudo useradd -r -d /opt/nexus -s /bin/false nexus
```

Assign ownership:

```bash
sudo chown -R nexus:nexus /opt/nexus
sudo chown -R nexus:nexus /opt/sonatype-work
```

Configure Nexus to run using the `nexus` user:

```bash
echo 'run_as_user="nexus"' | sudo tee /opt/nexus/bin/nexus.rc
```

---

# 8. Configure Nexus JVM Memory

Since `t3.medium` has 4 GB RAM, we can use a healthier JVM allocation.

Open Nexus JVM options:

```bash
sudo nano /opt/nexus/bin/nexus.vmoptions
```

Replace contents with:

```properties
-Xms1200m
-Xmx1200m
-XX:MaxDirectMemorySize=2g
-XX:+UnlockDiagnosticVMOptions
-XX:+LogVMOutput
-XX:LogFile=../sonatype-work/nexus3/log/jvm.log
-XX:-OmitStackTraceInFastThrow

-Dkaraf.home=.
-Dkaraf.base=.
-Djava.util.logging.config.file=etc/spring/java.util.logging.properties
-Dkaraf.data=../sonatype-work/nexus3
-Dkaraf.log=../sonatype-work/nexus3/log
-Djava.io.tmpdir=../sonatype-work/nexus3/tmp

-Djdk.tls.ephemeralDHKeySize=2048
-Dfile.encoding=UTF-8
-Djava.net.preferIPv4Stack=true
-Dcom.graphbuilder.geom.Geom.unifySize=0

--add-reads=java.xml=java.logging

--add-opens=java.base/java.security=ALL-UNNAMED
--add-opens=java.base/java.net=ALL-UNNAMED
--add-opens=java.base/java.lang=ALL-UNNAMED
--add-opens=java.base/java.util=ALL-UNNAMED
--add-opens=java.naming/javax.naming.spi=ALL-UNNAMED
--add-opens=java.rmi/sun.rmi.transport.tcp=ALL-UNNAMED

--add-exports=java.base/sun.net.www.protocol.http=ALL-UNNAMED
--add-exports=java.base/sun.net.www.protocol.https=ALL-UNNAMED
--add-exports=java.base/sun.net.www.protocol.jar=ALL-UNNAMED
--add-exports=jdk.xml.dom/org.w3c.dom.html=ALL-UNNAMED
--add-exports=jdk.naming.rmi/com.sun.jndi.url.rmi=ALL-UNNAMED
--add-exports=java.security.sasl/com.sun.security.sasl=ALL-UNNAMED
```

---

# 9. Configure Nexus Java Path

Edit Nexus startup configuration:

```bash
sudo nano /opt/nexus/bin/nexus
```

Find:

```bash
INSTALL4J_JAVA_HOME_OVERRIDE=
```

Replace with:

```bash
INSTALL4J_JAVA_HOME_OVERRIDE=/usr/lib/jvm/java-11-openjdk-amd64
```

This ensures Nexus always uses Java 11.

---

# 10. Configure Systemd Service

Create Nexus service file:

```bash
sudo nano /etc/systemd/system/nexus.service
```

Paste:

```ini
[Unit]
Description=Nexus Repository Manager
After=network.target

[Service]
Type=forking
LimitNOFILE=65536
User=nexus
Group=nexus

ExecStart=/opt/nexus/bin/nexus start
ExecStop=/opt/nexus/bin/nexus stop

Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

# 11. Enable and Start Nexus

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable service:

```bash
sudo systemctl enable nexus
```

Start Nexus:

```bash
sudo systemctl start nexus
```

Check status:

```bash
sudo systemctl status nexus
```

---

# 12. Verify Nexus Startup

Monitor logs:

```bash
tail -f /opt/sonatype-work/nexus3/log/nexus.log
```

Wait until you see:

```text
Started Sonatype Nexus
```

---

# 13. Access Nexus Web Interface

Open browser:

```text
http://your-ec2-public-ip:8081
```

---

# 14. Retrieve Initial Nexus Admin Password

Nexus generates a temporary admin password.

Retrieve it using:

```bash
cat /opt/sonatype-work/nexus3/admin.password
```

Login credentials:

| Username | Password           |
| -------- | ------------------ |
| admin    | Generated password |

---

# 15. Configure Maven Hosted Repositories

Inside Nexus UI:

## Create Repositories

Create:

* `maven-releases`
* `maven-snapshots`

Recommended repository types:

| Repository      | Version Policy |
| --------------- | -------------- |
| maven-releases  | Release        |
| maven-snapshots | Snapshot       |

---

# 16. Configure Spring Boot Project (`pom.xml`)

Add the following inside your `pom.xml` before `</project>`:

```xml
<distributionManagement>
    <repository>
        <id>nexus-releases</id>
        <name>Nexus Release Repository</name>
        <url>http://your-ec2-ip:8081/repository/maven-releases/</url>
    </repository>

    <snapshotRepository>
        <id>nexus-snapshots</id>
        <name>Nexus Snapshot Repository</name>
        <url>http://your-ec2-ip:8081/repository/maven-snapshots/</url>
    </snapshotRepository>
</distributionManagement>
```

---

# 17. Configure Maven Authentication (`settings.xml`)

On your local machine or CI/CD server:

File location:

```bash
~/.m2/settings.xml
```

Add:

```xml
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 https://maven.apache.org/xsd/settings-1.0.0.xsd">

    <servers>

        <server>
            <id>nexus-releases</id>
            <username>admin</username>
            <password>your_nexus_password</password>
        </server>

        <server>
            <id>nexus-snapshots</id>
            <username>admin</username>
            <password>your_nexus_password</password>
        </server>

    </servers>

</settings>
```

---

# 18. Build and Deploy Spring Boot Application

Navigate into your project:

```bash
cd /path/to/springboot-project
```

Deploy artifact:

```bash
mvn clean deploy -DskipTests
```

---

# 19. Verify Artifact Upload

Inside Nexus UI:

* Navigate to:

```text
Browse → maven-releases
```

or

```text
Browse → maven-snapshots
```

Your uploaded JAR should now appear in the repository.

---

# 20. Recommended Production Optimizations

## Increase Linux File Limits

```bash
sudo nano /etc/security/limits.conf
```

Add:

```text
nexus soft nofile 65536
nexus hard nofile 65536
```

---

## Open Required Ports

If using AWS Security Groups:

| Port        | Purpose         |
| ----------- | --------------- |
| 22          | SSH             |
| 8081        | Nexus           |
| 8080 / 8443 | Spring Boot App |

---

# 21. Useful Operational Commands

## Restart Nexus

```bash
sudo systemctl restart nexus
```

## Stop Nexus

```bash
sudo systemctl stop nexus
```

## View Nexus Logs

```bash
tail -f /opt/sonatype-work/nexus3/log/nexus.log
```

## Check Running Java Processes

```bash
ps -ef | grep java
```

---

# 22. Final Architecture Summary

| Component                | Runtime   | Purpose                |
| ------------------------ | --------- | ---------------------- |
| Nexus Repository Manager | Java 11   | Maven Artifact Hosting |
| Spring Boot Application  | Java 21   | Business Application   |
| EC2 Instance             | t3.medium | Shared Host            |
| Storage                  | gp3 EBS   | Artifact & App Storage |

---

# ✅ Deployment Completed

You now have:

* Nexus Repository Manager running securely on Java 11
* Spring Boot application compatible with Java 21
* Maven artifact deployment pipeline configured
* Production-friendly JVM memory allocation
* Systemd-managed Nexus service for automatic recovery and startup
