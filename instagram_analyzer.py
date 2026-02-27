#!/usr/bin/env python3
"""
Instagram Follower Analyzer
Analyzes a public Instagram profile's followers, following, and mutual follows.
"""

import instaloader
import getpass
import sys
from datetime import datetime


def get_profile_data(loader, target_username):
    """Fetch followers and following for the target profile."""
    print(f"\nFetching profile: @{target_username}")
    try:
        profile = instaloader.Profile.from_username(loader.context, target_username)
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Error: Profile @{target_username} does not exist.")
        sys.exit(1)
    except instaloader.exceptions.LoginRequiredException:
        print("Error: This profile is private. Login is required and you must follow this account.")
        sys.exit(1)

    print(f"Profile found: {profile.full_name} | Followers: {profile.followers} | Following: {profile.followees}")
    print("\nNote: Fetching large follower/following lists may take a while due to Instagram rate limits.")

    print("\nFetching following list...")
    following = set()
    try:
        for followee in profile.get_followees():
            following.add(followee.username)
            print(f"  Following: {len(following)}", end="\r")
    except instaloader.exceptions.LoginRequiredException:
        print("\nError: Login required to fetch following list.")
        sys.exit(1)
    print(f"  Following fetched: {len(following)}")

    print("\nFetching followers list...")
    followers = set()
    try:
        for follower in profile.get_followers():
            followers.add(follower.username)
            print(f"  Followers: {len(followers)}", end="\r")
    except instaloader.exceptions.LoginRequiredException:
        print("\nError: Login required to fetch followers list.")
        sys.exit(1)
    print(f"  Followers fetched: {len(followers)}")

    return followers, following


def write_report(target_username, followers, following):
    """Write analysis results to a text file."""
    mutual = followers & following
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{target_username}_analysis_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Instagram Follower Analysis for @{target_username}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

        # Following
        f.write(f"ACCOUNTS @{target_username} FOLLOWS ({len(following)})\n")
        f.write("-" * 40 + "\n")
        for username in sorted(following):
            f.write(f"@{username}\n")

        # Followers
        f.write(f"\nACCOUNTS THAT FOLLOW @{target_username} ({len(followers)})\n")
        f.write("-" * 40 + "\n")
        for username in sorted(followers):
            f.write(f"@{username}\n")

        # Mutual follows
        f.write(f"\nMUTUAL FOLLOWS - Both follow each other ({len(mutual)})\n")
        f.write("-" * 40 + "\n")
        for username in sorted(mutual):
            f.write(f"@{username}\n")

    return filename, len(followers), len(following), len(mutual)


def main():
    print("=" * 60)
    print("       Instagram Follower Analyzer")
    print("=" * 60)

    target_username = input("\nEnter the Instagram username to analyze: ").strip().lstrip("@")
    if not target_username:
        print("Error: Username cannot be empty.")
        sys.exit(1)

    print("\nLogin is required to access follower/following data.")
    print("Your credentials are used only to authenticate with Instagram.")
    session_username = input("Your Instagram username (for login): ").strip()
    session_password = getpass.getpass("Your Instagram password: ")

    loader = instaloader.Instaloader(
        quiet=True,
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
    )

    print("\nLogging in...")
    try:
        loader.login(session_username, session_password)
        print("Login successful.")
    except instaloader.exceptions.BadCredentialsException:
        print("Error: Invalid username or password.")
        sys.exit(1)
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        code = input("Two-factor authentication required. Enter the code: ").strip()
        loader.two_factor_login(code)
        print("Login successful.")
    except Exception as e:
        print(f"Login error: {e}")
        sys.exit(1)

    followers, following = get_profile_data(loader, target_username)

    print("\nWriting report...")
    filename, n_followers, n_following, n_mutual = write_report(target_username, followers, following)

    print(f"\nAnalysis complete!")
    print(f"  Following:      {n_following}")
    print(f"  Followers:      {n_followers}")
    print(f"  Mutual follows: {n_mutual}")
    print(f"\nReport saved to: {filename}")


if __name__ == "__main__":
    main()
