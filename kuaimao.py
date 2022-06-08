import requests
import execjs
from hashlib import md5
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import os


class Km:
    def __init__(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.session.keep_alive = False

        with open('cbc.js') as f:
            jsText = f.read()
        self.cbc_js = execjs.compile(jsText)

        self.Tpool = ThreadPoolExecutor(max_workers=10)

    def cbc_Encrypt(self, data):
        return self.cbc_js.call('AES_Encrypt', data)

    def cbc_Decrypt(self, data):
        return self.cbc_js.call('AES_Decrypt', data)

    def get_all_v(self, urlId, uId=0):
        if urlId == 'getUserInfo':
            url = f'https://ua1sf4m8.com/api/users/{urlId}'
        else:
            url = f'https://ua1sf4m8.com/api/videos/{urlId}'
        page = 1
        video_all = []
        while True:
            if urlId == 'getUserInfo':
                data = f'{{"page":{page},"perPage":12,"uId":"{uId}","meId":"60364099"}}'
            else:
                data = f'{{"page":{page},"perPage":19}}'
            data = self.cbc_Encrypt(data).upper()
            n = f'data={data}maomi_pass_xyz'
            sig = md5(n.encode()).hexdigest()
            datas = {
                'data': data,
                'sig': sig
            }
            resp = self.session.post(url, data=datas)
            value = self.cbc_Decrypt(resp.text)
            if urlId == 'getUserInfo':
                video_list = json.loads(value)['data']['video_list']
            else:
                video_list = json.loads(value)['data']['list']
            if len(video_list) == 0:
                break
            for index, video in enumerate(video_list):
                try:
                    mv_title = video['mv_title'] + str(index)
                    mv_play_url = video['mv_play_url']
                    mv_url = 'https://video.km7p7.xyz/' + re.findall('(uploads.*?mp4)', mv_play_url)[0]
                    video_all.append([mv_title, mv_url])
                    print(f'\r爬取了{len(video_all)}个视频信息了', end='')
                except:
                    pass
            page += 1

        return video_all

    def video_down(self, video):
        url = video[1]
        title = video[0]
        if not os.path.exists('快猫视频'):
            os.mkdir('快猫视频')
        resp = self.session.get(url)
        with open(f'快猫视频/{title}.mp4', 'wb') as f:
            f.write(resp.content)

    def run(self, urlId, uId=0):
        video_all = self.get_all_v(urlId, uId=uId)
        tasks = [self.Tpool.submit(self.video_down, video) for video in video_all]
        count = 1
        for _ in as_completed(tasks):
            print(f'\r下载完成进度：{int(count / len(tasks) * 100)}%', end='')
            count += 1


if __name__ == '__main__':
    listHot = 'listHot'
    listAll = 'listAll'
    getUserInfo = 'getUserInfo'
    km = Km()
    # 爬取用户所有视频，uId为用户id
    km.run(getUserInfo, uId=39321400)
    # 爬取热门视频
    km.run(listHot)


