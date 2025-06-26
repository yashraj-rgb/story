import requests

INSTAGRAM_SESSIONID = '73381388190%3AK1N3C9skVgyjsS%3A18%3AAYf1-OqNFvSD66aIAqapGTIX9URwz1kcRE9HKh24388'

HEADERS = {
    'User-Agent': 'Instagram 255.0.0.19.109 (iPhone14,3; iOS 15_1; en_US; en-US; scale=3.00; 1170x2532; 304799434)',
    'Cookie': f'sessionid={INSTAGRAM_SESSIONID};',
    'X-IG-App-ID': '936619743392459',  # Optional but helpful for some endpoints
}

def get_user_id(username):
    url = f'https://i.instagram.com/api/v1/users/web_profile_info/?username={username}'
    resp = requests.get(url, headers=HEADERS)

    print("Status code:", resp.status_code)
    print("Response body:", resp.text)  # Add this to debug

    try:
        data = resp.json()
        user_id = data['data']['user']['id']
        return user_id
    except Exception as e:
        print("Failed to parse response:", e)
        return None


def get_stories(user_id):
    url = f'https://i.instagram.com/api/v1/feed/reels_media/?reel_ids={user_id}'
    resp = requests.get(url, headers=HEADERS)
    data = resp.json()
    media_urls = []
    reels = data.get('reels', {})
    if str(user_id) in reels:
        items = reels[str(user_id)]['items']
        for item in items:
            if item['media_type'] == 1:
                media_urls.append(item['image_versions2']['candidates'][0]['url'])
            elif item['media_type'] == 2:
                media_urls.append(item['video_versions'][0]['url'])
    return media_urls

if __name__ == '__main__':
    username = input("Enter Instagram username: ")
    user_id = get_user_id(username)
    print(f'User ID: {user_id}')
    stories = get_stories(user_id)
    print("Story media URLs:")
    for url in stories:
        print(url)
