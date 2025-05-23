# Qualys Asset Group or Host File Report Generator

This Python script generates and downloads vulnerability scan reports from Qualys using either:

* A list of **Asset Group IDs**, or
* A **host file** with IP addresses or DNS names

The report is generated using a **specified report template ID** and downloaded in **Excel (.xlsx)** format.

---

## 🔧 Features

* ✅ Interactive CLI prompts for secure usage
* ✅ Supports **multiple asset group IDs**
* ✅ Supports **custom host files**
* ✅ Generates **Excel-formatted** reports
* ✅ Waits for the report to complete before downloading
* ✅ Automatically names output files
* ✅ Secure password input (no plaintext or logging)

---

## 📦 Requirements

* **Python 3.6+**

### 🧪 Third-Party Libraries

Install with:

```bash
pip install requests
```
🔹 Option 1: Asset Group IDs
Choose target input mode - (1) Asset Group ID(s) or (2) Host File [1/2]: 1
Enter one or more Asset Group IDs (comma-separated): 1234, 5678
Report Template ID: 4321

🔹 Option 2: Host File
Choose target input mode - (1) Asset Group ID(s) or (2) Host File [1/2]: 2
Enter path to host file (IP or FQDN per line): ./hosts.txt
Report Template ID: 4321


❗ Notes
You must have a valid Qualys account with API access enabled.

The script uses the Qualys VM/VMDR API v2.0.

Asset Group IDs and Template IDs must be valid and accessible to the user.

Host file must include one IP or hostname per line.

Passwords are securely entered using getpass (not echoed or saved).

Make sure your Qualys user account has access to the selected asset groups or hosts.
