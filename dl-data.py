import httpx
from bs4 import BeautifulSoup
import os
import json


def save_html(name, url: str) -> None:
    content = httpx.get(url)

    if not os.path.exists(f"regents_data/{name}"):
        os.mkdir(f"regents_data/{name}")

    with open(f"regents_data/{name}/src.html", "w") as file:
        file.write(content.text)

def index_test_info(name: str):
    with open(f"regents_data/{name}/src.html", "r") as file:
        soup = BeautifulSoup(file)

    tests = []

    for test in soup.select('#content-center > ul > li'):
        test_data = {}
        test_data["date"] = test.text
        test_data["name"] = f"{test.text} Regents in {name}"
        test_data["test_url"] = test.select("ul > li:nth-child(1) > ul > li:nth-child(1) > a")[0].get("href")
        test_data["answers_url"] = test.select("ul > li:nth-child(2) > ul > li:nth-child(1) > a")[0].get("href")
        test_data["rating-guide_url"] = test.select("ul > li:nth-child(3) > a")[0].get("href")
        test_data["model-response_url"] = test.select("ul > li:nth-child(4) > a")[0].get("href")
        tests.append(test_data)

    with open(f"regents_data/{name}/tests.txt", "w") as file:
        testnames = []
        for test in tests:
            testnames.append(test["date"])
        file.write("\n".join(testnames))

    with open(f"regents_data/{name}/tests.json", "w") as file:
        file.write(json.dumps(tests))

def download(url, path: str):
    with open(path, "wb") as file:
        file.write(httpx.get(url).content)

def download_files_for_topic(name: str):
    with open(f"regents_data/{name}/tests.json", "r") as file:
        tests = json.loads(file.read())

    for test in tests:
        os.mkdir(f"regents_data/{name}/{test["date"]}")

        download(test["test_url"], f"regents_data/{name}/{test["date"]}/test.pdf")
        download(test["answers_url"], f"regents_data/{name}/{test["date"]}/answers.pdf")
        download(test["rating-guide_url"], f"regents_data/{name}/{test["date"]}/rating-guide.pdf")
        download(test["model-response_url"], f"regents_data/{name}/{test["date"]}/model-response.pdf")
        with open(f"regents_data/{name}/{test["date"]}/test.json", "w") as file:
            file.write(json.dumps(test))

def main():
    with open(f"regents_data/tests.json", "r") as file:
        courses = json.loads(file.read())

    for course in courses:
        save_html(course["name"], course["url"])
        index_test_info(course["name"])
        download_files_for_topic(course["name"])
