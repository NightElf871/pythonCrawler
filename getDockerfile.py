import requests
import re
import pymysql

def getName(html_url):
    p_name = re.compile(r".+/(.+?)/(.+?)/")
    name = p_name.findall(html_url)
    if len(name) > 0:
        return name[0][0] + "/" + name[0][1]
    else:
        return ""

def getDockerfileFromHtml(html_url):
    _url = html_url+"~/dockerfile/"
    #print(_url)
    req = requests.get(url=_url)

    p_github_url = re.compile(r"github.com/(.+?)\"")
    res_github_url = p_github_url.findall(req.text)
    if len(res_github_url) > 0:
        res_github_url = res_github_url[0]
    else:
        res_github_url = ""

    p_dockerfile_div = re.compile(r"<div class=\"hljs\".+?>([\s\S]+?)</div>")
    res_div = p_dockerfile_div.findall(req.text, re.M)

    p_dockerfile_content = re.compile(r"<span.+?>|</span>")

    if len(res_div) > 0:
        res_content = re.subn(p_dockerfile_content, "", res_div[0])
        res_content = res_content[0].replace("\"","\\\"")
        if len(res_content) == 0:
            res_content = ""
    else:
        res_content = ""

    return res_content, res_github_url

db = pymysql.connect("[ip]","dockerteam","docker","test")

cursor = db.cursor()
cursor.execute("SELECT url from test.images")
count = 0
for row in cursor.fetchall():
    count = count + 1
    print(count)
    dockerfile_name = getName(row[0])
    print(dockerfile_name)

    dockerfile_content, github_url = getDockerfileFromHtml(row[0])
    #print(docker_file_content)
    #print(github_url)

    if dockerfile_content != "":
        try:
            cursor.execute("INSERT INTO dockerfile(dockerfile_name, github_url, dockerfile_content) VALUES(\"%s\", \" %s\", \"%s\")" % (dockerfile_name, github_url, dockerfile_content))
            db.commit()
            print("insert into database")
        except Exception as e:
            print(e)
    else:
        print("no dockerfile content, ignore")

db.commit()
db.close()

