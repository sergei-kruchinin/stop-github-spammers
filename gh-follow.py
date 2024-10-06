import requests
from config import GITHUB_TOKEN, USERNAME

FOLLOWER_FOLLOWING_RATIO_THRESHOLD = 10
NONMUTUAL_SPAMMER_RATIO_THRESHOLD = 0.5
MAX_FOLLOWERS_TO_GET_THEM = 400
MAX_FOLLOWING_TO_GET_THEM = 800


class GitHubUser:
    username: str
    followers_count: int
    following_count: int
    followers: set
    following: set
    non_mutual_followers: set
    non_mutual_followers_count = int
    mutual_followers = set
    mutual_followers_count = int
    non_followers = set
    non_followers_count = int

    def __init__(self, username: str):
        self.username = username
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
        }
        url = f'https://api.github.com/users/{username}'
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            user_info = response.json()
            self.followers_count = user_info['followers']
            self.following_count = user_info['following']
        except requests.HTTPError as e:
            print(f"Failed to get info for {username}: {e}")

    @staticmethod
    def get_github_users(url: str) -> set:
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
        }
        users = []
        try:
            while url:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                users.extend(response.json())
                if 'next' not in response.links:
                    break
                url = response.links['next']['url']
            return set([user['login'] for user in users])
        except requests.HTTPError as e:
            print(f"Failed to get info by {url}: {e}")

    def get_followers_following(self) -> None:
        followers_url = f'https://api.github.com/users/{self.username}/followers'
        following_url = f'https://api.github.com/users/{self.username}/following'
        self.followers = set(GitHubUser.get_github_users(followers_url))
        self.following = set(GitHubUser.get_github_users(following_url))

    def check_nonmutual_followers(self) -> None:
        self.non_mutual_followers = self.followers - self.following
        self.non_mutual_followers_count = len(self.non_mutual_followers)
        self.mutual_followers = self.followers & self.following
        self.mutual_followers_count = len(self.mutual_followers)
        self.non_followers = self.following - self.followers
        self.non_followers_count = len(self.non_followers)

    def print_non_mutual_count(self):
        print(f'  {self.username} non mutual followers count: {self.non_mutual_followers_count}')
        print(f'  {self.username} mutual followers count: {self.mutual_followers_count}')

    def print_follows(self):
        print(f'  {self.username} number of followers: {self.followers_count}')
        print(f'  {self.username} number of following: {self.following_count}')

    def print_non_mutual_users(self):
        print(f'Users who have followed {self.username} but {self.username} have not followed back:')
        for user in self.non_mutual_followers:
            print(user)

        print(f'Users {self.username} is  following but who haven\'t followed you back:')
        for user in self.non_followers:
            print(user)

    def check_spammer_slow(self):
        # Calculate ratio and determine if user might be a spammer
        if self.mutual_followers_count == 0:
            print(f'  {self.username} might be a spammer: no mutual followers.\n')
            return

        ratio = self.non_mutual_followers_count / self.mutual_followers_count
        print(f'  Ratio of non-mutual to mutual followers: {ratio:.2f}')
        if ratio > NONMUTUAL_SPAMMER_RATIO_THRESHOLD:
            print(f'  {self.username} might be a spammer based on non-mutual followers ratio.\n')
        else:
            print(f'  {self.username} probably is not a spammer based on non-mutual followers ratio.\n')

    def try_to_check_spammer_slow(self):
        if (self.followers_count < MAX_FOLLOWERS_TO_GET_THEM
                and self.following_count < MAX_FOLLOWING_TO_GET_THEM):
            self.get_followers_following()
            self.check_nonmutual_followers()
            self.print_follows()
            self.check_spammer_slow()

    @staticmethod
    def check_is_the_user_is_spammer(username: str):
        user = GitHubUser(username)
        user.get_followers_following()
        user.check_spammer_fast()
        user.try_to_check_spammer_slow()

    def check_spammer_fast(self) -> None:
        if self.following_count == 0:
            print(f'  {self.username} might be a spammer: zero following')
            return

        ratio = self.followers_count / self.following_count
        print(f'  Follower to following ratio: {ratio:.2f}')
        if ratio > FOLLOWER_FOLLOWING_RATIO_THRESHOLD:
            print(f'  {self.username} might be a spammer based on the ratio.\n')
        else:
            print(f'  {self.username} probably is not a spammer based on the ratio\n')

    def check_followers_spammers(self):
        print('Checking for spammers among users who have followed you but you have not followed back:')
        for follower in self.non_mutual_followers:
            GitHubUser.check_is_the_user_is_spammer(follower)

        print('Checking for spammers among users you are following but who haven\'t followed you back:')
        for following in self.non_followers:
            GitHubUser.check_is_the_user_is_spammer(following)


def main() -> None:
    me = GitHubUser(USERNAME)
    me.get_followers_following()
    me.check_nonmutual_followers()
    me.print_follows()
    me.print_non_mutual_count()
    me.print_non_mutual_users()
    me.check_followers_spammers()


if __name__ == '__main__':
    main()
