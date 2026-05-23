The following agenda points and step-by-step procedures are based on the provided tutorial for **AWS Lambda**.

### **Agenda Points**
The session focuses on seven key areas:
1.  **What is AWS Lambda?**
2.  **Creating an AWS Lambda function** from scratch.
3.  **Creating a function from a ZIP code file** stored locally.
4.  **Creating a function by uploading a ZIP file to an S3 bucket.**
5.  **Enabling a Function URL** for public or authenticated access.
6.  **Creating and using Environment Variables** within a function.
7.  **Creating and using AWS Lambda Layers** to share common libraries across multiple functions.

---

### **Step-by-Step Procedures**

#### **1. What is AWS Lambda?**
*   **Definition:** It is a **serverless executor** that takes code as input and produces an output after execution.
*   **Key Advantages:** There is **no server setup**, no need to manually start or stop servers, and it follows a **pay-per-go** model.
*   **Supported Languages:** It supports **Python, Java, Node.js, and Go**.

#### **2. How to Create a Basic Lambda Function**
1.  Open the **AWS Console**, search for "Lambda," and click **Create function**.
2.  Select **Author from scratch** and enter a **Function name**.
3.  Choose your **Runtime** (e.g., Python 3.12) and **Architecture** (e.g., x86_64).
4.  Click **Create function**.
5.  In the **Code** tab, write your logic, click **Deploy**, and then **Test** by creating a test event to see the execution results and logs.

#### **3. Creating a Function from a Local ZIP File**
1.  Write your code in an **IDE** (like IntelliJ or VS Code).
2.  **Mandatory Step:** You must define a **Lambda Handler** function in your code to serve as the entry point.
3.  Install dependencies locally by running `pip 3 install -r requirement.txt` in your terminal.
4.  **Zipping:** Go inside your project folder, select the code files, and the library folders (like `venv`), then **compress them into a ZIP file**.
5.  In the AWS Lambda console, go to the **Code** tab, click **Upload from**, and select **.zip file**.
6.  Update **Runtime settings** to ensure the **Handler** name matches your `filename.function_name` (e.g., `test_lambda.lambda_handler`).

#### **4. Uploading via S3 Bucket**
1.  Go to the **S3 console** and upload your code ZIP file to a bucket in the **same region** as your Lambda function.
2.  Copy the **S3 URI** of the uploaded ZIP file.
3.  In your Lambda function's **Code** tab, select **Upload from** and choose **Amazon S3 location**.
4.  Paste the **S3 URI** and click **Save**.

#### **5. Enabling Function URLs**
1.  In the Lambda function console, go to the **Configuration** tab and select **Function URL**.
2.  Click **Create function URL**.
3.  **For Public Access:** Select **Auth type: NONE**.
4.  **For Authenticated Access:** Select **Auth type: AWS_IAM**.
5.  Click **Save**.
6.  **To Test Authenticated URLs:** Use an application like **Postman**, set authorization to **AWS Signature**, and provide your **AWS Access Key** and **Secret Key**.

#### **6. Using Environment Variables**
1.  Go to the **Configuration** tab and select **Environment variables**.
2.  Click **Edit**, then **Add environment variable**.
3.  Enter a **Key** and **Value**, then click **Save**.
4.  In your Python code, import the `os` library and use `os.environ.get('YOUR_KEY')` to retrieve the value.

#### **7. Creating and Using Lambda Layers**
1.  **Directory Structure:** Create a folder named `python`, then subfolders: `python/lib/python3.x/site-packages/[your_module]`.
2.  Place your shared library code and an `__init__.py` file inside your module folder.
3.  **Zip the top-level `python` folder**.
4.  In the Lambda dashboard, click **Layers** -> **Create layer**, upload the ZIP, and click **Create**.
5.  **Attach to Lambda:** Open your Lambda function, scroll down to **Layers**, click **Add layer**, select **Custom layers**, and choose your created layer and version.
6.  **Usage:** In your function code, **import the module** just like a standard library (e.g., `from my_module.my_function import function_from_layer`).