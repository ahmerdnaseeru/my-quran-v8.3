import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import random
import os
import time

TOKEN = "8961687067:AAGfqmVYHxdMrwPjPOXytbpUk1qErA90Bbc"

LANGUAGES = {"en": "en.sahih","ha": "en.sahih","ar": "ar.uthmani"}
user_lang = {}

SAHIH_BUKHARI = {
"1": {"arabic": "إِنَّمَا الْأَعْمَالُ بِالنِّيَّاتِ", "english": "Actions are but by intentions", "meaning": "Every deed is judged by intention."},
"2": {"arabic": "اتَّقِ اللَّهَ حَيْثُمَا كُنْتَ", "english": "Fear Allah wherever you are", "meaning": "Allah is always watching."},
"3": {"arabic": "تَبَسُّمُكَ فِي وَجْهِ أَخِيكَ صَدَقَةٌ", "english": "Your smile to your brother is charity", "meaning": "Small deeds, big reward."},
"4": {"arabic": "لَا تَغْضَبْ", "english": "Do not get angry", "meaning": "Control your anger."},
"5": {"arabic": "الدُّنْيَا سِجْنُ الْمُؤْمِنِ", "english": "The world is a prison for the believer", "meaning": "This dunya is temporary."},
"6": {"arabic": "خَيْرُكُمْ مَنْ تَعَلَّمَ الْقُرْآنَ وَعَلَّمَهُ", "english": "The best of you are those who learn Quran and teach it", "meaning": "Spread knowledge."},
"7": {"arabic": "الْمُسْلِمُ مَنْ سَلِمَ الْمُسْلِمُونَ مِنْ لِسَانِهِ وَيَدِهِ", "english": "A Muslim is one from whose tongue and hand other Muslims are safe", "meaning": "Guard your words."},
"8": {"arabic": "مَنْ كَانَ يُؤْمِنُ بِاللَّهِ وَالْيَوْمِ الْآخِرِ فَلْيَقُلْ خَيْرًا", "english": "Whoever believes in Allah and the Last Day, let him speak good", "meaning": "Speak good or stay silent."},
"9": {"arabic": "ارْحَمُوا مَنْ فِي الْأَرْضِ يَرْحَمْكُمْ مَنْ فِي السَّمَاءِ", "english": "Be merciful to those on earth, and the One in heaven will have mercy on you", "meaning": "Show mercy."},
"10": {"arabic": "لَا يُؤْمِنُ أَحَدُكُمْ حَتَّى يُحِبَّ لِأَخِيهِ مَا يُحِبُّ لِنَفْسِهِ", "english": "None of you believes until he loves for his brother what he loves for himself", "meaning": "Genuine brotherhood."},
"11": {"arabic": "الصَّبْرُ ضِيَاءٌ", "english": "Patience is illumination", "meaning": "Sabr brings light."},
"12": {"arabic": "إِنَّ اللَّهَ رَفِيقٌ يُحِبُّ الرِّفْقَ", "english": "Allah is Gentle and loves gentleness", "meaning": "Be gentle."},
"13": {"arabic": "الدَّالُّ عَلَى الْخَيْرِ كَفَاعِلِهِ", "english": "The one who guides to good is like the one who does it", "meaning": "Share this bot."},
"14": {"arabic": "نِعْمَتَانِ مَغْبُونٌ فِيهِمَا كَثِيرٌ مِنَ النَّاسِ: الصِّحَّةُ وَالْفَرَاغُ", "english": "Two blessings people are heedless of: health and free time", "meaning": "Use your time."},
"15": {"arabic": "مَنْ سَتَرَ مُسْلِمًا سَتَرَهُ اللَّهُ", "english": "Whoever covers a Muslim, Allah will cover him", "meaning": "Don't expose others."}
}

