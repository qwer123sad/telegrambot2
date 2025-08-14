import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# 配置日志记录
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# 初始化记账变量
total_deposit = 0
total_withdrawal = 0
exchange_rate = 7.25
rate = 0

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_deposit, total_withdrawal
    text = update.message.text
    if text.startswith('+'):
        try:
            amount = float(text[1:])
            total_deposit += amount
            await update.message.reply_text(f"已入款：{text} \n总入款金额：{total_deposit}")
        except ValueError:
            await update.message.reply_text("入款格式错误，请输入正确的金额。")
    elif text.startswith('-'):
        try:
            amount = float(text[1:])
            if amount <= total_deposit:
                total_withdrawal += amount
                total_deposit -= amount
                await update.message.reply_text(f"已下发：{text} ({total_deposit + total_withdrawal}) \n总入款金额：{total_deposit}")
            else:
                await update.message.reply_text("下发金额超过可提取金额。")
        except ValueError:
            await update.message.reply_text("下发格式错误，请输入正确的金额。")
    else:
        await update.message.reply_text("请输入有效的指令，例如 +2888 或 -2888")

if __name__ == '__main__':
    application = ApplicationBuilder().token("8171585566:AAFz-IizTfOde-gbtXIAOnIBlawo-M3xxaM").build()

    message_handler = CommandHandler('handle_message', handle_message)
    application.add_handler(message_handler)

    application.run_polling()