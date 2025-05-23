# 📄 Qualys Report Automation Script

This script interacts with the Qualys API to generate vulnerability scan reports using either asset group IDs or a file containing IP addresses. The report is downloaded in **CSV format** and saved to the local machine.

---

## ✨ Features

- ✅ Securely prompts for Qualys username and password
- 📂 Option to generate reports using **Asset Group ID(s)** or **host IP file**
- 🔄 Launches new reports or resumes download using existing **Report ID**
- ⏳ Automatically polls Qualys to wait for report completion
- 📥 Saves the report in **CSV format** in a `reports/` directory

---

## 🧰 Requirements

- Python 3.7+
- No external libraries required — all dependencies are included in the Python standard library

---

## 🚀 Usage

Run the script:

```bash
python qualys_report.py
```

You will be prompted to:

- Enter your **Qualys credentials**
- Choose to:
  - Launch a new report
  - Resume and download a report by ID
- Provide either:
  - One or more **Asset Group IDs**
  - A path to a file containing **host IPs** (one IP per line)
- Enter a valid **Report Template ID**

The script will then:
- Launch the report and poll Qualys every 10 minutes
- Automatically download the CSV report once it’s ready
- Save it to the `reports/` folder

---

## 🧪 Examples

### ✅ Example 1: Launch a new report with asset group IDs

```
Qualys Username: your_user
Qualys Password:
Enter 1 to launch a new report or 2 to check/download existing report: 1
Enter one or more Asset Group IDs (comma-separated): 12345,67890
Enter Report Template ID: 101234
```

### ✅ Example 2: Use a file with IPs

```
Enter 1 to launch a new report or 2 to check/download existing report: 1
Use asset group ID(s) (1) or host file (2)? Enter 1 or 2: 2
Enter path to host file (one IP per line): host.txt
Enter Report Template ID: 101234
```

### ✅ Example 3: Resume a report that’s already running

```
Enter 1 to launch a new report or 2 to check/download existing report: 2
Enter existing Report ID: 78901
```

---

## 📁 Output

All downloaded reports are saved as:

```
reports/Qualys_Report_<timestamp or report_id>.csv
```

---

## 📝 Notes

- Report **type must be "Scan"** — ensure the report template supports this.
- Script retries status check every **10 minutes**.
- Use a plain text file for host IPs, one per line, e.g.:

```
10.0.0.1
10.0.0.2
10.0.0.3
```

---
