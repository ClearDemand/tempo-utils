import requests
import datetime
import os
import argparse
import sys

class TempoWorklogCopier:
    """
    Uses the Tempo API to read the worklogs for the source week and copy them to the destination
    week.
    """

    def __init__(self, api_token, user_account_id, dry_run=False):
        """
        Class constructor sets up the URL and auth headers as well as capturing
        the required parameters.
        """
        self.api_token = api_token
        self.user_account_id = user_account_id
        self.dry_run = dry_run
        self.base_url = "https://api.tempo.io/4"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def get_worklogs_for_week(self, start_date):
        """
        Uses the Tempo API to retrieve all of the worklogs for a given week.
        """
        end_date = start_date + datetime.timedelta(days=6)
        url = f"{self.base_url}/worklogs/user/{self.user_account_id}?from={start_date}&to={end_date}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()["results"]

    def prepare_new_worklog(self, worklog, delta_days):
        """
        Using an existing worklog as a model, a new worklog object is created
        by copying elements from a source object.
        """
        original_date = datetime.datetime.strptime(worklog["startDate"], "%Y-%m-%d").date()
        new_date = original_date + delta_days

        attribute_values = worklog.get("attributes", {}).get("values", [])

        return {
            "attributes": attribute_values,
            "authorAccountId": self.user_account_id,
            "issueId": worklog["issue"]["id"],
            "timeSpentSeconds": worklog["timeSpentSeconds"],
            "startDate": new_date.strftime("%Y-%m-%d"),
            "startTime": worklog["startTime"],
            "description": worklog.get("description", "Copied worklog")
        }

    def post_worklog(self, payload):
        """
        Call the Tempo API to create new worklogs.
        """
        url = f"{self.base_url}/worklogs"
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code >= 200 and response.status_code <= 299:
            print(f"✅ Created worklog for {payload['startDate']} - {payload['issueId']}")
        else:
            print(f"❌ Failed to create worklog: {response.status_code} {response.text}")

    def copy_week(self, source_start, destination_start):
        """
        Copies the worklogs from the week of the source_start date and creates new work logs
        in the week of the destination_start
        """
        print(f"Fetching worklogs from {source_start} to {source_start + datetime.timedelta(days=6)}...")
        worklogs = self.get_worklogs_for_week(source_start)

        if not worklogs:
            print("No worklogs found for the source week. Exiting.")
            return

        print(f"Found {len(worklogs)} worklogs to copy...")

        delta_days = destination_start - source_start

        for worklog in worklogs:
            new_payload = self.prepare_new_worklog(worklog, delta_days)

            if self.dry_run:
                print(f"[Dry Run] Would create worklog: {new_payload}")
            else:
                self.post_worklog(new_payload)

        if self.dry_run:
            print("✅ Dry run complete. No changes were made.")
        else:
            print("🎉 All worklogs copied successfully!")

def parse_args():
    '''
    Parse the arguments requrired for this application, including the source date, the destination
    date, and an optional "dry-run" flag.
    '''
    parser = argparse.ArgumentParser(description="Copy Tempo worklogs from one week to another.")
    parser.add_argument("--source", required=True, help="Source week start date (YYYY-MM-DD)")
    parser.add_argument("--dest", required=True, help="Destination week start date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be copied without actually creating worklogs")
    return parser.parse_args()

def main():
    '''
    Entry point for the application.  For security reasons, we capture the credential information
    from environment variables.
    '''
    if not os.getenv("TEMPO_API_TOKEN"):
        print("Error: TEMPO_API_TOKEN environment variable not set.")
        sys.exit(1)

    if not os.getenv("JIRA_USER_ACCOUNT_ID"):
        print("Error: JIRA_USER_ACCOUNT_ID environment variable not set.")
        sys.exit(1)

    args = parse_args()

    try:
        source_start = datetime.datetime.strptime(args.source, "%Y-%m-%d").date()
        destination_start = datetime.datetime.strptime(args.dest, "%Y-%m-%d").date()
    except ValueError:
        print("Error: Dates must be in YYYY-MM-DD format.")
        sys.exit(1)

    copier = TempoWorklogCopier(
        api_token=os.getenv("TEMPO_API_TOKEN"),
        user_account_id=os.getenv("JIRA_USER_ACCOUNT_ID"),
        dry_run=args.dry_run
    )

    copier.copy_week(source_start, destination_start)

if __name__ == "__main__":
    main()

