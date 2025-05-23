import requests
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth
import getpass
import time
import os

# Constants
QUALYS_BASE_URL = 'https://qualysapi.qualys.com'
OUTPUT_FORMAT = 'csv'

# Prompt for credentials
USERNAME = input("Qualys Username: ")
PASSWORD = getpass.getpass("Qualys Password: ")

# Headers for API calls
HEADERS = {
    'X-Requested-With': 'Python script',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Ensure reports directory exists
if not os.path.exists("reports"):
    os.makedirs("reports")


def read_hosts_from_file(file_path):
    with open(file_path, 'r') as f:
        ips = [line.strip() for line in f if line.strip()]
    return ','.join(ips)


def build_host_input():
    choice = input("Use asset group ID(s) (1) or host file (2)? Enter 1 or 2: ").strip()
    if choice == '1':
        ag_ids = input("Enter one or more Asset Group IDs (comma-separated): ").strip()
        return 'asset_group_ids', ag_ids
    elif choice == '2':
        file_path = input("Enter path to host file (one IP per line): ").strip()
        ips = read_hosts_from_file(file_path)
        return 'ips', ips
    else:
        print("Invalid choice. Exiting.")
        exit(1)


def launch_report():
    report_title = f"Qualys_Report_{int(time.time())}"
    template_id = input("Enter Report Template ID: ").strip()
    input_type, input_value = build_host_input()

    data = {
        'action': 'launch',
        'report_title': report_title,
        'report_type': 'Scan',
        'template_id': template_id,
        'output_format': OUTPUT_FORMAT,
        input_type: input_value
    }

    print("🚀 Launching report...")
    response = requests.post(
        f"{QUALYS_BASE_URL}/api/2.0/fo/report/",
        data=data,
        headers=HEADERS,
        auth=HTTPBasicAuth(USERNAME, PASSWORD)
    )

    root = ET.fromstring(response.text)

    # Updated parsing logic for response format
    report_id = None
    for item in root.findall('.//ITEM'):
        key = item.find('KEY')
        value = item.find('VALUE')
        if key is not None and key.text == "ID" and value is not None:
            report_id = value.text
            break

    if not report_id:
        raise Exception(f"❌ Report ID not found in response:\n{response.text}")

    print(f"📄 Report launched with ID: {report_id}")
    return report_id, report_title


def check_report_status(report_id):
    url = f'{QUALYS_BASE_URL}/api/2.0/fo/report/?action=list&id={report_id}'
    while True:
        response = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        root = ET.fromstring(response.text)
        state_elem = root.find('.//STATE')
        if state_elem is not None:
            status = state_elem.text
            if status == "Finished":
                print("✅ Report is ready for download.")
                return
            else:
                print(f"⌛ Report status: {status} (retrying in 10 minutes)")
                time.sleep(600)  # 10 minutes
        else:
            raise Exception(f"❌ Could not determine report status. Response:\n{response.text}")


def download_report(report_id, report_title=None):
    print(f"⬇️ Downloading report ID: {report_id}")
    url = f'{QUALYS_BASE_URL}/api/2.0/fo/report/?action=fetch&id={report_id}'
    response = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(USERNAME, PASSWORD))

    if response.status_code != 200:
        raise Exception(f"❌ Failed to download report. HTTP {response.status_code}")

    if not report_title:
        report_title = f"Qualys_Report_{report_id}"

    csv_path = os.path.join("reports", f"{report_title}.csv")

    with open(csv_path, 'wb') as f:
        f.write(response.content)
    print(f"📥 CSV report saved to: {csv_path}")


def main():
    mode = input("Enter 1 to launch a new report or 2 to check/download existing report: ").strip()
    if mode == '1':
        report_id, title = launch_report()
        check_report_status(report_id)
        download_report(report_id, title)
    elif mode == '2':
        report_id = input("Enter existing Report ID: ").strip()
        check_report_status(report_id)
        download_report(report_id)
    else:
        print("Invalid mode selected. Exiting.")
        exit(1)


if __name__ == "__main__":
    main()
