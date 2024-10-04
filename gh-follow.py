import requests
from config import GITHUB_TOKEN, USERNAME

FOLLOWER_FOLLOWING_RATIO_THRESHOLD = 10
NONMUTUAL_SPAMMER_RATIO_THRESHOLD = 0.5

def get_user_info(username: str) -> dict:
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
    }
    url = f'https://api.github.com/users/{username}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_nonmutual_followers(username: str) -> None:
    followers_url = f'https://api.github.com/users/{username}/followers'
    following_url = f'https://api.github.com/users/{username}/following'

    followers = set(get_github_users(followers_url))
    following = set(get_github_users(following_url))

    non_mutual_followers = followers - following
    non_mutual_followers_count = len(non_mutual_followers)

    mutual_followers = followers & following
    mutual_followers_count = len(mutual_followers)

    print(f'  {username} non mutual followers count: {non_mutual_followers_count}')
    print(f'  {username} mutual followers count: {mutual_followers_count}')

    # Calculate ratio and determine if user might be a spammer
    try:
        ratio = non_mutual_followers_count / mutual_followers_count
        print(f'  Ratio of non-mutual to mutual followers: {ratio:.2f}')
        if ratio > NONMUTUAL_SPAMMER_RATIO_THRESHOLD:
            print(f'  {username} might be a spammer based on non-mutual followers ratio.\n')
        else:
            print(f'  {username} probably is not a spammer based on non-mutual followers ratio.\n')
    except ZeroDivisionError:
        print(f'  {username} might be a spammer: no mutual followers.\n')

def check_spammer(username: str) -> None:
    try:
        user_info = get_user_info(username)

        followers_count = user_info['followers']
        following_count = user_info['following']

        print(f'  User: {username}')
        print(f'  Number of followers: {followers_count}')
        print(f'  Number of following: {following_count}')

        if following_count == 0:
            print(f'  {username} might be a spammer: zero following')
        else:
            ratio = followers_count / following_count
            print(f'  Follower to following ratio: {ratio:.2f}')
            if ratio > FOLLOWER_FOLLOWING_RATIO_THRESHOLD:
                print(f'  {username} might be a spammer based on the ratio.\n')
            else:
                print(f'  {username} probably is not a spammer based on the ratio\n')

        if followers_count < 400 and following_count < 800:
            get_nonmutual_followers(username)

        print()
    except requests.HTTPError as e:
        print(f"Failed to get info for {username}: {e}")

def get_github_users(url: str) -> list:
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
    }
    users = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        users.extend(response.json())
        if 'next' not in response.links:
            break
        url = response.links['next']['url']
    return [user['login'] for user in users]

def main() -> None:
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
