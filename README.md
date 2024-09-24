# Stop GH Spammers

Stop GH Spammers is a tool for detecting and dealing with dishonest followers on GitHub.

## Description

On GitHub, there is an issue where users follow you, you reciprocate, and then they unfollow you to increase their follower count. Cleaning up these dishonest followers can be a challenging task, so we created a small program to help with this.

## Installation

1. Obtain a GitHub Token:
    - Go to your GitHub account settings.
    - Create a new Personal Access Token with profile read and write permissions.
    - Copy the created token.

2. Clone the repository:
    ```sh
    git clone https://github.com/sergei-kruchinin/stop-gh-spamers
    ```

3. Navigate to the project directory:
    ```sh
    cd stop-gh-spamers
    ```

4. Create a `.env` file and add your GitHub token to it:
    ```env
    GH_API_KEY=your_github_api_key
    ```

## Usage

1. Run the `gh-follow.py` script:
    ```sh
    python gh-follow.py
    ```

2. The program will display:
    - Those who have followed you but you have not followed back.
    - Those you are following but who have not followed you back.
   
3. The program will also make predictions on whether a user is a spammer based on their followers-to-following ratio.

4. Evaluate for yourself if a user is a spammer. If it is obvious:
   - Unfollow the user.
   - File a report:
     1. Go to the user's profile and select "Block or report user".
     2. Choose "Report".
     3. Select the reason "Spam or inauthentic Activity".

## Report Text

```plaintext
Inauthentic use of the service such as rank abuse, star abuse, the use of bots, fake accounts or other deceptive uses of the service.
