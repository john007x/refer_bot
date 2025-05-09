import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
from keep_alive import keep_alive
import json

# Constants
TOKEN = "7764075200:AAGd_gSXxi4fa5edC0EdbkDgqakYJjXHWGg"
CHANNEL_IDS = ["@five_star_official5", "-1002684151914"]  # পাবলিক চ্যানেলের username ও ID
MIN_WITHDRAW = 8400
REFER_AMOUNT = 210

def get_channel_link(channel_id):
    """চ্যানেলের লিংক ফরমেট করে দেয়া"""
    return f"https://t.me/{channel_id}"

# Data Storage
def load_data():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open('users.json', 'w') as f:
        json.dump(data, f)

users_data = load_data()

def check_member(update: Update, context: CallbackContext) -> bool:
    """
    Verify if user is a member of the required channels
    Returns True if user is a member, False otherwise
    """
    try:
        user_id = update.effective_user.id
        
        for channel_id in CHANNEL_IDS:
            try:
                # Try to get chat member status
                member = context.bot.get_chat_member(channel_id, user_id)
                
                # Check if user is a member, admin, or creator
                if member.status in ['member', 'administrator', 'creator']:
                    return True
                
            except Exception as e:
                # Log specific error for debugging
                print(f"Error checking channel {channel_id} for user {user_id}: {str(e)}")
                continue
        
        # If we reach here, user is not a member of any required channel
        return False
        
    except Exception as e:
        # Log error and return False in case of any unexpected error
        print(f"Unexpected error in check_member: {str(e)}")
        return False

