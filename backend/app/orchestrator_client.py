import requests

# Your prod credentials
api_key = "jpysL6EkLhp4vd_Tn5ecUVYxaB-ZxvjkWMfgJUgPJJvR"
instance_url = "https://api.jp-tok.watson-orchestrate.cloud.ibm.com/instances/0b4a8b3e-ac8a-4ee1-be2e-ac89c2a6a1e4"

# 1. Get the IAM Bearer Token (standard IBM Cloud IAM)
token_url = "https://iam.cloud.ibm.com"
token_resp = requests.post(token_url, data={
    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
    "apikey": api_key
})
bearer_token = token_resp.json()["access_token"]

# 2. Call the Orchestrate Agents API
# Adjust URL if your version/instance path differs
agents_endpoint = f"{instance_url}/v1/agents"
headers = {"Authorization": f"Bearer {bearer_token}"}

response = requests.get(agents_endpoint, headers=headers)
print(response.json())
