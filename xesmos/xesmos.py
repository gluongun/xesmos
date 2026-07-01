
import discord
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


client = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

SYSTEM_PROMPT = """
You are a helpful, friendly AI assistant named Xesmos.
You help users with coding, problem-solving, and general questions.
You are concise but thorough. You speak in a casual, approachable tone.
"""

@bot.event
async def on_ready():
    print(f' logged in as {bot.user} ₍₍⚞(˶>ᗜ<˶)⚟⁾⁾')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return


    if message.content.startswith('!ask'):
        user_question = message.content[4:].strip()

        if not user_question:
            await message.channel.send("Ask me something after `!ask`")
            return

        async with message.channel.typing():
            try:

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_question}
                    ],
                    max_tokens=500,
                    temperature=0.7,
                )

                reply = response.choices[0].message.content

                if len(reply) > 1900:
                    for chunk in [reply[i:i+1900] for i in range(0, len(reply), 1900)]:
                        await message.channel.send(chunk)
                else:
                    await message.channel.send(reply)

            except Exception as e:
                await message.channel.send(f"something went wrong ( ꩜ ᯅ ꩜;): `{str(e)}`")
                print(f"Error: {e}")


    elif message.content.startswith('!scrape'):
        url = message.content[8:].strip()

        if not url or not url.startswith('http'):
            await message.channel.send("Please provide a valid URL: `!scrape https://example.com`")
            return

        async with message.channel.typing():
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
                title = soup.find("title")
                title_text = title.text.strip() if title else "no title found (๑•́ -•̀)"

                paragraphs = soup.find_all("p")
                text = " ".join([p.text.strip() for p in paragraphs[:3]])
                text = text[:500] + "..." if len(text) > 500 else text

                await message.channel.send(f"**{title_text}**\n\n{text}")
            except Exception as e:
                await message.channel.send(f" failed to scrape: {str(e)}")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)