def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)

    # Initialize user data if not exists
    if user_id not in users_data:
        users_data[user_id] = {
            'balance': 0,
            'referrals': [],
            'withdraw_status': False
        }
        save_data(users_data)

    # Check referral
    if len(context.args) > 0:
        referrer_id = context.args[0]
        if referrer_id != user_id and referrer_id in users_data and user_id not in users_data[
                referrer_id]['referrals']:
            users_data[referrer_id]['referrals'].append(user_id)
            users_data[referrer_id]['balance'] += REFER_AMOUNT
            save_data(users_data)

    # Check if user is already a member
    if check_member(update, context):
        show_dashboard(update, context)
        return

    welcome_msg = """স্বাগতম!
এই বটের মাধ্যমে আপনি রেফার করে ইনকাম করতে পারবেন।

✅ প্রথমে আমাদের চ্যানেলটি জয়েন করুন:
{}""".format(get_channel_link(CHANNEL_IDS[0]))

    keyboard = [[
        InlineKeyboardButton("চ্যানেল জয়েন করুন",
                             url=get_channel_link(CHANNEL_IDS[0]))
    ], [InlineKeyboardButton("✅ চেক জয়েন", callback_data='check_join')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(welcome_msg, reply_markup=reply_markup)


def show_dashboard(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📊 আমার ব্যালেন্স", callback_data='balance')],
        [InlineKeyboardButton("🔗 রেফার লিংক", callback_data='refer_link')],
        [InlineKeyboardButton("👥 রেফার সংখ্যা", callback_data='refer_count')],
        [
            InlineKeyboardButton("💸 উইথড্র রিকোয়েস্ট",
                                 callback_data='withdraw')
        ], [InlineKeyboardButton("❓ হেল্প", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Check if this is a callback query or a regular message
    if update.callback_query:
        update.callback_query.message.edit_text(
            "মেনু থেকে যেকোনো অপশন সিলেক্ট করুন:", reply_markup=reply_markup)
    else:
        update.message.reply_text("মেনু থেকে যেকোনো অপশন সিলেক্ট করুন:",
                                  reply_markup=reply_markup)


def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = str(query.from_user.id)

    if query.data == 'check_join':
        # Check if user is already a member
        if check_member(update, context):
            query.edit_message_text(
                "✅ আপনি সফলভাবে চ্যানেলে জয়েন করেছেন। এখন মেনু থেকে অন্য অপশন সিলেক্ট করুন।"
            )
            show_dashboard(update, context)
        else:
            # If not a member, show error and keep the join button visible
            query.answer("দয়া করে প্রথমে চ্যানেল জয়েন করুন!")
            # Keep the message with join button visible
            keyboard = [[
                InlineKeyboardButton("চ্যানেল জয়েন করুন",
                                     url=get_channel_link(CHANNEL_IDS[0]))
            ], [InlineKeyboardButton("✅ চেক জয়েন", callback_data='check_join')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                "দয়া করে প্রথমে চ্যানেল জয়েন করুন এবং পরে আবার চেক করুন।",
                reply_markup=reply_markup
            )
            return

    elif query.data == 'balance':
        balance = users_data[user_id]['balance']
        keyboard = [[InlineKeyboardButton("🔙 ব্যাক", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(f"💰 আপনার বর্তমান ব্যালেন্স: {balance} টাকা", reply_markup=reply_markup)

    elif query.data == 'refer_link':
        refer_link = f"https://t.me/cashgurubd_bot?start={user_id}"
        keyboard = [[InlineKeyboardButton("🔙 ব্যাক", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(f"🔗 আপনার রেফারাল লিংক:\n\n`{refer_link}`\n\nএই লিংক শেয়ার করে রেফার করুন", reply_markup=reply_markup, parse_mode='Markdown')

    elif query.data == 'refer_count':
        referrals = len(users_data[user_id]['referrals'])
        keyboard = [[InlineKeyboardButton("🔙 ব্যাক", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(f"👥 আপনার মোট রেফার সংখ্যা: {referrals} জন", reply_markup=reply_markup)

    elif query.data == 'withdraw':
        balance = users_data[user_id]['balance']
        if balance >= MIN_WITHDRAW:
            # উইথড্র বাটন দেখানো হবে
            keyboard = [
                [InlineKeyboardButton("💰 বিকাশ", callback_data='withdraw_bkash')],
                [InlineKeyboardButton("💰 নগদ", callback_data='withdraw_nagad')],
                [InlineKeyboardButton("💰 রকেট", callback_data='withdraw_rocket')],
                [InlineKeyboardButton("🔙 ব্যাক", callback_data='back_to_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text("💸 উইথড্র মেথড সিলেক্ট করুন:", reply_markup=reply_markup)
            return
        else:
            remaining = MIN_WITHDRAW - balance
            keyboard = [[InlineKeyboardButton("🔙 ব্যাক", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                f"⚠️ উইথড্র করতে আরো {remaining} টাকা এবং {remaining//REFER_AMOUNT} জন রেফার প্রয়োজন।", reply_markup=reply_markup
            )

    elif query.data == 'help':
        help_text = """❓ হেল্প সেকশন:

• প্রতিটি রেফারে আপনি পাবেন ২১০ টাকা
• মিনিমাম উইথড্র: ৮৪০০ টাকা (৪০ জন রেফার)
• পেমেন্ট ২৪ ঘণ্টার মধ্যে করা হবে"""
        keyboard = [[InlineKeyboardButton("🔙 ব্যাক", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(help_text, reply_markup=reply_markup)
        
    elif query.data == 'back_to_menu':
        show_dashboard(update, context)
        
    elif query.data.startswith('withdraw_'):
        payment_method = query.data.split('_')[1]
        users_data[user_id]['pending_withdraw'] = {
            'method': payment_method,
            'amount': users_data[user_id]['balance'],
            'status': 'pending'
        }
        save_data(users_data)
        
        query.edit_message_text(f"💳 আপনার {payment_method.upper()} নাম্বার দিন:\n\nসিস্টেম এখন আপনার নাম্বার অপেক্ষা করছে...")
        
        # পেমেন্ট নাম্বার সেট করার জন্য স্টেট সেট করা
        context.user_data['waiting_for_payment'] = {
            'method': payment_method,
            'user_id': user_id
        }

    query.answer()


def shanto(update: Update, context: CallbackContext):
    # প্রথমে এডমিন চেক করা হবে
    user_id = str(update.effective_user.id)
    if user_id != "6231391778":  # আপনার টেলিগ্রাম ID
        update.message.reply_text("আপনি এডমিন নন।")
        return

    keyboard = [
        [InlineKeyboardButton("📊 টোটাল ইনকাম", callback_data='shanto_income')],
        [InlineKeyboardButton("👥 টোটাল ইউজার", callback_data='shanto_users')],
        [InlineKeyboardButton("📊 টোটাল রেফার", callback_data='shanto_referrals')],
        [InlineKeyboardButton("💸 টোটাল উইথড্র", callback_data='shanto_withdraw')],
        [InlineKeyboardButton("📊 ইউজার স্ট্যাটিস্টিক্স", callback_data='shanto_stats')],
        [InlineKeyboardButton("🔍 চ্যানেল স্ট্যাটাস", callback_data='shanto_channels')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("এডমিন প্যানেল", reply_markup=reply_markup)


def shanto_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    if data == 'shanto_income':
        total_income = sum(user['balance'] for user in users_data.values())
        query.edit_message_text(f"টোটাল ইনকাম: {total_income} টাকা")

    elif data == 'shanto_users':
        total_users = len(users_data)
        query.edit_message_text(f"টোটাল ইউজার: {total_users} জন")

    elif data == 'shanto_referrals':
        total_referrals = sum(len(user['referrals']) for user in users_data.values())
        query.edit_message_text(f"টোটাল রেফার: {total_referrals} জন")

    elif data == 'shanto_withdraw':
        total_withdraw = sum(user['balance'] for user in users_data.values() if user.get('withdraw_status', False))
        query.edit_message_text(f"টোটাল উইথড্র: {total_withdraw} টাকা")

    elif data == 'shanto_stats':
        total_users = len(users_data)
        total_referrals = sum(len(user['referrals']) for user in users_data.values())
        total_income = sum(user['balance'] for user in users_data.values())
        total_withdraw = sum(user['balance'] for user in users_data.values() if user.get('withdraw_status', False))

        stats = f"""📊 ইউজার স্ট্যাটিস্টিক্স:
• টোটাল ইউজার: {total_users} জন
• টোটাল রেফার: {total_referrals} জন
• টোটাল ইনকাম: {total_income} টাকা
• টোটাল উইথড্র: {total_withdraw} টাকা"""
        query.edit_message_text(stats)

    elif data == 'shanto_channels':
        channels = []
        for channel_id in CHANNEL_IDS:
            try:
                chat = context.bot.get_chat(channel_id)
                if chat.type == 'channel':
                    bot_member = context.bot.get_chat_member(channel_id, context.bot.id)
                    status = "এডমিন" if bot_member.status in ['administrator', 'creator'] else "মেম্বার"
                    channels.append(f"@{channel_id} - {status}")
            except Exception as e:
                print(f"Error checking channel {channel_id}: {str(e)}")
                continue
        
        if channels:
            message = "চ্যানেল স্ট্যাটাস:\n\n" + "\n".join(channels)
        else:
            message = "কোনো চ্যানেল নেই।"
        
        query.edit_message_text(message)

    query.answer()


def handle_message(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    text = update.message.text
    
    # পেমেন্ট নাম্বার প্রসেস করা
    if 'waiting_for_payment' in context.user_data:
        payment_info = context.user_data['waiting_for_payment']
        payment_user_id = payment_info['user_id']
        payment_method = payment_info['method']
        
        # পেমেন্ট নাম্বার সেভ করা
        users_data[payment_user_id]['pending_withdraw']['number'] = text
        users_data[payment_user_id]['withdraw_status'] = True
        save_data(users_data)
        
        # এডমিনকে নোটিফিকেশন পাঠানো
        admin_notification = f"""📢 নতুন উইথড্র রিকোয়েস্ট!

👤 ইউজার: {update.effective_user.first_name}
💳 মেথড: {payment_method.upper()}
💰 এমাউন্ট: {users_data[payment_user_id]['pending_withdraw']['amount']} টাকা
📱 নাম্বার: {text}"""
        
        try:
            context.bot.send_message(chat_id="6231391778", text=admin_notification)
        except Exception as e:
            print(f"Error sending admin notification: {str(e)}")
        
        # ইউজারকে কনফার্মেশন পাঠানো
        keyboard = [[InlineKeyboardButton("🔙 মেনুতে ফিরে যান", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            f"""✅ আপনার উইথড্র রিকোয়েস্ট সফলভাবে সাবমিট হয়েছে!

💳 মেথড: {payment_method.upper()}
💰 এমাউন্ট: {users_data[payment_user_id]['pending_withdraw']['amount']} টাকা
📱 নাম্বার: {text}

পেমেন্ট ২৪ ঘণ্টার মধ্যে করা হবে।""",
            reply_markup=reply_markup
        )
        
        # স্টেট ক্লিয়ার করা
        del context.user_data['waiting_for_payment']
    else:
        # অন্যান্য মেসেজ হ্যান্ডলিং
        update.message.reply_text(
            "দয়া করে /start কমান্ড দিয়ে বট শুরু করুন।"
        )


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("shanto", shanto))
    # প্যাটার্ন ওভারল্যাপিং ঠিক করা হয়েছে
    dp.add_handler(CallbackQueryHandler(shanto_callback, pattern='^shanto_'))
    dp.add_handler(CallbackQueryHandler(button_callback))
    
    # মেসেজ হ্যান্ডলার যোগ করা হয়েছে
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    keep_alive()
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
