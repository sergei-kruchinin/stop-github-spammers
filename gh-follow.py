import asyncio
import httpx

from config import GITHUB_TOKEN, USERNAME

FOLLOWER_FOLLOWING_RATIO_THRESHOLD = 10
NONMUTUAL_SPAMMER_RATIO_THRESHOLD = 0.5
MAX_FOLLOWERS_TO_GET_THEM = 2400
MAX_FOLLOWING_TO_GET_THEM = 2800


class GitHubUser:
    def __init__(self, username: str):
        self.username = username
        self.followers_count = 0
        self.following_count = 0
        self.followers = set()
        self.following = set()
        self.non_mutual_followers = set()
        self.non_mutual_followers_count = 0
        self.mutual_followers = set()
        self.mutual_followers_count = 0
        self.non_followers = set()
        self.non_followers_count = 0

    async def fetch_user_info(self):
        url = f'https://api.github.com/users/{self.username}'
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                user_info = response.json()
                self.followers_count = user_info['followers']
                self.following_count = user_info['following']
            except httpx.HTTPError as e:
                print(f"Failed to get info for {self.username}: {e}")

    @staticmethod
    async def get_github_users(url: str) -> set:
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
        }
        users = set()
        async with httpx.AsyncClient() as client:
            try:
                while url:
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()
                    page_users = {user['login'] for user in response.json()}
                    users.update(page_users)
                    url = response.links.get('next', {}).get('url', None)
            except httpx.HTTPError as e:
                print(f"Failed to get users from {url}: {e}")
        return users

    async def get_followers_following(self):
        followers_url = f'https://api.github.com/users/{self.username}/followers?per_page=100'
        following_url = f'https://api.github.com/users/{self.username}/following?per_page=100'
        self.followers = await self.get_github_users(followers_url)
        self.following = await self.get_github_users(following_url)

    def check_nonmutual_followers(self):
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

    def is_spammer_fast(self):
        self.print_follows()
        ratio = self.followers_count / self.following_count if self.following_count else float('inf')
        if ratio > FOLLOWER_FOLLOWING_RATIO_THRESHOLD:
            print(f'  {self.username} might be a spammer (fast check).')
        else:
            print(f'  {self.username} probably is not a spammer (fast check).')

    async def try_to_check_spammer_slow(self):
        if (self.followers_count < MAX_FOLLOWERS_TO_GET_THEM
                and self.following_count < MAX_FOLLOWING_TO_GET_THEM):
            await self.get_followers_following()
            self.check_nonmutual_followers()
            self.print_non_mutual_count()
            self.is_spammer_slow()

    def is_spammer_slow(self):
        if not self.mutual_followers_count:
            print(f'  {self.username} might be a spammer: no mutual followers.')
        else:
            ratio = self.non_mutual_followers_count / self.mutual_followers_count
            if ratio > NONMUTUAL_SPAMMER_RATIO_THRESHOLD:
                print(f'  {self.username} might be a spammer (slow check).')
            else:
                print(f'  {self.username} probably is not a spammer (slow check).')


async def check_user(username: str):
    user = GitHubUser(username)
    await user.fetch_user_info()
    user.is_spammer_fast()
    await user.try_to_check_spammer_slow()


async def main():
    me = GitHubUser(USERNAME)
    await me.fetch_user_info()
    await me.get_followers_following()
    me.check_nonmutual_followers()
    me.print_follows()
    me.print_non_mutual_count()

    tasks = [check_user(follower) for follower in me.non_mutual_followers]
    tasks += [check_user(following) for following in me.non_followers]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
