
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Bot
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler
import database as db
import json
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Translations
TRANSLATIONS = {
    'en': {
        'welcome_msg': "👋 Hello {name}!\nWelcome to the Gmail Selling Bot.\nSelect an option below to get started.",
        'btn_register': "➕ Register a new account",
        'btn_my_accounts': "📋 My accounts",
        'btn_balance': "💰 Balance",
        'btn_referrals': "👥 My referrals",
        'btn_settings': "⚙️ Settings",
        'btn_help': "💬 Help",
        'balance_msg': "💰 *Wallet Balance*\n\n✅ Available: {balance:.2f} BDT\n⏳ Hold: {hold:.2f} BDT\n\nFunds in 'Hold' will be moved to 'Available' after admin approval (approx. 24h).",
        'withdraw_btn': "💸 Withdraw",
        'no_accounts_sold': "You haven't sold any accounts yet.",
        'my_accounts_title': "📋 *My Last 10 Accounts:*\n\n",
        'referrals_msg': "👥 *My Referrals*\n\n💰 *Commission per Sale:* {bonus:.2f} BDT\n👥 Total Referrals: {count}\n\n🔗 *Your Referral Link:*\n`{link}`",
        'help_msg': "Contact [Support](https://t.me/Gmail_Employee_Support) for help.",
        'settings_title': "⚙️ *Settings*",
        'payment_methods_btn': "💳 Payment Methods",
        'language_btn': "🌐 Language",
        'close_btn': "🚫 Close",
        'back_btn': "🔙 Back",
        'payment_methods_msg': "💳 *Payment Methods*\n\nYour saved methods:\n{info_str}\n\nSelect a method to add/edit:",
        'select_language': "🌐 Select Language:",
        'language_set': "✅ Language set to English (Saved).",
        'enter_payment': "Enter your *{method} {label}*:",
        'payment_saved': "✅ Saved {method}: `{value}`",
        'no_accounts_avail': "⚠️ No accounts available. Please try again later.",
        'register_msg': "Register account using the specified data and get {price} BDT\n\nFirst name: `{first}`\nLast name: `{last}`\nEmail: `{email}`\nPassword: `{password}`\n{recovery_section}\n\n🔒 Be sure to use the specified data.",
        'btn_done': "✔️ Done",
        'btn_cancel_reg': "🚫 Cancel registration",
        'btn_how_to': "❓ How to create account",
        'account_submitted': "✅ Account submitted for approval! You earned {price} BDT (Hold).\nAdmin will verify within 24 hours.\nCheck 'My accounts' for status.",
        'reg_cancelled': "🚫 Registration cancelled. Account released.",
        'help_create_msg': "Go to gmail.com, click Create Account, use the provided email and password. Use a clean IP.",
        'withdraw_no_method': "⚠️ You have not set a payment method yet.\nPlease go to ⚙️ Settings > Payment Methods and save one first.",
        'withdraw_min_error': "⚠️ Minimum withdrawal is 0.50 BDT. You have {balance:.2f} BDT.",
        'withdraw_request_msg': "💸 *Withdraw Request*\n\nAvailable: {balance:.2f} BDT\nSaved Methods: {methods_str}\n\nEnter the amount you want to withdraw (e.g. 5.00):",
        'invalid_amount': "❌ Invalid amount. Please enter a number (e.g. 5.50) or /cancel.",
        'amount_greater_zero': "❌ Amount must be greater than 0.",
        'withdraw_success': "✅ Withdrawal request of {amount:.2f} BDT submitted successfully!",
        'withdraw_error': "❌ Error: {msg}",
        'action_cancelled': "Action cancelled."
    },
    'bn': {
        'welcome_msg': "👋 হ্যালো {name}!\nGmail সেলিং বটে স্বাগতম।\nশুরু করতে নিচের একটি অপশন সিলেক্ট করুন।",
        'btn_register': "➕ নতুন অ্যাকাউন্ট রেজিস্টার করুন",
        'btn_my_accounts': "📋 আমার অ্যাকাউন্টগুলো",
        'btn_balance': "💰 ব্যালেন্স",
        'btn_referrals': "👥 আমার রেফারেল",
        'btn_settings': "⚙️ সেটিংস",
        'btn_help': "💬 সাহায্য",
        'balance_msg': "💰 *ওয়ালেট ব্যালেন্স*\n\n✅ অ্যাভেইলেবল: {balance:.2f} BDT\n⏳ হোল্ড: {hold:.2f} BDT\n\n'হোল্ড' এর টাকা অ্যাডমিন অ্যাপ্রুভালের পর 'অ্যাভেইলেবল' এ চলে যাবে (প্রায় ২৪ ঘণ্টা)।",
        'withdraw_btn': "💸 উইথড্র",
        'no_accounts_sold': "আপনি এখনো কোনো অ্যাকাউন্ট বিক্রি করেননি।",
        'my_accounts_title': "📋 *আমার শেষ ১০টি অ্যাকাউন্ট:*\n\n",
        'referrals_msg': "👥 *আমার রেফারেল*\n\n💰 *সেল প্রতি কমিশন:* {bonus:.2f} BDT\n👥 মোট রেফারেল: {count}\n\n🔗 *আপনার রেফারেল লিংক:*\n`{link}`",
        'help_msg': "সাহায্যের জন্য [সাপোর্ট](https://t.me/Gmail_Employee_Support) এ যোগাযোগ করুন।",
        'settings_title': "⚙️ *সেটিংস*",
        'payment_methods_btn': "💳 পেমেন্ট মেথড",
        'language_btn': "🌐 ভাষা (Language)",
        'close_btn': "🚫 বন্ধ করুন",
        'back_btn': "🔙 পেছনে",
        'payment_methods_msg': "💳 *পেমেন্ট মেথড*\n\nআপনার সেভ করা মেথড:\n{info_str}\n\nঅ্যাড/এডিট করতে একটি মেথড সিলেক্ট করুন:",
        'select_language': "🌐 ভাষা সিলেক্ট করুন:",
        'language_set': "✅ ভাষা বাংলা সেট করা হয়েছে (সেভড)।",
        'enter_payment': "আপনার *{method} {label}* দিন:",
        'payment_saved': "✅ সেভড {method}: `{value}`",
        'no_accounts_avail': "⚠️ কোনো অ্যাকাউন্ট নেই। দয়া করে পরে চেষ্টা করুন।",
        'register_msg': "নিচের তথ্য দিয়ে অ্যাকাউন্ট তৈরি করুন এবং {price} BDT পান\n\nনাম: `{first} {last}`\nইমেইল: `{email}`\nপাসওয়ার্ড: `{password}`\n{recovery_section}\n\n🔒 অবশ্যই এই তথ্যগুলো ব্যবহার করবেন।",
        'btn_done': "✔️ সম্পন্ন (Done)",
        'btn_cancel_reg': "🚫 বাতিল করুন",
        'btn_how_to': "❓ কিভাবে অ্যাকাউন্ট করবেন",
        'account_submitted': "✅ অ্যাকাউন্ট জমা দেওয়া হয়েছে! আপনি {price} BDT অর্জন করেছেন (হোল্ড)।\nঅ্যাডমিন ২৪ ঘণ্টার মধ্যে ভেরিফাই করবেন।\n'আমার অ্যাকাউন্টগুলো' তে স্ট্যাটাস চেক করুন।",
        'reg_cancelled': "🚫 রেজিস্ট্রেশন বাতিল করা হয়েছে। অ্যাকাউন্ট রিলিজড।",
        'help_create_msg': "gmail.com এ যান, Create Account এ ক্লিক করুন, দেওয়া ইমেইল এবং পাসওয়ার্ড ব্যবহার করুন। ক্লিন আইপি ব্যবহার করুন।",
        'withdraw_no_method': "⚠️ আপনি কোনো পেমেন্ট মেথড সেট করেননি।\nদয়া করে ⚙️ সেটিংস > পেমেন্ট মেথড এ গিয়ে আগে সেট করুন।",
        'withdraw_min_error': "⚠️ সর্বনিম্ন উইথড্র 0.50 BDT। আপনার আছে {balance:.2f} BDT।",
        'withdraw_request_msg': "💸 *উইথড্র রিকোয়েস্ট*\n\nঅ্যাভেইলেবল: {balance:.2f} BDT\nসেভড মেথড: {methods_str}\n\nআপনি কত টাকা তুলতে চান লিখুন (যেমন: 5.00):",
        'invalid_amount': "❌ ভুল অ্যামাউন্ট। দয়া করে সংখ্যা লিখুন (যেমন: 5.50) অথবা /cancel দিন।",
        'amount_greater_zero': "❌ অ্যামাউন্ট ০ এর বেশি হতে হবে।",
        'withdraw_success': "✅ {amount:.2f} BDT এর উইথড্র রিকোয়েস্ট সফলভাবে জমা হয়েছে!",
        'withdraw_error': "❌ এরর: {msg}",
        'action_cancelled': "অ্যাকশন বাতিল করা হয়েছে।"
    }
}

