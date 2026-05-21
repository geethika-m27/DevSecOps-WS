If you want a simple, straightforward script without any complex automation logic, you can use this clean, direct **Declarative Pipeline**.

This script checks out your code, packages it, and pushes the artifact straight to Nexus using your Jenkins credentials.

```groovy
pipeline {
    agent any

    tools {
        // Make sure these match the names defined in your Jenkins 'Global Tool Configuration'
        jdk 'openjdk-21'
        maven 'maven-3.9'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                // Compiles your Spring Boot application and skips unit tests for speed
                sh 'mvn clean package -DskipTests=true'
            }
        }

        stage('Deploy to Nexus') {
            steps {
                // Securely pulls your Nexus username and password from Jenkins credentials store
                withCredentials([usernamePassword(credentialsId: 'nexus-credentials-id', 
                                                 usernameVariable: 'NEXUS_USER', 
                                                 passwordVariable: 'NEXUS_PASSWORD')]) {
                    
                    // Runs the deployment command using your t3.medium EC2 IP address
                    sh '''
                        mvn deploy -DskipTests=true \
                        -DaltDeploymentRepository=nexus-releases::default::http://YOUR-EC2-IP:8081/repository/maven-releases/ \
                        -Dusername=${NEXUS_USER} \
                        -Dpassword=${NEXUS_PASSWORD}
                    '''
                }
            }
        }
    }
}

```

### ⚙️ Quick Customization Steps:

1. Replace **YOUR-EC2-IP** inside the deploy stage with your actual t3.medium public or private IP address.
2. If your project's version inside your pom.xml ends with -SNAPSHOT, change the URL path in the script from /maven-releases/ to /maven-snapshots/ and change nexus-releases to nexus-snapshots.