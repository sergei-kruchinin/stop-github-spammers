import requests
from config import GITHUB_TOKEN, USERNAME

FOLLOWER_FOLLOWING_RATIO_THRESHOLD = 10

def get_github_users(url):
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
    }
    users = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        users.extend(response.json())
        url = response.links.get('next', {}).get('url')
    return [user['login'] for user in users]

def check_spammer(username):
    followers_url = f'https://api.github.com/users/{username}/followers'
    following_url = f'https://api.github.com/users/{username}/following'

    followers = get_github_users(followers_url)
    following = get_github_users(following_url)

    followers_count = len(followers)
    following_count = len(following)

    print(f'User: {username}')
    print(f'Number of followers: {followers_count}')
    print(f'Number of following: {following_count}')

    if following_count == 0:
        print(f'{username} might be a spammer: zero following')
    else:
        ratio = followers_count / following_count
        print(f'Follower to following ratio: {ratio:.2f}')
        if ratio > FOLLOWER_FOLLOWING_RATIO_THRESHOLD:
            print(f'{username} might be a spammer based on the ratio.\n')
        else:
            print(f'{username} probably is not a spammer based on the ratio\n')
    print()

def main():
    followers_url = f'https://api.github.com/users/{USERNAME}/followers'
    following_url = f'https://api.github.com/users/{USERNAME}/following'

    followers = set(get_github_users(followers_url))
    following = set(get_github_users(following_url))

    followers_count = len(followers)
    print('Followers count:', followers_count)

    following_count = len(following)
    print('Following count:', following_count)

    not_mutual_followers = followers - following
    non_followers = following - followers

    print('Users who have followed you but you have not followed back:')
    for user in not_mutual_followers:
        print(user)

    print('Users you are following but who haven\'t followed you back:')
    for user in non_followers:
        print(user)

    print('Checking for spammers among users who have followed you but you have not followed back:')
    for user in not_mutual_followers:
        check_spammer(user)

    print('Checking for spammers among users you are following but who haven\'t followed you back:')
    for user in non_followers:
        check_spammer(user)

if __name__ == '__main__':
    main()
