
It covers everything from downloading the offline data database to executing the scans using the **Short Way (Simple)** and the **Long Way (Advanced)**.

---

## Step 1: Prepare the Offline NVD Database (Prerequisite)

Before running any offline commands, you must manually download the vulnerability database so your local machine doesn't try to query the internet. Run these terminal commands:

```bash
# 1. Install required download and extraction tools
sudo apt update && sudo apt install pipx unzip -y

# 2. Add pipx to your PATH and refresh your environment
pipx ensurepath
source ~/.bashrc  

# 3. Install gdown to download files from Google Drive via CLI
pipx install gdown

# 4. Download the NVD 12.0 compressed data bundle
gdown 1o7FKaSLfJ-MxNuZQvXM8BbBTG9cUfCSN -O nvd-data-12.zip

# 5. Create the required directory structure and extract the database
mkdir -p ~/.m2/repository/org/owasp/dependency-check-data/12.0
unzip nvd-data-12.zip -d ~/.m2/repository/org/owasp/dependency-check-data/12.0

```

---

## Strategy A: The Short Way (Simple & Automated)

**Best for:** CI/CD pipelines, automated builds, and everyday team use. This approach hardcodes your configurations inside your `pom.xml` so your terminal commands remain short and easy to remember.

### 1. Add Configuration to `pom.xml`

Insert this plugin snippet inside the `<build><plugins>` section of your `pom.xml`.

> ⚠️ **Crucial Rule:** Leave the trailing `/12.0` out of the `<dataDirectory>` path in the XML. Because the plugin version is `12.0.0`, it will look inside the `12.0` subfolder you extracted during Step 1 automatically.

```xml
<plugin>
    <groupId>org.owasp</groupId>
    <artifactId>dependency-check-maven</artifactId>
    <version>12.0.0</version>
    <configuration>
        <autoUpdate>false</autoUpdate>
        <dataDirectory>${user.home}/.m2/repository/org/owasp/dependency-check-data</dataDirectory>
        <failBuildOnCVSS>7.0</failBuildOnCVSS>
        <formats>
            <format>HTML</format>
            <format>JSON</format>
        </formats>
    </configuration>
    <executions>
        <execution>
            <goals>
                <goal>check</goal>
            </goals>
        </execution>
    </executions>
</plugin>

```


### 2. Simple Executions

With the configurations stored safely in the XML file, run either of these short commands (the `-o` flag tells Maven to run fully offline):

* **To run ONLY the vulnerability scan:**
```bash
mvn dependency-check:check -o

```


* **To compile, build, and scan the project all at once:**
```bash
mvn clean verify -o

```



---

## Strategy B: The Long Way (Advanced & Zero-Config)

**Best for:** One-time local debugging, scanning external projects, or ad-hoc security audits where you **cannot or do not want to modify the project's `pom.xml` file**.

These commands bypass your project configurations entirely by declaring every single instruction explicitly in the terminal string.

### 1. Advanced Offline Command (No `pom.xml` changes)

This massive command overrides everything, explicitly pointing directly to your extracted `12.0` folder path, turning off updates, and forcing offline processing (`-o`):

* **Scan Only:**
```bash
mvn org.owasp:dependency-check-maven:12.0.0:check \
  -DautoUpdate=false \
  -DdataDirectory=/home/ubuntu/.m2/repository/org/owasp/dependency-check-data/12.0 \
  -DfailBuildOnCVSS=7.0 \
  -Dformats=HTML,JSON \
  -o

```


* **Clean, Build, and Scan:**
```bash
mvn clean verify org.owasp:dependency-check-maven:12.0.0:check \
  -DautoUpdate=false \
  -DdataDirectory=/home/ubuntu/.m2/repository/org/owasp/dependency-check-data/12.0 \
  -DfailBuildOnCVSS=7.0 \
  -Dformats=HTML,JSON \
  -o

```



### 2. Advanced Online Command (No `pom.xml` changes + NVD API Key)

If you are on an internet-connected machine and want to run a zero-config check while bypassing rate limits dynamically using your NVD API Key instead of the local folder structure:

```bash
mvn org.owasp:dependency-check-maven:12.0.0:check \
  -DnvdApiKey=YOUR_API_KEY_HERE \
  -DfailBuildOnCVSS=7.0 \
  -Dformats=HTML,JSON

```

## Verification

1. **Check Logs:** You should see `Check for updates (multi-threaded) : Finished` instantly..
2. **Locate Report:** Open `target/dependency-check-report.html`.
3. **Validate Findings:** Verify that **CVE-2021-44228 (Log4Shell)** is flagged.

**Note:** The `-o` flag in the command stands for **Offline**. It ensures Maven uses your local `.m2` repository and does not try to reach out to the internet for any reason.
