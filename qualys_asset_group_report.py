import requests
import getpass
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth
import time
import os

# Constants
QUALYS_BASE_URL = 'https://qualysapi.qualys.com'
HEADERS = {'X-Requested-With': 'Python Script'}
OUTPUT_FORMAT = 'excel'

# Prompt for credentials
USERNAME = input("Qualys Username: ").strip()
PASSWORD = getpass.getpass("Qualys Password: ").strip()

# Select mode
print("\nSelect operation:")
print("1 - Launch new report")
print("2 - Retrieve existing report by ID")
mode = input("Enter option [1 or 2]: ").strip()


def check_report_status(report_id):
    url = f'{QUALYS_BASE_URL}/api/2.0/fo/report/?action=list&id={report_id}'
    while True:
        response = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        root = ET.fromstring(response.text)
        status_elem = root.find('.//ITEM[@key="status"]')
        if status_elem is not None:
            status = status_elem.text
            if status == "Finished":
                print("✅ Report is ready for download.")
                return
            else:
                print(f"⌛ Report status: {status} (retrying in 10 minutes)")
                time.sleep(600)  # Wait 10 minutes
        else:
            raise Exception(f"❌ Could not determine report status. Response:\n{response.text}")


def download_report(report_id, report_title=None):
    url = f'{QUALYS_BASE_URL}/api/2.0/fo/report/?action=fetch&id={report_id}'
    response = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    if not report_title:
        report_title = f"Qualys_Report_{report_id}"
    filename = f"{report_title}.xlsx"
    with open(filename, 'wb') as f:
        f.write(response.content)
    print(f"📄 Report downloaded: {filename}")


def launch_report():
    # Prompt for template ID
    template_id = input("Enter the Report Template ID: ").strip()

    # Input method
    print("\nSelect target input method:")
    print("1. Use Asset Group ID(s)")
    print("2. Use Host File (host.txt)")
    input_mode = input("Enter option [1 or 2]: ").strip()

    target_param = {}

    if input_mode == "1":
        group_ids = input("Enter one or more Asset Group IDs (comma-separated): ").strip()
        target_param['asset_group_ids'] = group_ids
    elif input_mode == "2":
        host_file_path = input("Enter path to host file (one IP or FQDN per line): ").strip()

        if not os.path.exists(host_file_path):
            print(f"❌ File not found: {host_file_path}")
            exit(1)

        with open(host_file_path, 'r') as f:
            hosts = [line.strip() for line in f if line.strip()]

        if not hosts:
            print("❌ Host file is empty.")
            exit(1)

        host_list = ",".join(sorted(set(hosts)))
        target_param['ips'] = host_list
    else:
        print("❌ Invalid option.")
        exit(1)

    # Title
    report_title = f"Qualys_Report_{int(time.time())}"

    url = f'{QUALYS_BASE_URL}/api/2.0/fo/report/'
    data = {
        'action': 'launch',
        'report_title': report_title,
        'report_type': 'Scan',
        'template_id': template_id,
        'output_format': OUTPUT_FORMAT,
    }

    # Include target param
    if 'ips' in target_param:
        data['ips'] = target_param['ips']
    else:
        data['asset_group_ids'] = target_param['asset_group_ids']

    response = requests.post(url, headers=HEADERS, auth=HTTPBasicAuth(USERNAME, PASSWORD), data=data)

    if not response.text.strip():
        raise Exception("❌ Empty response from Qualys API.")

    try:
        root = ET.fromstring(response.text)
        report_id_elem = root.find('.//ITEM[@key="id"]')
        if report_id_elem is not None:
            report_id = report_id_elem.text
            print(f"🆔 Report launched. Report ID: {report_id}")
            return report_id, report_title
        else:
            print("🚫 Response from API:")
            print(response.text)
            raise Exception("❌ Report ID not found in response.")
    except ET.ParseError as e:
        raise Exception(f"❌ Failed to parse XML response: {e}\nRaw Response:\n{response.text}")


def main():
    if mode == "1":
        print("🚀 Launching new report...")
        report_id, title = launch_report()
        check_report_status(report_id)
        download_report(report_id, title)
    elif mode == "2":
        report_id = input("Enter existing Report ID to check/download: ").strip()
        check_report_status(report_id)
        download_report(report_id)
    else:
        print("❌ Invalid operation.")
        exit(1)


if __name__ == '__main__':
    main()
