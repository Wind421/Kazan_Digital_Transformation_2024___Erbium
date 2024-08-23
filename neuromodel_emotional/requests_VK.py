import requests
import csv
import time
from tqdm import tqdm

token = 'Token'
version = '5.199'
domain = '-179583563'
with open(r'D:\Python_Projects\hakaton\comments_vk.csv', mode='w', encoding='utf-8') as file:

    writer = csv.writer(file)
    writer.writerow(['id_comment', 'text_comment', 'id_wallpost'])

    offset = 0
    for offset in tqdm(range(0, 15001, 100), desc="Fetching posts"):
        response = requests.get(
            "https://api.vk.com/method/wall.get",
            params={
                'access_token': token,
                'v': version,
                'owner_id': domain,
                'offset': offset,
                'count': 100
            }
        )
        offset+=100
        data = response.json()
        posts_data = data['response']['items']
        
        for post in tqdm(posts_data, desc=f"Processing posts at offset {offset}", leave=False):
            post_id = '3_'+str(post['id'])

            time.sleep(0.1) 
            comments_response = requests.get(
                "https://api.vk.com/method/wall.getComments",
                params={
                    'access_token': token,
                    'v': version,
                    'owner_id': domain,
                    'post_id': post['id']
                }
            )
            comments_data = comments_response.json()
            comments = comments_data['response']['items']
                    
            for comment in comments:
                comment_id = '3_'+str(comment['id'])
                comment_text = comment['text']
                if comment_text != '':
                    writer.writerow([comment_id, comment_text, post_id])
