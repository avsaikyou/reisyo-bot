import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime
import os
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"counts": {}, "month": datetime.now().month}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# -----------------------
# ロール更新
# -----------------------
async def update_level_roles(member, count):
    beginner = discord.utils.get(member.guild.roles, name="冷笑初級😅")
    intermediate = discord.utils.get(member.guild.roles, name="冷笑中級😅")
    advanced = discord.utils.get(member.guild.roles, name="冷笑上級😅")

    for role in [beginner, intermediate, advanced]:
        if role and role in member.roles:
            await member.remove_roles(role)

    if count >= 50 and advanced:
        await member.add_roles(advanced)
    elif count >= 30 and intermediate:
        await member.add_roles(intermediate)
    elif count >= 10 and beginner:
        await member.add_roles(beginner)

async def update_king_role(guild):
    if not data["counts"]:
        return

    sorted_users = sorted(data["counts"].items(), key=lambda x: x[1], reverse=True)
    top_user_id = int(sorted_users[0][0])
    king_role = discord.utils.get(guild.roles, name="冷笑王😅")

    if not king_role:
        return

    for member in guild.members:
        if king_role in member.roles and member.id != top_user_id:
            await member.remove_roles(king_role)

    member = guild.get_member(top_user_id)
    if member and king_role not in member.roles:
        await member.add_roles(king_role)

# -----------------------
# 月リセット
# -----------------------
@tasks.loop(minutes=60)
async def monthly_reset():
    current_month = datetime.now().month
    if data["month"] != current_month:
        data["counts"] = {}
        data["month"] = current_month
        save_data(data)

        for guild in bot.guilds:
            for member in guild.members:
                for role_name in ["冷笑初級😅", "冷笑中級😅", "冷笑上級😅", "冷笑王😅"]:
                    role = discord.utils.get(guild.roles, name=role_name)
                    if role and role in member.roles:
                        await member.remove_roles(role)

@bot.event
async def on_ready():
    print("冷笑Bot起動完了...出る！😅")
    monthly_reset.start()

# -----------------------
# メッセージ検知
# -----------------------
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content
    normalized = content.lower().replace("ｗ", "w")

    detected = False

    if "😅" in normalized:
        detected = True
    elif "うおw" in normalized:
        detected = True
    elif "クカ" in normalized:
        detected = True
    elif normalized.strip() == "w":
        detected = True

    if detected:
        await message.channel.send(
            "冷笑を検知😅"
        )

    await bot.process_commands(message)


# -----------------------
# コマンド
# -----------------------
@bot.command()
async def ranking(ctx):
    if not data["counts"]:
        await ctx.send("まだ誰も冷笑してないけど...😅")
        return

    sorted_users = sorted(data["counts"].items(), key=lambda x: x[1], reverse=True)

    msg = "🔥 😅冷笑ランキング😅 🔥\n"
    for i, (user_id, count) in enumerate(sorted_users[:5], start=1):
        user = await bot.fetch_user(int(user_id))
        msg += f"{i}位 {user.name} : {count}回😅\n"

    await ctx.send(msg)

@bot.command()
async def mycount(ctx):
    user_id = str(ctx.author.id)
    count = data["counts"].get(user_id, 0)
    await ctx.send(f"{ctx.author.mention} の冷笑回数は... {count}回😅")

bot.run(TOKEN)
