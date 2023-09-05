import praw
import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger
from datetime import datetime
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
# Initialize the PRAW Reddit instance
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent,
    username=username,
    password=password)




def get_top_5_subreddits(user):
    subreddit_activity = {}
    user = reddit.redditor(user)
    try:
        for comment in user.comments.new(limit=200):
            try:
                subreddit_name = comment.subreddit.display_name
                subreddit_activity[subreddit_name] = subreddit_activity.get(subreddit_name, 0) + 1
            except:
                pass
        for submission in user.submissions.new(limit=200):
            try:
                subreddit_name = submission.subreddit.display_name
                subreddit_activity[subreddit_name] = subreddit_activity.get(subreddit_name, 0) + 1
            except:
                pass
        sorted_subreddits = sorted(subreddit_activity.items(), key=lambda x: x[1], reverse=True)
        top_10 = sorted_subreddits[:10]

        return ', '.join([f'{subreddit} ({activity})' for subreddit, activity in top_10])
    except Exception as e:
        print(f"Error getting top subreddits for user {user}: {str(e)}")
        return str(e)


# Open a session to interact with the database


@bot.event
async def on_ready():
    print("Bot is up and ready!")
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command[s]")
    except Exception as e:
        logger.error(str(e))


@bot.tree.command(name="lookup_reddit")
@app_commands.describe(reddit_user="the reddit username of the user you want to look up",)
@commands.has_permissions(administrator = True)
async def decrement_votes(interaction: discord.Interaction,reddit_user:str):
    try:
        user = reddit.redditor(reddit_user)
    except Exception as e:
        interaction.response.send_message(f"Couldn't find username,{str(e)}")
    await interaction.response.defer()
    try:
        creation_time = datetime.utcfromtimestamp(user.created_utc)
    except:
        creation_time = "UnKnown"

    try:
        is_gold = user.is_gold
    except:
        is_gold = "UnKnown"

    try:
        top_5_comments = [comment.permalink for comment in user.comments.top(limit=5)]
    except:
        top_5_comments = "UnKnown"

    try:
        top_5_submissions = [(submission.title,submission.permalink) for submission in user.submissions.top(limit=5)]

    except:
        top_5_submissions = "UnKnown"
    try:
        top_5_subreddits = get_top_5_subreddits(reddit_user)
    except:
        pass

    # Create a Discord embed
    embed = discord.Embed(title=f"User Info for {reddit_user}", color=0x7289da)
    embed.add_field(name="Creation Time", value=creation_time, inline=False)
    embed.add_field(name="Is Gold", value=is_gold, inline=False)
    embed.add_field(name="Top 10 Subreddits",value=top_5_subreddits)

    # Add top 5 comments
    if top_5_comments != "Unknown":
        for i,comment_permalink in enumerate(top_5_comments, start=1):
            embed.add_field(
                name=f"Top Comment {i}",
                value=f"**Permalink:** https://www.reddit.com/{comment_permalink}",
                inline=False
            )

    # Add top 5 submissions
    if top_5_submissions != "Unknown":
        for i, (submission_title, submission_permalink) in enumerate(top_5_submissions, start=1):
            embed.add_field(
                name=f"Top Submission {i}",
                value=f"**Title:** {submission_title}\n**Permalink:** https://www.reddit.com/{submission_permalink}",
                inline=False)

    await interaction.followup.send(embed=embed)


bot.run(TOKEN)

session.close()
