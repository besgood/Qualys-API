# Qualys Asset Group Report Generator

This Python script automates the generation and download of Qualys vulnerability scan reports for **one or more Asset Group IDs**, using a specified **report template**. The final report is downloaded in **Excel format (.xlsx)**.

---

## 🔧 Features

- Securely prompts for your Qualys username and password (no hardcoding)
- Accepts **multiple Asset Group IDs**
- Supports user-specified Report Template ID
- Generates report in Excel format
- Waits for report to finish and downloads it automatically

---

## 📦 Requirements

- Python 3.6+
- Internet access to connect to [Qualys API](https://qualysapi.qualys.com)
- Access to the Qualys Vulnerability Management (VM/VMDR) API

### Python Dependencies

Install via pip:

```bash
pip install requests
