import requests

def send_comment():
    url = "https://api.weibo.com/2/comments/create.json"
    params = {
        'access_token': '2.00XywhYI0xvh2e66647bf75c0tvgBF',	# 刚才请求到的access_token
        'id': '4908623132888539',
        'comment':'12334',
        'rip':'111.42.148.194'
    }

    requests.post(url=url, data=params)
    

send_comment()