import requests
import re
import pymysql

def getName(html_url):
    p_name = re.compile(r".+/(.+?)/(.+?)/")
    name = p_name.findall(html_url)
    if len(name) > 0:
        return name[0][0] + "/" + name[0][1]
    else:
        return "fail"

def getDockerfileFromHtml(html_url):
    _url = html_url+"~/dockerfile/"
    #print(_url)
    req = requests.get(url=_url)

    p_dockerfile_div = re.compile(r"<div class=\"hljs\".+?>([\s\S]+?)</div>")
    res_div = p_dockerfile_div.findall(req.text, re.M)

    p_dockerfile_content = re.compile(r"<span.+?>|</span>")

    if len(res_div) > 0:
        res_content = re.subn(p_dockerfile_content, "", res_div[0])
        res_content = res_content[0].replace("\"","\\\"")
        if len(res_content) > 0:
            return res_content
        else:
            return "fail"
    else:
        return "fail"

db = pymysql.connect("112.74.190.220","dockerteam","docker","test")

cursor = db.cursor()
cursor.execute("SELECT url from test.images LIMIT 50")
count = 0
for row in cursor.fetchall():
    count = count + 1
    print(count)
    dockerfile_name = getName(row[0])
    print(dockerfile_name)

    dockerfile_content = getDockerfileFromHtml(row[0])
    #print(docker_file_content)

    if dockerfile_content != "fail":
        try:
            cursor.execute("INSERT INTO dockerfile(dockerfile_name, dockerfile_content) VALUES(\"%s\",\" %s\")" % (
            dockerfile_name, dockerfile_content))
            db.commit()
        except Exception as e:
            print(e)

db.commit()
db.close()

