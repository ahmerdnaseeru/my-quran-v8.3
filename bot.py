import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import random
import os
import time

TOKEN = os.getenv("TOKEN")

LANGUAGES = {"en": "en.sahih","ha": "en.sahih","ar": "ar.uthmani"}
user_lang = {}

SAHIH_BUKHARI = {
"1": {"arabic": "إِنَّمَا الْأَعْمَالُ بِالنِّيَّاتِ", "english": "Actions are but by intentions", "meaning": "Every deed is judged by intention."},
"2": {"arabic": "اتَّقِ اللَّهَ حَيْثُمَا كُنْتَ", "english": "Fear Allah wherever you are", "meaning": "Allah is always watching."},
"3": {"arabic": "تَبَسُّمُكَ فِي وَجْهِ أَخِيكَ صَدَقَةٌ", "english": "Your smile to your brother is charity", "meaning": "Small deeds, big reward."},
"4": {"arabic": "لَا تَغْضَبْ", "english": "Do not get angry", "meaning": "Control your anger."},
"5": {"arabic": "الدُّنْيَا سِجْنُ الْمُؤْمِنِ", "english": "The world is a prison for the believer", "meaning": "This dunya is temporary."}
}

SURAH_LIST = ["1.Al-Fatiha","2.Al-Baqarah","3.Ali Imran","114.An-Nas"]

BOT_DESCRIPTION = "🤍 **Sincerely Islamic Bot v8.4** 🤍\nFull 114 Surahs, Audio, Hadith & Search."

def get_random_hadith():
    key = random.choice(list(SAHIH_BUKHARI.keys()))
    h = SAHIH_BUKHARI[key]
    return f"📜 **Sahih Bukhari #{key}**\n\n`{h['arabic']}`\n\n**English:** {h['english']}\n\n**Meaning:** {h['meaning']}"

