import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 全局变量用于存储记账数据，可根据需求改用数据库持久化
# 数据结构示例：{"income": [], "expense": [], "total_income": 0, "total_expense": 0, "exchange_rate": 7.3}
bot_data = {
    "income": [],
    "expense": [],
    "total_income": 0,
    "total_expense": 0,
    "exchange_rate": 7.3  # 固定汇率，可按需调整
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """启动命令，发送欢迎信息"""
    await update.message.reply_text('欢迎使用记账机器人！\n输入 `/add +金额` 记录入款，`/add -金额` 记录下发（支出），试试吧～')

async def add_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理添加记账记录的逻辑"""
    text = update.message.text
    # 提取金额，简单处理指令格式，假设指令是 /add +100 或 /add -100 形式
    try:
        amount_str = text.split()[1]
        amount = float(amount_str)
        if amount > 0:
            # 入款
            bot_data["total_income"] += amount
            bot_data["income"].append({
                "time": update.message.date.strftime("%H:%M:%S"),
                "amount": amount,
                "usdt_amount": amount / bot_data["exchange_rate"]
            })
            reply_text = generate_income_reply(bot_data)
        else:
            # 下发（支出）
            bot_data["total_expense"] += abs(amount)
            bot_data["expense"].append({
                "time": update.message.date.strftime("%H:%M:%S"),
                "amount": abs(amount),
                "original_amount": abs(amount) * bot_data["exchange_rate"]  # 反向体现对应原金额
            })
            reply_text = generate_expense_reply(bot_data)
        await update.message.reply_text(reply_text)
    except (IndexError, ValueError) as e:
        await update.message.reply_text('指令格式错误～请输入 `/add +金额` 或 `/add -金额` ，比如 `/add +100`  、 `/add -50` ')

def generate_income_reply(data):
    """生成入款后的模板回复"""
    income = data["income"][-1]  # 取最新一条入款
    income_time = income["time"]
    income_amount = data["total_income"]  # 累计入款
    usdt_amount = income["usdt_amount"]
    # 组装入款部分文案
    income_text = f"土豆客服 飞博游戏\n\n已入款（{len(data['income'])}笔）：\n{income_time} {income_amount} / {data['exchange_rate']}={usdt_amount:.2f}\n\n"
    
    # 组装下发（支出）部分文案
    expense_text = "已下发（{}笔）：\n".format(len(data["expense"]))
    for exp in data["expense"]:
        expense_text += f"{exp['time']} {exp['amount']} ({exp['original_amount']:.2f})\n"
    
    # 计算应下发、已下发、未下发等汇总
    total_income_usdt = data["total_income"] / data["exchange_rate"]
    total_expense_usdt = data["total_expense"] / data["exchange_rate"]
    total_income_original = data["total_income"]
    total_expense_original = data["total_expense"]
    
    summary_text = f"""总入款金额：{total_income_original:.2f}
费率：0%
固定汇率：{data['exchange_rate']}
应下发：{total_income_original:.2f} | {total_income_usdt:.2f} (USDT)
已下发：{total_expense_original:.2f} | {total_expense_usdt:.2f} (USDT)
未下发：{total_income_original - total_expense_original:.2f} | {total_income_usdt - total_expense_usdt:.2f} (USDT)"""
    
    return income_text + expense_text + summary_text

def generate_expense_reply(data):
    """生成下发（支出）后的模板回复"""
    expense = data["expense"][-1]  # 取最新一条支出
    # 先组装入款部分文案
    income_text = f"土豆客服 飞博游戏\n\n已入款（{len(data['income'])}笔）：\n"
    for inc in data["income"]:
        income_text += f"{inc['time']} {inc['amount']} / {data['exchange_rate']}={inc['usdt_amount']:.2f}\n"
    income_text += "\n"
    
    # 组装下发（支出）部分文案
    expense_time = expense["time"]
    expense_amount = expense["amount"]
    expense_original = expense["original_amount"]
    expense_text = f"已下发（{len(data['expense'])}笔）：\n{expense_time} {expense_amount} ({expense_original:.2f})\n\n"
    
    # 计算应下发、已下发、未下发等汇总
    total_income_usdt = data["total_income"] / data["exchange_rate"]
    total_expense_usdt = data["total_expense"] / data["exchange_rate"]
    total_income_original = data["total_income"]
    total_expense_original = data["total_expense"]
    
    summary_text = f"""总入款金额：{total_income_original:.2f}
费率：0%
固定汇率：{data['exchange_rate']}
应下发：{total_income_original:.2f} | {total_income_usdt:.2f} (USDT)
已下发：{total_expense_original:.2f} | {total_expense_usdt:.2f} (USDT)
未下发：{total_income_original - total_expense_original:.2f} | {total_income_usdt - total_expense_usdt:.2f} (USDT)"""
    
    return income_text + expense_text + summary_text

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """错误处理"""
    logging.error(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    # 替换为你自己的 Telegram Bot Token
    token = "YOUR_TELEGRAM_BOT_TOKEN"  
    application = ApplicationBuilder().token(token).build()
    
    # 添加命令处理器
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('add', add_record))
    
    # 添加错误处理器
    application.add_error_handler(error_handler)
    
    # 启动机器人
    application.run_polling()
