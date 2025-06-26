from flask import Flask, request, jsonify, send_from_directory, Response
import requests
import json

app = Flask(__name__, static_url_path='', static_folder='static')

INSTAGRAM_SESSIONID = '73794078346%3AFdR69z0aFOPNh0%3A0%3AAYf5dp8s-ouVYA61XmTangeqSYBAgoPp2hJXIrtnsg'
HEADERS = {
    'User-Agent': 'Instagram 255.0.0.19.109 (iPhone14,3; iOS 15_1; en_US; en-US; scale=3.00; 1170x2532; 304799434)',
    'Cookie': f'sessionid={INSTAGRAM_SESSIONID};',
    'X-IG-App-ID': '936619743392459',
}

def get_user_profile(username):
    url = f'https://i.instagram.com/api/v1/users/web_profile_info/?username={username}'
    resp = requests.get(url, headers=HEADERS)
    try:
        data = resp.json()['data']['user']
        return data
    except:
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
                media_urls.append({'type': 'image', 'url': item['image_versions2']['candidates'][0]['url']})
            elif item['media_type'] == 2:
                media_urls.append({'type': 'video', 'url': item['video_versions'][0]['url']})
    return media_urls

def get_highlights(user_id):
    tray_url = f'https://i.instagram.com/api/v1/highlights/{user_id}/highlights_tray/'
    tray_resp = requests.get(tray_url, headers=HEADERS)

    if tray_resp.status_code != 200:
        return []

    highlights_data = []
    tray = tray_resp.json().get('tray', [])

    for h in tray:
        highlight_id = h['id']
        title = h.get('title', '')
        cover_url = h.get('cover_media', {}).get('cropped_image_version', {}).get('url', '')

        # Fetch stories inside this highlight
        stories_url = f'https://i.instagram.com/api/v1/feed/reels_media/?reel_ids={highlight_id}'
        stories_resp = requests.get(stories_url, headers=HEADERS)
        stories_json = stories_resp.json()

        highlight_stories = []
        items = stories_json.get('reels', {}).get(highlight_id, {}).get('items', [])
        for item in items:
            if item['media_type'] == 1:
                highlight_stories.append({
                    'type': 'image',
                    'url': item['image_versions2']['candidates'][0]['url']
                })
            elif item['media_type'] == 2:
                highlight_stories.append({
                    'type': 'video',
                    'url': item['video_versions'][0]['url']
                })

        highlights_data.append({
            'id': highlight_id,
            'title': title,
            'cover_url': cover_url,
            'stories': highlight_stories
        })

    return highlights_data

def get_recent_posts(profile_data):
    posts = []
    edges = profile_data.get('edge_owner_to_timeline_media', {}).get('edges', [])
    for edge in edges:
        node = edge['node']
        posts.append({
            'type': 'video' if node.get('is_video') else 'image',
            'url': node.get('display_url', ''),
            'caption': node.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', ''),
            'likes': node.get('edge_liked_by', {}).get('count', 0),
            'comments': node.get('edge_media_to_comment', {}).get('count', 0),
            'shortcode': node.get('shortcode', '')
        })
    return posts

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/stories')
def api_get_stories():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    user_data = get_user_profile(username)
    if not user_data:
        return jsonify({'error': 'User not found'}), 404

    # Debug output
    print(json.dumps(user_data, indent=2))

    user_id = user_data['id']
    stories = get_stories(user_id)
    highlights = get_highlights(user_id)
    posts = get_recent_posts(user_data)

    profile = {
        'id': user_id,
        'username': user_data['username'],
        'full_name': user_data.get('full_name', ''),
        'biography': user_data.get('biography', ''),
        'profile_pic_url': user_data.get('profile_pic_url_hd', ''),
        'follower_count': user_data.get('edge_followed_by', {}).get('count', 0),
        'following_count': user_data.get('edge_follow', {}).get('count', 0),
        'stories': stories,
        'highlights': highlights,
        'posts': posts
    }

    return jsonify(profile)

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return 'No URL provided', 400
    try:
        resp = requests.get(url, headers=HEADERS, stream=True)
        content_type = resp.headers.get('Content-Type', 'application/octet-stream')
        return Response(resp.content, content_type=content_type)
    except:
        return 'Failed to load media', 500

if __name__ == '__main__':
    app.run(debug=True)
