from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from datetime import date, timedelta, datetime
import logging

from app import user_manager
from config import WEBAPP_URL

logger = logging.getLogger(__name__)

user_states = {}
DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
DAYS_UKR_SHORT = ["Пн", "Вт", "Ср", "Чт", "Пт"]
NUMBER_EMOJIS = {
    1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
    6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣",
}

def build_menu(buttons, n_cols):
    return [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]

async def show_main_menu(update, context, message_text="Добро пожаловать в главное меню!"):
    keyboard = [
        [InlineKeyboardButton("🗓️ Расписание", callback_data='show_schedule_days')],
        [InlineKeyboardButton("🔎 Поиск предмета", callback_data='search_subject')],
        [InlineKeyboardButton("📚 Загрузить ДЗ", callback_data='upload_homework')],
        [InlineKeyboardButton("🌐 Открыть веб-версию", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text=message_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=message_text, reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_number = user_manager.register_user(user_id)
    logger.info(f"[User #{user_number}] {update.effective_user.full_name} ({user_id}) started the bot.")
    
    await show_main_menu(update, context, f"Привет, {update.effective_user.first_name}!\nЧем могу помочь?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Используйте кнопки для навигации.\n/start - показать главное меню.")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_number = user_manager.register_user(user_id)
    state_info = user_states.get(user_id)
    db = context.bot_data['db']
    
    back_to_menu_button = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Главное меню", callback_data='go_back_to_main_menu')]])

    if not state_info:
        await update.message.reply_text("Не понимаю вас. Пожалуйста, используйте кнопки.")
        return

    state = state_info.get('state')

    if state == 'awaiting_subject_search':
        query = update.message.text
        logger.info(f"[User #{user_number}] Searched for: '{query}'")
        results = db.find_subject_schedule(query)
        message = f'🔎 *Результаты поиска по "{query}"*:\n\n'
        if not results:
            message += 'Ничего не найдено.'
        else:
            day_map_rus = {"Пн": "Понедельник", "Вт": "Вторник", "Ср": "Среда", "Чт": "Четверг", "Пт": "Пятница"}
            grouped_results = {}
            for day_ukr, lesson_num, time in results:
                if day_ukr not in grouped_results:
                    grouped_results[day_ukr] = []
                grouped_results[day_ukr].append((lesson_num, time))
            
            for day_ukr in DAYS_UKR_SHORT:
                if day_ukr in grouped_results:
                    day_name = day_map_rus.get(day_ukr, day_ukr)
                    message += f"*{day_name}*:\n"
                    for lesson_num, time in grouped_results[day_ukr]:
                        emoji_num = NUMBER_EMOJIS.get(lesson_num, f"{lesson_num}.")
                        message += f"  {emoji_num} _{time}_\n"
                    message += "\n"
        
        user_states[user_id] = None
        await update.message.reply_text(message, reply_markup=back_to_menu_button, parse_mode='Markdown')

    elif state == 'awaiting_hw_text':
        subject = state_info.get('subject')
        task = update.message.text
        logger.info(f"[User #{user_number}] Added homework for '{subject}': '{task}'")
        due_date = db.get_next_lesson_date(subject, date.today())
        
        if due_date:
            db.add_homework(subject, due_date, task)
            due_date_formatted = datetime.strptime(due_date, "%Y-%m-%d").strftime("%d.%m.%Y")
            message = f"✅ Домашка по предмету *{subject}* на *{due_date_formatted}* сохранена!"
        else:
            message = f"❌ Не удалось найти следующий урок по предмету *{subject}*. Домашка не сохранена."
        
        user_states[user_id] = None
        await update.message.reply_text(message, reply_markup=back_to_menu_button, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    db = context.bot_data['db']
    user_id = query.from_user.id
    user_number = user_manager.register_user(user_id)

    if data == 'go_back_to_main_menu':
        await show_main_menu(update, context)

    elif data == 'show_schedule_days':
        button_list = [InlineKeyboardButton(day, callback_data=f"show_day_{i}") for i, day in enumerate(DAYS)]
        keyboard = build_menu(button_list, n_cols=2)
        keyboard.append([InlineKeyboardButton("⬅️ Назад в меню", callback_data='go_back_to_main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите день недели:", reply_markup=reply_markup)

    elif data.startswith('show_day_'):
        day_index = int(data.split('_')[2])
        day_name = DAYS[day_index]
        logger.info(f"[User #{user_number}] Viewed schedule for {day_name}.")
        day_name_ukr = DAYS_UKR_SHORT[day_index]

        today = date.today()
        days_diff = day_index - today.weekday()
        target_date = today + timedelta(days=days_diff)
        target_date_str = target_date.strftime("%Y-%m-%d")
        
        schedule = db.get_schedule_for_day(day_name_ukr)
        homework = db.get_homework_for_date(target_date_str)
        
        message = f"🗓️ *Расписание на {day_name} ({target_date.strftime('%d.%m')})*\n\n"
        if not schedule:
            message += "Уроков нет! 🎉\n"
        else:
            for lesson in schedule:
                num, subject, time = lesson
                emoji_num = NUMBER_EMOJIS.get(num, f"{num}.")
                message += f"{emoji_num} *{subject}* "
                if time and time != "N/A":
                    message += f"⏰ _{time}_\n"
                else:
                    message += "\n"

        message += f"\n📚 *Домашнее задание*\n\n"
        if not homework:
            message += "Домашки нет! ✨\n"
        else:
            for hw in homework:
                subject, task = hw
                message += f"*{subject}:* {task}\n"

        keyboard = [[InlineKeyboardButton("⬅️ Назад к выбору дня", callback_data='show_schedule_days')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == 'search_subject':
        user_states[user_id] = {'state': 'awaiting_subject_search'}
        await query.edit_message_text("Введите название предмета для поиска:")
        
    elif data == 'upload_homework':
        subjects = db.get_subjects_by_frequency()
        button_list = [InlineKeyboardButton(s, callback_data=f"hw_subject_{s}") for s in subjects]
        keyboard = build_menu(button_list, n_cols=2)
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data='go_back_to_main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите предмет для добавления ДЗ:", reply_markup=reply_markup)
    
    elif data.startswith('hw_subject_'):
        subject = data.replace('hw_subject_', '', 1)
        user_states[user_id] = {'state': 'awaiting_hw_text', 'subject': subject}
        await query.edit_message_text(f"Пришлите текст домашки по предмету: *{subject}*", parse_mode='Markdown')