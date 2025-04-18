from dotenv import load_dotenv
load_dotenv()
import requests
import json
import random
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Authorization": "Bearer " + GITHUB_TOKEN,
}

def get_random_id(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"

    response = requests.get(url, headers=headers)
    # 检查响应状态码
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} - {response.text}")
    # 将响应内容转换为JSON格式
    data = json.loads(response.text)

    issues_num = len(data)
    if issues_num == 0:
        raise Exception("No issues found in the repository.")
    # 随机选择一个issue
    issue_index = random.randint(0, issues_num - 1)
    random_issue = data[issue_index]
    issue_id = random_issue["number"]
    return [issue_id, random_issue["comments"]]

def get_post_data(owner, repo, post_id, comment_id):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{post_id}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} - {response.text}")
    data = response.json()
    data_str = "Title: "+ data["title"] + "\n\n"
    data_str += "User @"+ data["user"]["login"] + ":\n"+data["body"] + "\n\n"
    comment_url = data["comments_url"]
    response = requests.get(comment_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} - {response.text}")
    comments = response.json()
    data_str += "Comments:\n"
    j=0
    for i in comments:
        if len(data_str) > 4096 or j >= comment_id: 
            break
        username = i["user"]["login"]
        body = i["body"]
        data_str += f"User @{username}: \n{body}\n\n"
        j += 1
    return data_str

def send_post_data(owner, repo, post_id, data_file):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{post_id}/comments"
    with open(data_file, 'r', encoding='utf-8') as file:
        # 读取markdown文本内容
        markdown_content = file.read()
        # 使用json模块正确处理数据，自动进行转义
        data = json.dumps({"body": markdown_content})
        # 发送请求
        response = requests.post(url, headers=headers, data=data)
        if response.status_code != 201:
            raise Exception(f"Error: {response.status_code} - {response.text}")
    return response.status_code

if __name__ == "__main__":
    owner = "chenxiex"
    repo = "test"
    send_post_data(owner, repo, 1, "test.txt")