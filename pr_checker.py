import os
from dotenv import load_dotenv
import requests
import base64
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get Azure DevOps credentials from environment variables
organization = os.getenv('AZURE_ORGANIZATION')
project = os.getenv('AZURE_PROJECT')
pat = os.getenv('AZURE_PAT')

# Define repositories to check - consider moving these to config file or environment variables as well
repositories = {
    'enow-admin': os.getenv('REPO_ENOW_ADMIN'),
    'enow-backend': os.getenv('REPO_ENOW_BACKEND'),
    'enow-frontend': os.getenv('REPO_ENOW_FRONTEND'),
    'enow-playwright': os.getenv('REPO_ENOW_PLAYWRIGHT'),
    'enow-terraform': os.getenv('REPO_ENOW_TERRAFORM'),
    'enow-terraform-modules': os.getenv('REPO_ENOW_TERRAFORM_MODULES')
}

# Create a markdown file for results
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
md_filename = f"pull_requests_report_{current_time}.md"
md_file = open(md_filename, "w", encoding="utf-8")

# Write Markdown header
md_file.write(f"# Pull Requests Without Work Items Report\n\n")
md_file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
md_file.write(f"Organization: {organization}\n")
md_file.write(f"Project: {project}\n\n")
md_file.write(f"## Results\n\n")

# Encode PAT for authorization header
encoded_pat = base64.b64encode(f":{pat}".encode()).decode()

# Set up the headers for the request
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {encoded_pat}'
}

# Track total PRs without work items
total_prs_without_work_items = 0
repo_results = {}

# Iterate through each repository
for repo_name, repo_id in repositories.items():
    print(f"\n{'=' * 50}")
    print(f"Checking repository: {repo_name}")
    print(f"{'=' * 50}")
    
    # Also write to markdown
    md_file.write(f"### Repository: {repo_name}\n\n")
    
    # Get all pull requests for this repository
    pr_url = f'https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repo_id}/pullrequests?api-version=6.0'
    pr_response = requests.get(pr_url, headers=headers)
    
    if pr_response.status_code != 200:
        error_msg = f"Error accessing repository {repo_name}: {pr_response.status_code}"
        print(error_msg)
        print(f"Response: {pr_response.text}")
        md_file.write(f"{error_msg}\n\n")
        continue
    
    pull_requests = pr_response.json()['value']
    
    if not pull_requests:
        no_pr_msg = f"No pull requests found in {repo_name}"
        print(no_pr_msg)
        md_file.write(f"{no_pr_msg}\n\n")
        continue
    
    found_msg = f"Found {len(pull_requests)} pull requests in {repo_name}"
    print(found_msg)
    md_file.write(f"{found_msg}\n\n")
    
    # Check each pull request for related work items
    prs_without_work_items = []
    
    for pr in pull_requests:
        pr_id = pr['pullRequestId']
        work_items_url = f'https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repo_id}/pullrequests/{pr_id}/workitems?api-version=6.0'
        work_items_response = requests.get(work_items_url, headers=headers)
        
        if work_items_response.status_code != 200:
            error_msg = f"Error checking work items for PR {pr_id}: {work_items_response.status_code}"
            print(f"  {error_msg}")
            md_file.write(f"  {error_msg}\n\n")
            continue
            
        work_items = work_items_response.json()['value']
        
        if not work_items:  # If there are no related work items
            prs_without_work_items.append(pr)
    
    # Output the pull requests without work items for this repository
    if prs_without_work_items:
        found_msg = f"Found {len(prs_without_work_items)} PRs without work items in {repo_name}:"
        print(f"\n{found_msg}")
        md_file.write(f"#### {found_msg}\n\n")
        
        # Create a markdown table
        md_file.write("| PR ID | Title | Created By | Created Date | URL |\n")
        md_file.write("|-------|-------|------------|--------------|-----|\n")
        
        for pr in prs_without_work_items:
            creator = pr['createdBy']['displayName'] if 'createdBy' in pr else 'Unknown'
            created_date = pr['creationDate'].split('T')[0] if 'creationDate' in pr else 'Unknown date'
            pr_url = pr['url'].replace("_apis/git/repositories", "_git").replace("pullRequests", "pullrequest")
            web_url = pr_url.split("?")[0]
            
            # Console output
            print(f"  PR #{pr['pullRequestId']}: {pr['title']}")
            print(f"    Created by: {creator} on {created_date}")
            print(f"    URL: {web_url}")
            print()
            
            # Markdown table row
            md_file.write(f"| #{pr['pullRequestId']} | {pr['title']} | {creator} | {created_date} | [Link]({web_url}) |\n")
        
        md_file.write("\n")
        total_prs_without_work_items += len(prs_without_work_items)
        repo_results[repo_name] = len(prs_without_work_items)
    else:
        all_good_msg = f"All pull requests in {repo_name} have associated work items! 👍"
        print(all_good_msg)
        md_file.write(f"#### {all_good_msg}\n\n")
        repo_results[repo_name] = 0

# Write summary to Markdown
md_file.write("## Summary\n\n")
md_file.write("| Repository | PRs Without Work Items |\n")
md_file.write("|------------|------------------------|\n")

for repo, count in repo_results.items():
    md_file.write(f"| {repo} | {count} |\n")

md_file.write(f"\n**Total PRs Without Work Items: {total_prs_without_work_items}**\n")

# Console summary
print(f"\n{'=' * 50}")
print(f"SUMMARY: Found {total_prs_without_work_items} total PRs without work items across all repositories")
print(f"Results written to {md_filename}")
print(f"{'=' * 50}")

# Close the file
md_file.close()
