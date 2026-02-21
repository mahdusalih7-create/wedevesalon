import discord
import subprocess
import requests
import os

# توكن البوت من متغير البيئة (في Railway)
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# ملفات الدمبر
DUMP_SCRIPT = "deobfuscator_console.py"
TEMP_FILE = "input.lua"
OUTPUT_FILE = "output.lua"

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

async def run_dumper(input_path, mode="dump"):
    try:
        result = subprocess.run(
            ["python3", DUMP_SCRIPT, input_path, OUTPUT_FILE, mode],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith(".l"):
        await message.reply("⏳ جاري فك التشفير...")

        parts = message.content.split()
        mode = "dump"  # افتراضي
        url_or_file = None

        # صيغة: .l dump رابط
        if len(parts) > 1:
            if parts[1] in ["dump", "decompile"]:
                mode = parts[1]
            if len(parts) > 2:
                url_or_file = parts[2]

        # لو فيه رابط
        if url_or_file:
            try:
                r = requests.get(url_or_file)
                with open(TEMP_FILE, "wb") as f:
                    f.write(r.content)
            except:
                await message.reply("❌ فشل تحميل الملف من الرابط")
                return
        # لو فيه ملف مرفق
        elif message.attachments:
            file = message.attachments[0]
            await file.save(TEMP_FILE)
        else:
            await message.reply("❌ ارسل رابط أو ارفق ملف")
            return

        # تشغيل الدمبر
        output = await run_dumper(TEMP_FILE, mode)

        # إرسال الناتج
        if os.path.exists(OUTPUT_FILE):
            await message.reply(file=discord.File(OUTPUT_FILE))
        else:
            await message.reply(f"```{output[:1900]}```")

client.run(TOKEN)
