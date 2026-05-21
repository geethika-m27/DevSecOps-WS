Here is the complete, end-to-end blueprint to install Sonatype Nexus 3 using two different approaches on Ubuntu, configure your Spring Boot project components, and execute a flawless artifact deployment.

---

## Phase 1: Choose Your Installation Path

Pick **either** Path A (Docker Container) or Path B (Native Host Service) to get your Nexus Server up and running.

### Path A: The Docker Container Way (Cleanest & Quickest)

```bash
# 1. Clean up conflicting old packages
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done

# 2. Add Docker's official GPG signing key
sudo apt-get update && sudo apt-get install ca-certificates curl gnupg -y
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# 3. Add the stable APT repository link
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/list.d/docker.list > /dev/null

# 4. Install the runtime packages
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

# 5. Spin up Nexus with persistent disk mapping
sudo docker volume create nexus-data
sudo docker run -d -p 8081:8081 --name nexus --restart always -v nexus-data:/nexus-data sonatype/nexus3:latest

```

---

### Path B: The Native Host Linux Service Way

If your host virtual machine cannot run Docker, configure the binary execution layers directly:

---

## Phase 2: First-Time Nexus UI Setup

Nexus takes roughly 2 minutes to initialize its underlying database elements. Monitor progress using `tail -f /opt/sonatype-work/nexus3/log/nexus.log` (or `docker logs -f nexus`).

1. Open your browser and navigate to `http://<your-server-ip>:8081`.
2. Click **Sign In** in the top-right corner.
3. Retrieve your temporary admin setup token password:
* **Path A (Docker):** `sudo docker exec -it nexus cat /nexus-data/admin.password`
* **Path B (Native):** `sudo cat /opt/sonatype-work/nexus3/admin.password`


4. Complete the login wizard step, set your new corporate master password, and keep **Anonymous Access disabled** to lock down resource visibility.

---

## Phase 3: Connect Your Spring Boot Project

### 1. Update `pom.xml`

Add the target distribution routes directly inside your code repository blocks before the closing `</project>` element:

```xml
    <distributionManagement>
        <repository>
            <id>nexus-releases</id>
            <name>Nexus Release Repository</name>
            <url>http://localhost:8081/repository/maven-releases/</url>
        </repository>
        <snapshotRepository>
            <id>nexus-snapshots</id>
            <name>Nexus Snapshot Repository</name>
            <url>http://localhost:8081/repository/maven-snapshots/</url>
        </snapshotRepository>
    </distributionManagement>

```

### 2. Configure Local Authentication Secrets (`settings.xml`)

To prevent exposing administrative credentials within shared source repositories, save verification profiles into your user home directory profile configuration file located at `~/.m2/settings.xml`:

```xml
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 https://maven.apache.org/xsd/settings-1.0.0.xsd">
    <servers>
        <server>
            <id>nexus-releases</id>
            <username>admin</username>
            <password>admin#123</password>
        </server>
        <server>
            <id>nexus-snapshots</id>
            <username>admin</username>
            <password>admin#123</password>
        </server>
    </servers>
</settings>

```

---

## Phase 4: Build and Deploy

Navigate directly back into your Spring Boot repository workspace path and trigger the artifact upload workflow:

```bash
cd /mnt/host/d/PROJECTS/JAVA-PROJECTS/springboot
mvn clean deploy -DskipTests

```

### What Happens Behind the Scenes:

* Maven parses your `pom.xml` project description properties and notes version `0.1.0`.
* Because the string doesn't include a `-SNAPSHOT` suffix, it maps execution steps directly to the `nexus-releases` distribution cluster definition.
* It matches the identity token string references against the local `settings.xml` credential blocks.
* Your artifact gets compiled, packed into a production JAR archive, and pushed via HTTP requests straight into your Nexus repository registry. You can instantly confirm it by going to **Browse** on the Nexus UI!