SURAH_LIST = [
"A1.Fatiha","2.Al-Baqarah","3.Ali Imran","4.An-Nisa","5.Al-Maidah","6.Al-Anam","7.Al-Araf","8.Al-Anfal","9.At-Tawbah","10.Yunus",
"11.Hud","12.Yusuf","13.Ar-Rad","14.Ibrahim","15.Al-Hijr","16.An-Nahl","17.Al-Isra","18.Al-Kahf","19.Maryam","20.Taha",
"21.Al-Anbiya","22.Al-Hajj","23.Al-Muminun","24.An-Nur","25.Al-Furqan","26.Ash-Shuara","27.An-Naml","28.Al-Qasas","29.Al-Ankabut","30.Ar-Rum",
"31.Luqman","32.As-Sajdah","33.Al-Ahzab","34.Saba","35.Fatir","36.Yasin","37.As-Saffat","38.Sad","39.Az-Zumar","40.Ghafir",
"41.Fussilat","42.Ash-Shura","43.Az-Zukhruf","44.Ad-Dukhan","45.Al-Jathiyah","46.Al-Ahqaf","47.Muhammad","48.Al-Fath","49.Al-Hujurat","50.Qaf",
"51.Adh-Dhariyat","52.At-Tur","53.An-Najm","54.Al-Qamar","55.Ar-Rahman","56.Al-Waqiah","57.Al-Hadid","58.Al-Mujadilah","59.Al-Hashr","60.Al-Mumtahanah",
"61.As-Saff","62.Al-Jumuah","63.Al-Munafiqun","64.At-Taghabun","65.At-Talaq","66.At-Tahrim","67.Al-Mulk","68.Al-Qalam","69.Al-Haqqah","70.Al-Maarij",
"71.Nuh","72.Al-Jinn","73.Al-Muzzammil","74.Al-Muddathir","75.Al-Qiyamah","76.Al-Insan","77.Al-Mursalat","78.An-Naba","79.An-Naziat","80.Abasa",
"81.At-Takwir","82.Al-Infitar","83.Al-Mutaffifin","84.Al-Inshiqaq","85.Al-Buruj","86.At-Tariq","87.Al-Ala","88.Al-Ghashiyah","89.Al-Fajr","90.Al-Balad",
"91.Ash-Shams","92.Al-Lail","93.Ad-Duhaa","94.Ash-Sharh","95.At-Tin","96.Al-Alaq","97.Al-Qadr","98.Al-Bayyinah","99.Az-Zalzalah","100.Al-Adiyat",
"101.Al-Qariah","102.At-Takathur","103.Al-Asr","104.Al-Humazah","105.Al-Fil","106.Quraish","107.Al-Maun","108.Al-Kawthar","109.Al-Kafirun","110.An-Nasr",
"111.Al-Masad","112.Al-Ikhlas","113.Al-Falaq","114.An-Nas"
]

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

def get_back_keyboard(back_to):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back", callback_data=back_to), InlineKeyboardButton("🏠 Menu", callback_data="back_to_menu")]
    ])

async def set_bot_commands(app):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("menu", "Show main menu"),
        BotCommand("help", "How to use the bot"),
        BotCommand("quranlist", "Read full surah"),
        BotCommand("play", "Play Quran audio"),
        BotCommand("search", "Search in Quran"),
        BotCommand("hadith", "Read Hadith")
    ]
    await app.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("English 🇺🇸", callback_data="lang_en")],[InlineKeyboardButton("Hausa 🇳🇬", callback_data="lang_ha")],[InlineKeyboardButton("Arabic 🇸🇦", callback_data="lang_ar")]]
    await update.message.reply_text(f"{BOT_DESCRIPTION}\n\n{get_random_hadith()}\n\n**Choose language:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """**📖 HOW TO USE THE BOT**

**Quran Commands:**
`/quran 2:255` - Get any ayah with translation
`/quranlist` - Select and read full surah
`/play 36` - Play audio of any surah
`/ayah` - Get random ayah

**Knowledge Commands:**
`/hadith` - Browse 15 Sahih Bukhari hadith
`/search sabr` - Search keyword in Quran

**Utility:**
`/menu` - Show all buttons
`/help` - Show this message

Share this bot. It is Sadaqah Jariyah 🤍"""
    await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=get_menu_keyboard())

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("**📋 Main Menu**\nChoose what you want:", reply_markup=get_menu_keyboard(), parse_mode='Markdown')

async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "salam" in text or "salaam" in text or "assalam" in text:
        await update.message.reply_text("Wa Alaikumussalam Warahmatullahi Wabarakatuh 🤍\nType /menu to start")
    elif "jzk" in text or "jazak" in text:
        await update.message.reply_text("Wa Iyyaka 🤍")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
