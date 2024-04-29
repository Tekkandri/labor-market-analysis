import requests
import re
import random
from time import sleep
from fake_useragent import UserAgent
import csv

HH_VAC_LIST = ["bi","data","sql","аналитик данных","analyst"]
REGEXP_LIST = ["bi","analyst","аналитик","данных","sql","data"]

proxy_1 = {
    "http":"http://Le9YJs:onEjhN@45.129.6.81:8000",
    "https":"http://Le9YJs:onEjhN@45.129.6.81:8000"
}
proxy_2 = {
    "http":"http://Le9YJs:onEjhN@45.129.5.186:8000",
    "https":"http://Le9YJs:onEjhN@45.129.5.186:8000"
}
proxies = [proxy_1, proxy_2]

headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 YaBrowser/20.12.2.105 Yowser/2.5 Safari/537.36"
}

def hh_parse():
    jobs = []
    session = requests.Session()
    HH_ID_LIST = []
    for vac in HH_VAC_LIST:

        ua = UserAgent()
        url = f"https://api.hh.ru/vacancies?text={vac}&only_with_salary=true"
        session.cookies.clear()
        head = {'user-agent': ua.random}
        resp = session.get(url, headers=head, proxies=proxies[random.randrange(0, 2)]).json()

        try:
            pages = resp["pages"]
            print(pages)
            for page in range(pages):
                sleep(random.randrange(1, 3))

                ua = UserAgent()
                url = f"https://api.hh.ru/vacancies?text={vac}&page={page}&only_with_salary=true"
                session.cookies.clear()
                resp = session.get(url, headers={'user-agent': ua.random},
                                   proxies=proxies[random.randrange(0, 2)]).json()

                for item in resp["items"]:
                    name = item["name"]
                    id = item["id"]
                    try:
                        city = item["area"]["name"]
                    except:
                        city = None

                    for reg in REGEXP_LIST:
                        regexp = re.compile(reg)
                        if regexp.findall(str(name).lower()):
                            if id not in HH_ID_LIST:
                                HH_ID_LIST.append(id)
                                print(name)
                                if item["salary"] != None:
                                    cur = item["salary"]["currency"]
                                    if item["salary"]["from"] != None:
                                        min_salary = item["salary"]["from"]
                                    else:
                                        min_salary = None
                                    if item["salary"]["to"] != None:
                                        max_salary = item["salary"]["to"]
                                    else:
                                        max_salary = None
                                    jobs.append({
                                        "name": name,
                                        "max_salary": f"{max_salary}",
                                        "min_salary": f"{min_salary}",
                                        "currancy": cur,
                                        "location": city,
                                    })
                                else:
                                    jobs.append({
                                            "name": name,
                                            "min_salary": None,
                                            "max_salary": None,
                                            "currancy": None,
                                            "location": city
                                        })
        except Exception as e:
            print(e)
    res_list = [i for n, i in enumerate(jobs)
                if i not in jobs[n + 1:]]
    return res_list

if __name__ == "__main__":
    with open("hhru.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter="|")
        writer.writerow(["Name", "Min_salary", "Max_salary", "Currancy", "Location"])
        for job in hh_parse():
            writer.writerow([job["name"], job["min_salary"], job["max_salary"], job["currancy"],job["location"]])