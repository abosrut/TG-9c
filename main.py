from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from app import telegram_bot
from app import database_manager
from app import logger_config
from config import TELEGRAM_BOT_TOKEN

def main():
    logger_config.setup_logging()
    
    database_manager.init_and_populate_db()

    bot_data = { 'db': database_manager }

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.bot_data.update(bot_data)
    
    application.add_handler(CommandHandler("start", telegram_bot.start))
    application.add_handler(CommandHandler("help", telegram_bot.help_command))
    application.add_handler(CallbackQueryHandler(telegram_bot.button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_bot.text_handler))
    
    application.run_polling()

if __name__ == '__main__':
    main()