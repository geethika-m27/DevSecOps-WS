This guide is now reorganized to prioritize the **Permanent Configuration** and explains the "Short Version" vs. the "Full Coordinate" command as requested.

---

# Workshop Guide: Local NVD Data Setup for Dependency-Check

This guide explains how to bypass NIST API rate limits and "403 Forbidden" errors by using a pre-downloaded vulnerability database.

## 1. Prerequisites (Download & Extract)

Before configuring Maven, ensure the data is in the correct location so the plugin can find it.

```bash
# 1. Install the tools
sudo apt update && sudo apt install pipx unzip -y

# 2. Add pipx to your PATH
pipx ensurepath

# --- RESTART / REFRESH HAPPENS HERE ---
source ~/.bashrc  
# --------------------------------------

# 3. Now you can install gdown
pipx install gdown

# 4. And run gdown (if this fails, run 'source ~/.bashrc' one more time)
gdown 1o7FKaSLfJ-MxNuZQvXM8BbBTG9cUfCSN -O nvd-data-12.zip

# 5. Extract the data
mkdir -p ~/.m2/repository/org/owasp/dependency-check-data/12.0
unzip nvd-data-12.zip -d ~/.m2/repository/org/owasp/dependency-check-data/12.0
```

---

## 2. Permanent Configuration in `pom.xml`

To avoid typing long flags every time, add this configuration to your `pom.xml`. This locks the security policy to **CVSS 7.0 (High)** and points the plugin to your local folder.

```xml
<plugin>
    <groupId>org.owasp</groupId>
    <artifactId>dependency-check-maven</artifactId>
    <version>12.2.0</version>
    <configuration>
        <autoUpdate>false</autoUpdate>
        <dataDirectory>${user.home}/.m2/repository/org/owasp/dependency-check-data/</dataDirectory>
        
        <failBuildOnCVSS>7.0</failBuildOnCVSS>
        
        <formats>
            <format>HTML</format>
            <format>JSON</format>
        </formats>
    </configuration>
</plugin>

```

### The "Short Version" Command

Once the `pom.xml` above is saved, you no longer need to type the full coordinates. Use this command to run the scan:

```bash
mvn dependency-check:check -U -DautoUpdate=false -DdataDirectory=/home/ubuntu/.m2/repository/org/owasp/dependency-check-data/12.0

```

### Check the report 
```bash
cat /home/ubuntu/springboot/target/dependency-check-report.html
```

---

## 3. Why we don't use the long command anymore

In early setup steps, we used the "Full Coordinate" command:
`mvn org.owasp:dependency-check-maven:check -DautoUpdate=false -DdataDirectory=...`

**Why stop using it?**

1. **Redundancy:** Once the plugin is in your `pom.xml`, Maven already knows the `groupId`, `artifactId`, and `version`. Typing them again is redundant.
2. **Configuration Sync:** The long command ignores the `<configuration>` block in your `pom.xml` unless you repeat every single flag. Using `mvn dependency-check:check` automatically respects your `failBuildOnCVSS` and `formats` settings.
3. **Human Error:** The long command is easy to mistype. The short version is clean and standardized for the classroom.

---

## 4. Execution Workflow

1. **Regular Development:** Use `mvn clean verify`. This will **not** run the security scan (it remains fast).
2. **Security Audit:** When you want to check for bugs, run:
```bash
mvn dependency-check:check -DautoUpdate=false -o

```



---

## 5. Verification

1. **Check Logs:** You should see `Check for updates (multi-threaded) : Finished` instantly.
2. **Locate Report:** Open `target/dependency-check-report.html`.
3. **Validate Findings:** Verify that **CVE-2021-44228 (Log4Shell)** is flagged.

**Note:** The `-o` flag in the command stands for **Offline**. It ensures Maven uses your local `.m2` repository and does not try to reach out to the internet for any reason.