def get_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Read Full Quran", callback_data="menu_quranlist")],
        [InlineKeyboardButton("🎧 Play Quran Audio", callback_data="menu_play_help"), InlineKeyboardButton("🔍 Search Quran", callback_data="menu_search_help")],
        [InlineKeyboardButton("📚 Hadith Library", callback_data="menu_hadith"), InlineKeyboardButton("🎲 Random Ayah", callback_data="menu_ayah")],
        [InlineKeyboardButton("🌍 Change Language", callback_data="menu_lang")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("English 🇺🇸", callback_data="lang_en")],[InlineKeyboardButton("Hausa 🇳🇬", callback_data="lang_ha")],[InlineKeyboardButton("Arabic 🇸🇦", callback_data="lang_ar")]]
    await update.message.reply_text(f"{BOT_DESCRIPTION}\n\n{get_random_hadith()}\n\n**Choose language:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Sincerely Islamic Bot v8.4 Running...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        user_lang[query.from_user.id] = lang
        await query.edit_message_text(f"**Language: {lang.upper()}** ✅\n\n", parse_mode='Markdown')
        time.sleep(0.5)
        await query.message.reply_text("**What would you like to do?**", reply_markup=get_menu_keyboard(), parse_mode='Markdown')
    
    elif data == "menu_quranlist": await quranlist(update, context)
    elif data == "menu_hadith": await hadith(update, context)
    elif data == "menu_ayah": await ayah(update, context)
    elif data == "menu_lang": await start(update, context)
    elif data == "menu_play_help": await query.edit_message_text("**To play audio:**\nUse `/play 1` for Surah 1\nExample: `/play 112`", parse_mode='Markdown', reply_markup=get_back_keyboard("back_to_menu"))
    elif data == "menu_search_help": await query.edit_message_text("**To search:**\nUse `/search jannah`\nExample: `/search tawakkul`", parse_mode='Markdown', reply_markup=get_back_keyboard("back_to_menu"))
    elif data == "back_to_menu": await menu(update, context)
    elif data.startswith("surah_"): await surah_callback(update, context)
    elif data.startswith("hadith_"): await hadith_callback(update, context)
    elif data == "back_to_list": await quranlist(update, context)
    elif data == "back_to_hadith": await hadith(update, context)

async def quranlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    row = []
    for i, surah in enumerate(SURAH_LIST):
        num = surah.split(".")[0]
        name = surah.split(".")[1]
        row.append(InlineKeyboardButton(f"{num}. {name}", callback_data=f"surah_{num}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)
    keyboard.append([InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")])
    target = update.callback_query if update.callback_query else update
    await target.message.reply_text("📖 **Select a Surah to Read - All 114**", reply_markup=InlineKeyboardMarkup(keyboard))

async def surah_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    surah_num = query.data.split("_")[1]
    lang_code = user_lang.get(query.from_user.id, "en")
    trans_api = LANGUAGES.get(lang_code, "en.sahih")
    await query.edit_message_text(f"⏳ Fetching Surah {surah_num}...")
    try:
        ar = requests.get(f"https://api.alquran.cloud/v1/surah/{surah_num}/ar.uthmani", timeout=30).json()['data']['ayahs']
        en = requests.get(f"https://api.alquran.cloud/v1/surah/{surah_num}/{trans_api}", timeout=30).json()['data']['ayahs']
        surah_name = SURAH_LIST[int(surah_num)-1].split(".")[1]
        await query.message.reply_text(f"**📖 Surah {surah_name} - {len(ar)} Ayahs**\n\n", parse_mode='Markdown')
        msg = ""
        for i in range(len(ar)):
            chunk = f"`{ar[i]['text']}`\n**{i+1}.** {en[i]['text']}\n\n"
            if len(msg) + len(chunk) > 3500:
                await query.message.reply_text(msg, parse_mode='Markdown')
                msg = chunk
                time.sleep(1)
            else: msg += chunk
        if msg: await query.message.reply_text(msg, parse_mode='Markdown')
        await query.message.reply_text("**Finished**", reply_markup=get_back_keyboard("back_to_list"))
    except: await query.message.reply_text("❌ Error fetching surah.")

async def hadith(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(f"Sahih Bukhari #{num}", callback_data=f"hadith_{num}")] for num in SAHIH_BUKHARI.keys()]
    keyboard.append([InlineKeyboardButton("🎲 Random Hadith", callback_data="hadith_random")])
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")])
    target = update.callback_query if update.callback_query else update
    await target.message.reply_text("📚 **Sahih Bukhari Library - 15 Hadith**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def hadith_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "hadith_random": text = get_random_hadith()
    else:
        num = query.data.split("_")[1]
        h = SAHIH_BUKHARI[num]
        text = f"📜 **Sahih Bukhari #{num}**\n`{h['arabic']}`\n\n**English:** {h['english']}\n\n**Meaning:** {h['meaning']}"
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=get_back_keyboard("back_to_hadith"))

async def quran(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args: return await update.message.reply_text("❌ Use: `/quran 2:255`", parse_mode='Markdown')
        ref = context.args[0]
        lang_code = user_lang.get(update.effective_user.id, "en")
        trans_api = LANGUAGES.get(lang_code, "en.sahih")
        arabic = requests.get(f"https://api.alquran.cloud/v1/ayah/{ref}/ar.uthmani", timeout=10).json()['data']['text']
        trans = requests.get(f"https://api.alquran.cloud/v1/ayah/{ref}/{trans_api}", timeout=10).json()['data']['text']
        await update.message.reply_text(f"**{ref}**\n\n`{arabic}`\n\n**Translation**: {trans}", parse_mode='Markdown', reply_markup=get_back_keyboard("back_to_menu"))
    except: await update.message.reply_text("❌ Use: /quran 2:255")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args: return await update.message.reply_text("❌ Use: `/play 1`", parse_mode='Markdown')
        surah = int(context.args[0])
        await update.message.reply_text(f"⏳ Downloading Surah {surah}...")
        filename = f"Surah_{surah}.mp3"
        audio_url = f"https://download.quranicaudio.com/quran/mishari_rashid_alafasy/{surah:03}.mp3"
        r = requests.get(audio_url, timeout=90)
        with open(filename, 'wb') as f: f.write(r.content)
        with open(filename, 'rb') as audio: await update.message.reply_audio(audio=audio, title=f"Surah {surah}", performer="Mishari Alafasy")
        os.remove(filename)
        await update.message.reply_text("**Done**", reply_markup=get_back_keyboard("back_to_menu"))
    except: await update.message.reply_text("❌ Download failed.")

async def ayah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.args = [f"{random.randint(1,114)}:{random.randint(1,10)}"]
    await quran(update, context)

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args: return await update.message.reply_text("❌ Use: `/search sabr`", parse_mode='Markdown')
        keyword = " ".join(context.args)
        await update.message.reply_text(f"⏳ Searching Quran for '{keyword}'...")
        res = requests.get(f"https://api.alquran.cloud/v1/search/{keyword}/all/en", timeout=15)
        data = res.json()
        if data['data']['count'] > 0:
            matches = data['data']['matches'][:5]
            msg = f"**🔍 Found {data['data']['count']} results for '{keyword}':**\n\n"
            for m in matches: msg += f"**{m['surah']['name']} {m['surah']['number']}:{m['numberInSurah']}**\n`{m['text']}`\n\n"
            await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=get_back_keyboard("back_to_menu"))
        else: await update.message.reply_text(f"❌ No results for '{keyword}'", reply_markup=get_back_keyboard("back_to_menu"))
    except: await update.message.reply_text("❌ Search error.", reply_markup=get_back_keyboard("back_to_menu"))

def main():
    app = ApplicationBuilder().token(TOKEN).job_queue(None).build()
    app.post_init = set_bot_commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("quran", quran))
    app.add_handler(CommandHandler("quranlist", quranlist))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("ayah", ayah))
    app.add_handler(CommandHandler("hadith", hadith))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))
    print("Sincerely Islamic Bot v8.4 Running... Alhamdulillah")
    app.run_polling()

if __name__ == "__main__":
    main()