async def get_text(user_id, key, lang=None, **kwargs):
    if not lang:
        lang = await db.get_user_language(user_id)
    text = TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)
    return text.format(**kwargs) if kwargs else text

# States for Settings & Withdraw
SET_PAYMENT = 1
ENTER_PAYMENT_VALUE = 2
WITHDRAW_AMOUNT = 3

REQUIRED_CHANNEL = "@Gmail_Employee_News"

async def check_membership(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception as e:
        logging.error(f"Error checking membership for {user_id}: {e}")
        # If bot is not admin or channel invalid, we might want to fail open or closed.
        # For now, let's log and return False (fail closed) to be safe, or True to not block if error.
        # Given "Bot must be admin", False is safer to ensure it works as intended.
        return False
    return False

async def send_join_channel_message(update, context):
    user = update.effective_user
    text = (
        f"👋 Hey, {user.first_name} আপনাকে স্বাগতম!\n\n"
        "🔴 সমস্ত আপডেট পেতে আমাদের বটের অফিসিয়াল চ্যানেলে যোগদান করুন ⬇️\n\n"
        "⚠️ চ্যানেলে জয়েন না করলে বট ব্যবহার করতে পারবেন না!"
    )
    keyboard = [
        [InlineKeyboardButton("💎 Join Channel", url="https://t.me/Gmail_Employee_News")],
        [InlineKeyboardButton("✅ জয়েন করেছি", callback_data="check_join")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        # If called from a callback (unlikely for initial check, but possible)
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup)

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    try:
        lang = await db.get_user_language(user.id)
        keyboard = [
            [await get_text(user.id, 'btn_register', lang=lang), await get_text(user.id, 'btn_my_accounts', lang=lang)],
            [await get_text(user.id, 'btn_balance', lang=lang), await get_text(user.id, 'btn_referrals', lang=lang)],
            [await get_text(user.id, 'btn_settings', lang=lang), await get_text(user.id, 'btn_help', lang=lang)]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        text = await get_text(user.id, 'welcome_msg', lang=lang, name=user.first_name)
        
        await context.bot.send_message(chat_id=user.id, text=text, reply_markup=reply_markup)
    except Exception as e:
        logging.error(f"Error sending main menu: {e}")

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    is_member = await check_membership(user_id, context)
    
    if is_member:
        await query.answer("✅ আপনি চ্যানেলে জয়েন করেছেন!")
        await query.message.delete()
        
        # Initial start flow - Register if not exists
        await db.add_user(user_id, query.from_user.full_name)
        
        await send_main_menu(update, context, query.from_user)
    else:
        await query.answer("⚠️ আপনি এখনো চ্যানেলে জয়েন করেননি!", show_alert=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logging.info(f"Start command received from user {update.effective_user.id}")
        user = update.effective_user
        args = context.args
        referrer_id = None
        
        if args and args[0].isdigit():
            referrer_id = int(args[0])
            if referrer_id == user.id:
                referrer_id = None
        
        # Check Channel Membership
        if not await check_membership(user.id, context):
            await send_join_channel_message(update, context)
            return

        # Check Ban Status
        if await db.check_ban(user.id):
            await update.message.reply_text("🚫 You are banned from using this bot.")
            return

        is_new = await db.add_user(user.id, user.full_name, referrer_id)
        
        if is_new:
            # Notify Admins
            admins = await db.get_admins()
            if admins:
                admin_bot = Bot(token=ADMIN_BOT_TOKEN)
                for admin_id in admins:
                    try:
                        await admin_bot.send_message(admin_id, f"👤 *New Member Joined*\nName: {user.full_name}\nID: `{user.id}`", parse_mode="Markdown")
                    except Exception as e:
                        logging.error(f"Failed to notify admin {admin_id}: {e}")

        await send_main_menu(update, context, user)
        logging.info(f"Start reply sent to {user.id}")
    except Exception as e:
        logging.error(f"Error in start command: {e}", exc_info=True)
        # Avoid crashing if we can't reply
        try:
            await update.message.reply_text("An error occurred. Please try again later.")
        except:
            pass

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        user_id = update.effective_user.id
        logging.info(f"Message received from {user_id}: {text}")

        # Check Channel Membership
        if not await check_membership(user_id, context):
            await send_join_channel_message(update, context)
            return
            
        # Check Ban Status
        if await db.check_ban(user_id):
            await update.message.reply_text("🚫 You are banned from using this bot.")
            return

        
        # Determine functionality based on text (checking both English and Bangla)
        # We need a robust way to identify commands. 
        # For simplicity, we'll try to match the text against known button values for the user's language OR English
        
        lang = await db.get_user_language(user_id)
        t_en = TRANSLATIONS['en']
        t_bn = TRANSLATIONS['bn']
        t_cur = TRANSLATIONS.get(lang, t_en)
        
        if text in [t_en['btn_register'], t_bn['btn_register']]:
            await register_account(update, context)
            
        elif text in [t_en['btn_balance'], t_bn['btn_balance']]:
            balance, hold = await db.get_user_balance(user_id)
            keyboard = [[InlineKeyboardButton(await get_text(user_id, 'withdraw_btn'), callback_data="withdraw_start")]]
                
            await update.message.reply_text(
                await get_text(user_id, 'balance_msg', balance=balance, hold=hold),
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            
        elif text in [t_en['btn_my_accounts'], t_bn['btn_my_accounts']]:
            history = await db.get_user_history_list(user_id)
            if not history:
                await update.message.reply_text(await get_text(user_id, 'no_accounts_sold'))
            else:
                msg = await get_text(user_id, 'my_accounts_title')
                for email, password, date, status in history:
                    status_icon = "✅" if status == 'sold' else "⏳" if status == 'submitted' else "❌"
                    msg += f"{status_icon} `{email}`\n"
                await update.message.reply_text(msg, parse_mode="Markdown")
                
        elif text in [t_en['btn_referrals'], t_bn['btn_referrals']]:
            count = await db.get_referral_stats(user_id)
            bonus = await db.get_referral_bonus()
            bot_username = context.bot.username
            link = f"https://t.me/{bot_username}?start={user_id}"
            await update.message.reply_text(
                await get_text(user_id, 'referrals_msg', bonus=bonus, count=count, link=link),
                parse_mode="Markdown"
            )
            
        elif text in [t_en['btn_help'], t_bn['btn_help']]:
            await update.message.reply_text(await get_text(user_id, 'help_msg'))
            
        elif text in [t_en['btn_settings'], t_bn['btn_settings']]:
            await settings_menu(update, context)

    except Exception as e:
        logging.error(f"Error in handle_message: {e}", exc_info=True)
        await update.message.reply_text("An error occurred processing your request.")

# --- Withdraw Flow ---
async def withdraw_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    # Check Channel Membership
    if not await check_membership(user_id, context):
        await send_join_channel_message(update, context)
        return ConversationHandler.END
    
    # Check if payment info exists
    pay_info = await db.get_payment_info(user_id)
    if not pay_info:
        await query.message.reply_text(await get_text(user_id, 'withdraw_no_method'))
        return ConversationHandler.END
        
    balance, _ = await db.get_user_balance(user_id)
    if balance < 0.50:
         await query.message.reply_text(await get_text(user_id, 'withdraw_min_error', balance=balance))
         return ConversationHandler.END

    methods_str = ", ".join(pay_info.keys())
    await query.message.reply_text(
        await get_text(user_id, 'withdraw_request_msg', balance=balance, methods_str=methods_str),
        parse_mode="Markdown"
    )
    return WITHDRAW_AMOUNT

async def withdraw_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    try:
        amount = float(update.message.text)
    except ValueError:
        await update.message.reply_text(await get_text(user_id, 'invalid_amount'))
        return WITHDRAW_AMOUNT
        
    if amount <= 0:
         await update.message.reply_text(await get_text(user_id, 'amount_greater_zero'))
         return WITHDRAW_AMOUNT

    pay_info = await db.get_payment_info(user_id)
    details = json.dumps(pay_info)
    
    success, msg = await db.create_withdrawal(user_id, amount, "Manual", details)
    if success:
        await update.message.reply_text(await get_text(user_id, 'withdraw_success', amount=amount))
        
        # Notify Admins
        admins = await db.get_admins()
        if admins:
            admin_bot = Bot(token=ADMIN_BOT_TOKEN)
            for admin_id in admins:
                try:
                    await admin_bot.send_message(
                        admin_id, 
                        f"💸 *New Withdrawal Request*\n"
                        f"User ID: `{user_id}`\n"
                        f"Amount: `BDT {amount:.2f}`",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logging.error(f"Failed to notify admin {admin_id}: {e}")
    else:
        await update.message.reply_text(await get_text(user_id, 'withdraw_error', msg=msg))
        
    return ConversationHandler.END

# --- Settings Flow ---
async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = [
        [InlineKeyboardButton(await get_text(user_id, 'payment_methods_btn'), callback_data="settings_payment")],
        [InlineKeyboardButton(await get_text(user_id, 'language_btn'), callback_data="settings_language")],
        [InlineKeyboardButton(await get_text(user_id, 'close_btn'), callback_data="close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = await get_text(user_id, 'settings_title')
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    
    # Check Channel Membership
    if not await check_membership(user_id, context):
        await send_join_channel_message(update, context)
        return ConversationHandler.END
    
    if data == "settings_payment":
        keyboard = [
            [InlineKeyboardButton("Binance UID", callback_data="pay_Binance")],
            [InlineKeyboardButton("Bkash", callback_data="pay_Bkash")],
            [InlineKeyboardButton("Nagad", callback_data="pay_Nagad")],
            [InlineKeyboardButton("Rocket", callback_data="pay_Rocket")],
            [InlineKeyboardButton(await get_text(user_id, 'back_btn'), callback_data="settings_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        info = await db.get_payment_info(user_id)
        info_str = "\n".join([f"• {k}: `{v}`" for k,v in info.items()]) if info else "No methods set."
        
        await query.edit_message_text(
            await get_text(user_id, 'payment_methods_msg', info_str=info_str),
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return SET_PAYMENT
        
    elif data == "settings_language":
         keyboard = [
            [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"), InlineKeyboardButton("🇧🇩 Bangla", callback_data="lang_bn")],
            [InlineKeyboardButton(await get_text(user_id, 'back_btn'), callback_data="settings_back")]
        ]
         await query.edit_message_text(await get_text(user_id, 'select_language'), reply_markup=InlineKeyboardMarkup(keyboard))
         
    elif data.startswith("lang_"):
        lang = data.split("_")[1]
        
        logging.info(f"User {user_id} switching language to {lang}")
        await db.set_user_language(user_id, lang)
        
        # Verify it was set
        new_lang = await db.get_user_language(user_id)
        logging.info(f"User {user_id} language in DB is now: {new_lang}")
        
        # Update text immediately
        await query.edit_message_text(await get_text(user_id, 'language_set', lang=lang))
        
        # Refresh Main Menu Keyboard
        user = query.from_user
        keyboard = [
            [await get_text(user.id, 'btn_register', lang=lang), await get_text(user.id, 'btn_my_accounts', lang=lang)],
            [await get_text(user.id, 'btn_balance', lang=lang), await get_text(user.id, 'btn_referrals', lang=lang)],
            [await get_text(user.id, 'btn_settings', lang=lang), await get_text(user.id, 'btn_help', lang=lang)]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        # Send a fresh message confirming the change (which updates the keyboard)
        # We use a trick: delete the old 'welcome' message if we could, but we can't easily track it.
        # Just sending a new one is standard.
        await context.bot.send_message(
            chat_id=user_id,
            text=await get_text(user.id, 'welcome_msg', lang=lang, name=user.first_name),
            reply_markup=reply_markup
        )
        
    elif data == "settings_back":
        await settings_menu(update, context)
        return ConversationHandler.END
        
    elif data == "close":
        await query.delete_message()
        return ConversationHandler.END

async def payment_method_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    method = query.data.split("_")[1]
    context.user_data['payment_method'] = method
    
    label = "UID" if method == "Binance" else "Number"
    
    await query.edit_message_text(await get_text(user_id, 'enter_payment', method=method, label=label), parse_mode="Markdown")
    return ENTER_PAYMENT_VALUE

async def save_payment_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = update.message.text
    method = context.user_data.get('payment_method')
    user_id = update.effective_user.id
    
    await db.update_payment_info(user_id, {method: value})
    
    await update.message.reply_text(await get_text(user_id, 'payment_saved', method=method, value=value), parse_mode="Markdown")
    
    await settings_menu(update, context)
    return ConversationHandler.END

async def register_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    account = await db.get_available_account(user_id)
    
    if not account:
        await update.message.reply_text(await get_text(user_id, 'no_accounts_avail'))
        return

    acc_id, email, password, first, last = account
    price = await db.get_price()
    recovery = await db.get_recovery_email()
    # first, last = await db.get_names() # Removed global names

    
    # Explicit instruction
    if recovery and recovery != "None":
        recovery_section = (
            f"\n🛡️ **Recovery Email:** `{recovery}`\n"
            "⚠️ *You MUST set this email as the recovery email for the account!*"
        )
    else:
        recovery_section = ""
    
    message = await get_text(user_id, 'register_msg', price=price, first=first, last=last, email=email, password=password, recovery_section=recovery_section)
    
    keyboard = [
        [InlineKeyboardButton(await get_text(user_id, 'btn_done'), callback_data="done")],
        [InlineKeyboardButton(await get_text(user_id, 'btn_cancel_reg'), callback_data="cancel")],
        [InlineKeyboardButton(await get_text(user_id, 'btn_how_to'), callback_data="help_create")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Check Channel Membership
    if not await check_membership(user_id, context):
        await send_join_channel_message(update, context)
        return

    # Check Ban Status
    if await db.check_ban(user_id):
        await query.answer("🚫 You are banned.", show_alert=True)
        return
    data = query.data
    
    if data == "done":
        try:
             success, msg, acc_info = await db.mark_account_submitted(user_id)
             if success:
                price = msg
                id_val, email, password, f, l = acc_info
                
                await query.edit_message_text(await get_text(user_id, 'account_submitted', price=price))
                
                # Notify Admins
                admins = await db.get_admins()
                if admins:
                    admin_bot = Bot(token=ADMIN_BOT_TOKEN)
                    for admin_id in admins:
                        try:
                             # Note: Admin needs to have started Admin Bot (or have chatted with it)? 
                             # YES. But here we are using ADMIN_BOT_TOKEN.
                             # If we use ADMIN_BOT_TOKEN, we are the Admin Bot.
                             # Can Admin Bot message the Admin? YES, because Admin started Admin Bot.
                             await admin_bot.send_message(admin_id, f"📥 *New Account Submitted*\nUser: `{user_id}`\nEmail: `{email}`", parse_mode="Markdown")
                        except Exception as e:
                            logging.error(f"Failed to notify admin {admin_id}: {e}")
             else:
                await query.edit_message_text(f"❌ Error: {msg}")
        except AttributeError:
             await query.edit_message_text("❌ System error.")

    elif data == "cancel":
        await db.cancel_registration(user_id)
        await query.edit_message_text(await get_text(user_id, 'reg_cancelled'))

    elif data == "help_create":
        await query.message.reply_text(await get_text(user_id, 'help_create_msg'))
        
    elif data == "close":
        await query.delete_message()

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(await get_text(user_id, 'action_cancelled'))
    return ConversationHandler.END

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(msg="Exception while handling an update:", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text("An internal error occurred. Admin has been notified.")
        except:
             pass # If we can't reply, simple log is enough

def get_user_handler():
    cancel_handler = CommandHandler("cancel", cancel)
    
    # Settings Conversation
    conv_settings = ConversationHandler(
        entry_points=[CallbackQueryHandler(settings_callback, pattern="^settings_payment$")],
        states={
            SET_PAYMENT: [CallbackQueryHandler(payment_method_choice, pattern="^pay_")],
            ENTER_PAYMENT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_payment_value)]
        },
        fallbacks=[cancel_handler, CallbackQueryHandler(settings_callback, pattern="^settings_back$"), CallbackQueryHandler(settings_callback, pattern="^close$")]
    )
    
    # Withdraw Conversation
    conv_withdraw = ConversationHandler(
        entry_points=[CallbackQueryHandler(withdraw_start, pattern="^withdraw_start$")],
        states={
            WITHDRAW_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_process)]
        },
        fallbacks=[cancel_handler]
    )

    return [
        CommandHandler("start", start),
        conv_settings,
        conv_withdraw,
        
        CallbackQueryHandler(settings_callback, pattern="^settings_"),
        CallbackQueryHandler(settings_callback, pattern="^lang_"),
        CallbackQueryHandler(settings_callback, pattern="^close$"),
        CallbackQueryHandler(check_join_callback, pattern="^check_join$"),

        
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
        CallbackQueryHandler(button_handler)
    ]
