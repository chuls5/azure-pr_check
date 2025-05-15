# Azure DevOps PR Work Item Checker 🔍

This script checks all pull requests across multiple repositories in an Azure DevOps project and reports those without associated work items.

## 🌟 Features

- Scans multiple repositories in one run
- Creates a beautiful markdown report with tables
- Provides a summary of PRs missing work items
- Easy to configure with environment variables

## 📋 Prerequisites

You'll need these packages:

- `requests` - For making API calls to Azure DevOps
- `python-dotenv` - For loading environment variables
- `base64` - For encoding authentication (built-in)
- `datetime` - For timestamping reports (built-in)

Install required packages:

````bash
## ⚙️ Configuration

Create a `.env` file with the following variables:

```ini
# Azure DevOps credentials
AZURE_ORGANIZATION=yourorganization
AZURE_PROJECT=yourproject
AZURE_PAT=yourpersonalaccesstoken

# Repository IDs
REPO_NAME_1=repository-guid-1
REPO_NAME_2=repository-guid-2
# Add more repositories as needed
````

### Setting up your Personal Access Token (PAT)

1. Go to Azure DevOps and click on your profile icon in the top right
2. Select "Personal access tokens"
3. Click "New Token"
4. Give it a name like "PR Work Item Checker"
5. Set the organization where you want to use this token
6. For minimum permissions, select:
   - Custom defined
   - Under "Code", select "Read"
7. Set an expiration date
8. Click "Create"
9. Copy the token and add it to your `.env` file

## 🚀 Running the Script

Make sure your `.env` file is set up with all required variables.
Run the script from your terminal:

```bash
python pr_checker.py
```

## 📊 Understanding the Report

The markdown report includes:

- A timestamp of when it was generated
- Results for each repository
- A table of PRs without work items (if any)
- A summary with counts per repository
- Total count of PRs missing work items

## 👩‍💻 Happy Coding! 👨‍💻
