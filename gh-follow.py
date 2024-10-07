import requests
from config import GITHUB_TOKEN, USERNAME

# Thresholds for determining potential spam behavior
FOLLOWER_FOLLOWING_RATIO_THRESHOLD = 10
NONMUTUAL_SPAMMER_RATIO_THRESHOLD = 0.5
MAX_FOLLOWERS_TO_GET_THEM = 1400  # Adjust this lower for faster results
MAX_FOLLOWING_TO_GET_THEM = 1800  # Adjust this lower for faster results


class GitHubUser:
    """Class representing a GitHub user and their follower/following stats."""

    username: str
    followers_count: int
    following_count: int
    followers: set
    following: set
    non_mutual_followers: set
    non_mutual_followers_count: int
    mutual_followers: set
    mutual_followers_count: int
    non_followers: set
    non_followers_count: int

    def __init__(self, username: str):
        """Initializes the GitHubUser with the given username and fetches basic info.

        Args:
            username (str): The GitHub username.
        """
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

        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
        }
        url = f'https://api.github.com/users/{username}'
        try:
            # Fetching dara from github
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            # Parse user info from API response
            user_info = response.json()
            self.followers_count = user_info['followers']
            self.following_count = user_info['following']

        except requests.HTTPError as e:
            print(f"Failed to get info for {username}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while fetching user info: {e}")

    @staticmethod
    def get_github_users(url: str) -> set:
        """Fetches GitHub users from the given URL.

        Args:
            url (str): The API URL to fetch users from.

        Returns:
            set: A set of GitHub usernames.
        """
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
        }
        users = []
        try:
            # Support pagination to iterate through all available pages
            while url:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                users.extend(response.json())
                url = response.links.get('next', {}).get('url')
            return set([user['login'] for user in users])

        except requests.HTTPError as e:
            print(f"Failed to get users from {url}: {e}")
            return set()
        except Exception as e:
            print(f"An unexpected error occurred while fetching users: {e}")
            return set()

    def get_followers_following(self) -> None:
        """Retrieves the user's followers and followings."""
        followers_url = f'https://api.github.com/users/{self.username}/followers'
        following_url = f'https://api.github.com/users/{self.username}/following'
        self.followers = set(GitHubUser.get_github_users(followers_url))
        self.following = set(GitHubUser.get_github_users(following_url))

    def check_nonmutual_followers(self) -> None:
        """Identifies non-mutual followers and followings."""
        # Determine non-mutual followers and followings
        self.non_mutual_followers = self.followers - self.following
        self.non_mutual_followers_count = len(self.non_mutual_followers)

        # Determine mutual followers
        self.mutual_followers = self.followers & self.following
        self.mutual_followers_count = len(self.mutual_followers)

        # Determine non-followers
        self.non_followers = self.following - self.followers
        self.non_followers_count = len(self.non_followers)

    def print_non_mutual_count(self) -> None:
        """Prints counts of mutual and non-mutual followers."""
        print(f'  {self.username} non mutual followers count: {self.non_mutual_followers_count}')
        print(f'  {self.username} mutual followers count: {self.mutual_followers_count}')

    def print_follows(self) -> None:
        """Prints the numbers of followers and following for the user."""
        print(f'  {self.username} number of followers: {self.followers_count}')
        print(f'  {self.username} number of following: {self.following_count}')

    def print_non_mutual_users(self) -> None:
        """Prints users who are non-mutual followers and non-followers."""
        if self.non_mutual_followers:
            print(f'Users who have followed {self.username} but haven\'t followed back:')
            for user in self.non_mutual_followers:
                print(user)
        if self.non_followers:
            print(f'Users {self.username} is following but who haven\'t followed back:')
            for user in self.non_followers:
                print(user)

    def check_spammer_slow(self) -> None:
        """Evaluates if user is a potential spammer based on non-mutual followers ratio."""
        if self.mutual_followers_count == 0:
            print(f'  {self.username} might be a spammer: no mutual followers.\n')
            return
        ratio = self.non_mutual_followers_count / self.mutual_followers_count
        print(f'  {self.username} ratio of non-mutual to mutual followers: {ratio:.2f}')
        if ratio > NONMUTUAL_SPAMMER_RATIO_THRESHOLD:
            print(f'  {self.username} might be a spammer based on non-mutual followers ratio.\n')
        else:
            print(f'  {self.username} probably is not a spammer based on non-mutual followers ratio.\n')

    def try_to_check_spammer_slow(self) -> None:
        """Runs a deeper spam check if counts are below thresholds."""
        if (self.followers_count < MAX_FOLLOWERS_TO_GET_THEM
                and self.following_count < MAX_FOLLOWING_TO_GET_THEM):
            self.get_followers_following()
            self.check_nonmutual_followers()
            self.print_non_mutual_count()
            self.check_spammer_slow()

    @staticmethod
    def check_is_the_user_is_spammer(username: str) -> None:
        """Checks if the specified user might be a spammer.

        Args:
            username (str): The GitHub username to check.
        """
        user = GitHubUser(username)
        user.check_spammer_fast()
        user.try_to_check_spammer_slow()

    def check_spammer_fast(self) -> None:
        """Quickly checks if user might be a spammer based on follower/following ratio."""
        self.print_follows()
        if self.following_count == 0:
            print(f'  {self.username} might be a spammer: zero following')
            return

        ratio = self.followers_count / self.following_count
        print(f'  {self.username} follower to following ratio: {ratio:.2f}')
        if ratio > FOLLOWER_FOLLOWING_RATIO_THRESHOLD:
            print(f'  {self.username} might be a spammer based on the ratio.\n')
        else:
            print(f'  {self.username} probably is not a spammer based on the ratio\n')

    def check_followers_spammers(self) -> None:
        """Checks if non-mutual followers and non-followers might be spammers."""
        print('Checking for spammers among users who have followed you but you have not followed back:')
        for follower in self.non_mutual_followers:
            GitHubUser.check_is_the_user_is_spammer(follower)

        print('Checking for spammers among users you are following but who haven\'t followed you back:')
        for following in self.non_followers:
            GitHubUser.check_is_the_user_is_spammer(following)


def main() -> None:
    """Main function to execute the check followers and followings on GitHub."""
    me = GitHubUser(USERNAME)
    me.get_followers_following()
    me.check_nonmutual_followers()
    me.print_follows()
    me.print_non_mutual_count()
    me.print_non_mutual_users()
    me.check_followers_spammers()


if __name__ == '__main__':
    main()