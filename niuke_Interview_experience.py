# -*- coding = UTF-8 #-*-
import os
import re
import requests
import html2text as ht


headers = {
        'authority': 'gw-c.nowcoder.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://www.nowcoder.com',
        'referer': 'https://www.nowcoder.com/',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }


def get_and_save_contents(spath, text_id):
    """
    获取本篇面经的内容，并转换为MD格式，剔除与面经无关信息后，存储为md文件
    :param spath: 存储地址
    :param text_id: 面经ID
    :存储面经的内容
    """
    url = "https://www.nowcoder.com/discuss/" + str(text_id)
    url_content = requests.get(url, headers=headers).text
    # 获取面经的关键词
    keywords = re.findall('<meta name="keywords" content="(.*?)"/>', url_content)[0]
    # 获取面经的title
    title = re.findall('<title>(.*?)_牛客网</title>', url_content)[0]
    print(f"成功获取面经：{title}")
    # 剔除标题中的标点符号
    r = "[：_.!+-=——,$%^，。？、~@#￥%……&*《》<>「」|{}【】()/]"
    title = re.sub(r, '_', title).replace(" ", "")
    # 将HTML转为markdown格式
    text_maker = ht.HTML2Text()
    mdtext = text_maker.handle(url_content)
    final_mdtext = delete_invaild_info(mdtext)
    # 在markdown内容最后添加上关键词
    final_mdtext += f"\nkeywords:{keywords}\n"
    with open(os.path.join(spath, title+".md"), "w", encoding="utf-8") as fh:
        fh.write(final_mdtext)

# 删除无效的信息
def delete_invaild_info(mdtext):
    mdtexts = mdtext.split("\n")
    final_mdtext = ""
    flag = 0
    for line in mdtexts:
        if line.startswith("# "):
            flag = 1
        if line.startswith("提示 "):
            flag = 0
        if flag:
            final_mdtext += "\n" + line
    return final_mdtext


# 算法工程师精选面经组合，jobId = "645"
def get_job_experience(page):
    json_data = {"type": "all",
                 "query": "NLP算法面经",
                 "page": page,
                 "tag": [{"id": 818}],
                 "order": "",
                 "gioParams": {
                     "logid_var": "7B535194127704DAD4163CC2EF16241C-1695399854066",
                     "sessionID_var": "6663_1695224608938_7034",
                     "searchFrom_var": "搜索页输入框",
                     "searchEnter_var": "主站"
                               }
                 }
    response = requests.post(
        'https://gw-c.nowcoder.com/api/sparta/pc/search',
        headers=headers,
        json=json_data,
    )
    return response.json()

# 获取所有的知识ID
def get_text_ids(topNumGroup):
    # 获取返回内容
    text_ids = []
    for i in range(1, topNumGroup + 1):
        res = get_job_experience(i)
        records = res['data']['records']
        for i, record in enumerate(records):
            try:
                text_id = record['entityDataId']
            except:
                continue
            # 面经ID
            text_ids.append(text_id)
    return text_ids


if __name__ == '__main__':
    res = get_job_experience(page=1)
    pages = res.get("data", {}).get("totalPage", 0)
    # 获取文章代号
    jobIDs = get_text_ids(pages)
    spath = "./mds"
    for text_id in jobIDs:
        get_and_save_contents(spath, text_id)