import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton,ChatPermissions,MenuButtonCommands,BotCommand,BotCommandScopeAllPrivateChats,ReplyKeyboardRemove,BotCommandScopeChatAdministrators
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler,MessageHandler,ConversationHandler, CallbackContext,CallbackQueryHandler
from telegram.ext import filters
from telegram.constants import DiceEmoji, ParseMode,ChatType,MenuButtonType,BotCommandScopeType
from datetime import time, datetime, timedelta, timezone
import uuid
import sqlite3
import random

db = sqlite3.connect('db/ac.sqlite3')
db.execute('CREATE TABLE IF NOT EXISTS ac (id INTEGER PRIMARY KEY, chatID INTEGER, open BOOLEAN, temp INTEGER, mode TEXT)')
db.execute('CREATE TABLE IF NOT EXISTS lottery (id INTEGER PRIMARY KEY, lottery_sn TEXT, group_id INTEGER, creater_id INTEGER, lottery_title TEXT, lottery_number INTEGER, prize_number INTEGER, lottery_keyword TEXT,open BOOLEAN, joined_number INTEGER)')
db.execute('CREATE TABLE IF NOT EXISTS lottery_detail (id INTEGER PRIMARY KEY, lottery_sn TEXT, lottery_tgid INTEGER, win BOOLEAN)')
db.close()

def insert_ac(chatid,open,temp,mode):
    conn = sqlite3.connect("db/ac.sqlite3")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('INSERT INTO ac VALUES (null,?,?,?,?)',(chatid,open,temp,mode))
    conn.commit()
def get_ac(chatid):
    conn = sqlite3.connect("db/ac.sqlite3")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ac WHERE chatID = ?',(chatid,))
    result = cursor.fetchone()
    if not result:
        cursor.execute('INSERT INTO ac VALUES (null,?,?,?,?)',(chatid,True, 26,'cold'))
        conn.commit()
    cursor.close()
    conn.close()
    return result
def update_ac_temp(chatid,temp):
    conn = sqlite3.connect("db/ac.sqlite3")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('UPDATE ac SET temp = ? WHERE chatID = ?',(temp,chatid))
    conn.commit()
    cursor.close()
    conn.close()
def update_ac_mode(chatid,mode):
    conn = sqlite3.connect("db/ac.sqlite3")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('UPDATE ac SET mode = ? WHERE chatID = ?',(mode,chatid))
    conn.commit()
    cursor.close()
    conn.close()
def update_ac_open(chatid,open):
    conn = sqlite3.connect("db/ac.sqlite3")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('UPDATE ac SET open = ? WHERE chatID = ?',(open,chatid))
    conn.commit()
    cursor.close()
    conn.close()
def insert_lottery(lottery_sn, group_id, creater_id, lottery_title, lottery_number, prize_number, lottery_keyword,open = False,joined_number = 0):
    conn = sqlite3.connect("db/ac.sqlite3")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('INSERT INTO lottery VALUES (null,?,?,?,?,?,?,?,?,?)',(lottery_sn, group_id, creater_id, lottery_title, lottery_number, prize_number,lottery_keyword, open, joined_number))
    conn.commit()
def get_lottery_by_lottery_sn(lottery_sn):
    conn = sqlite3.connect("db/ac.sqlite3")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM lottery WHERE lottery_sn = ?',(lottery_sn,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result
def update_lottery_open(lottery_sn, open):
    conn = sqlite3.connect("db/ac.sqlite3")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('UPDATE lottery SET open = ? WHERE lottery_sn = ?',(open,lottery_sn))
    conn.commit()
    cursor.close()
    conn.close()
def update_lottery_joined_number(lottery_sn, joined_number):
    conn = sqlite3.connect("db/ac.sqlite3")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('UPDATE lottery SET joined_number = ? WHERE lottery_sn = ?',(joined_number,lottery_sn))
    conn.commit()
    cursor.close()
    conn.close()
def get_lottery_by_groupid(group_id, open = False):
    conn = sqlite3.connect("db/ac.sqlite3")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM lottery WHERE group_id = ? and open = ?',(group_id, open))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result
def get_lottery_by_groupid_and_tgid(group_id, creater_id, open = False):
    conn = sqlite3.connect("db/ac.sqlite3")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM lottery WHERE group_id = ? and creater_id = ? and open = ?',(group_id, creater_id, open))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result
def insert_lottery_detail(lottery_sn, lottery_tgid):
    conn = sqlite3.connect("db/ac.sqlite3")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('INSERT INTO lottery_detail VALUES (null,?,?,?)',(lottery_sn, lottery_tgid, False))
    conn.commit()
    cursor.close()
    conn.close()
def get_lottery_detail_by_lottery_sn(lottery_sn):
    conn = sqlite3.connect("db/ac.sqlite3")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM lottery_detail WHERE lottery_sn = ?',(lottery_sn,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result
def get_lottery_detail_by_lottery_sn_and_tgid(lottery_sn, lottery_tgid):
    conn = sqlite3.connect("db/ac.sqlite3")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM lottery_detail WHERE lottery_sn = ? AND lottery_tgid = ?',(lottery_sn, lottery_tgid))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result
def update_lottery_detail_winer(lottery_sn, lottery_tgid):
    conn = sqlite3.connect("db/ac.sqlite3")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('UPDATE lottery_detail SET win = ? WHERE lottery_sn = ? AND lottery_tgid = ?',(True, lottery_sn, lottery_tgid))
    conn.commit()
    cursor.close()
    conn.close()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)
logger = logging.getLogger(__name__)
BOT_TOKEN = os.getenv('BOT_TOKEN')
opens = {
    'cold': {16: 'CAACAgUAAxkBAANlZIXNack-UxzcaQFSPgX3lesuG0MAAo8OAAIqYzFUeKJhiqSXrAsvBA', 17: 'CAACAgUAAxkBAANnZIXNbrQ_9KFD1qSPS9vjaehJb4QAAjsJAAIU9TBU24JLGxRuEiwvBA', 18: 'CAACAgUAAxkBAANpZIXNca2-UgO4VusLZMML1YE438kAAsIIAAIhxzFUcKQLDxPR2fQvBA', 19: 'CAACAgUAAxkBAANrZIXNdIfz-j9k43XOjywIAy8HZdkAAosOAALshTFU7DGMV5xcZYUvBA', 20: 'CAACAgUAAxkBAANtZIXNeD02TdXU0PY1_jDm_b4oh7oAAvEaAAJiUTFUXXtR7MAcoJEvBA', 21: 'CAACAgUAAxkBAANvZIXNepMQMexKkNsQcMKnybJMWVUAAlsLAAICBTFUZFOEweCmHj0vBA', 22: 'CAACAgUAAxkBAANxZIXNfWdFlP2r2CyAXKco8bJlbe4AAtoLAALGnTFUbkMiYs97Kc0vBA', 23: 'CAACAgUAAxkBAANzZIXNgGoMuBa3Kfi9HFLSU3VGFtwAAnAJAAIEgDFUSelnUHo3FU8vBA', 24: 'CAACAgUAAxkBAAN1ZIXNgkezTJfjK6aB5c8WBsW4V3YAAoUJAAJgSClUwXCQ6JbtwPYvBA', 25: 'CAACAgUAAxkBAAN3ZIXNhDH7lT2HlO9dPMVNtHveRKUAAlIJAAPIMVSUXBpcNBhZTy8E', 26: 'CAACAgUAAxkBAAN5ZIXNh31LR5V60HSn4nuaNjv3sg4AAjQKAALLajFUMKSgFqnTBNwvBA', 27: 'CAACAgUAAxkBAAN7ZIXNijhJ70EL1S_v7798auXUUfUAAjkMAAK33TFUI926roJMtmwvBA', 28: 'CAACAgUAAxkBAAN9ZIXNjfYd8kCc0KcDcdAy3iH4dp4AAp8MAAIg7yhUVfuAdXKT3IUvBA', 29: 'CAACAgUAAxkBAAN_ZIXNkKzp4qEjaYJm5YSIFiikqb4AAmELAAJyvzBUSLIfU79b6psvBA', 30: 'CAACAgUAAxkBAAOBZIXNksY0FOCb9dhoFCWEEZqv7ZUAAswJAALeWylUUJ_zz6k5cT0vBA'},
    'hot': {16: 'CAACAgUAAxkBAAODZIXN1a2Jroy7J-SXo1iV4KlU3DIAAkAKAAJ4nTFUUBUwxHPSjr4vBA', 17: 'CAACAgUAAxkBAAOFZIXN2r1XZ75QKrKmMSDo-gQUzAsAAi8JAALxoDFUC-KI0MEtrnEvBA', 18: 'CAACAgUAAxkBAAOHZIXN3mCECsCs8QAB-DaLtgwvkcfsAAK5CgAC4bsxVBmq1BxhTa6uLwQ', 19: 'CAACAgUAAxkBAAOJZIXN4YA1NKvjpvtwZN3-BdMgZhUAAhALAAIGqTBUl1_CxAVmXx8vBA', 20: 'CAACAgUAAxkBAAOLZIXN5Bay2prTM880n1WzwgEvJAIAAvYKAAK6YDBUL6IR_3ZixIEvBA', 21: 'CAACAgUAAxkBAAONZIXN7ewmoghlj6gGUHDabueXOU8AAhQLAAJOiDBUk2xNyToC4TEvBA', 22: 'CAACAgUAAxkBAAOPZIXN8lUYY1yl3nShT4L-9g7z1vQAAlQKAAIrLTBU-3WQdsX15BIvBA', 23: 'CAACAgUAAxkBAAORZIXN9iTmVVTHAAE_L_JAZb714X4sAAK1CgAC1BApVD_vnL7Bc6KHLwQ', 24: 'CAACAgUAAxkBAAOTZIXOAlVMqwP1Vx-N1_VPZeu-CdQAAv8IAALK1TBUikuA3PDKUKMvBA', 25: 'CAACAgUAAxkBAAOVZIXOBy4Yqx3wAv46wswMm1enmYYAAqoJAAJucjFU4iB5BMRr7v4vBA', 26: 'CAACAgUAAxkBAAOXZIXOC-a-STSWpqCSMQcV4gksnB0AAi8MAAKwrClURVA-dK9e87QvBA', 27: 'CAACAgUAAxkBAAOZZIXOEPTfXFIuDWnA-yKo3pCktfIAAl0NAALkgTFUQg8MU9Z-lxMvBA', 28: 'CAACAgUAAxkBAAObZIXOHPJCMTbEXvIDk1mpSUwSTc0AAg0PAAJEATFUW3kvtf1qRt0vBA', 29: 'CAACAgUAAxkBAAOdZIXOIrFMoFlc3GJ3bu8ZnbQJguEAAkYKAAJj8TBUv0yBhPSMsr4vBA', 30: 'CAACAgUAAxkBAAOfZIXOKOnBV8OT1JzNFL7YFz3ZSDcAAmkJAAJIvDFUAAEfR2ka7JmELwQ'}
    }
close = 'CAACAgUAAxkBAAHPBgNkhdCzbwXMf4GeAAEloaSbKOD5peIAAhIMAAIeqjBUWHXNJwdEfQUvBA'
START_LOTTERY, WAIT_LOTTERY_TITLE, WAIT_LOTTERY_MODE, WAIT_LOTTERY_KEYWORD,WAIT_LOTTERY_NUMBER,WAIT_PRIZE_NUMBER, WAIT_LOTTERY_DONE, LOTTERY_CONFIRMED, LOTTERY_CANCELED, LOTTERY_MASTER_OPEN = range(10)
stickers = {}
async def delay_delete_messages_in_jobdata(context):
    for m in context.job.data:
        try:
            await m.delete()
        except:
            pass
async def delete_messages(messages):
    for m in messages:
        try:
            await m.delete()
        except:
            pass
def get_ac_menu_keyboard_markup():
    keyboard = [
        [InlineKeyboardButton("🟢打开", callback_data='open'), InlineKeyboardButton("🔴关闭", callback_data='close'),
         InlineKeyboardButton("❄️制冷", callback_data='cold'),InlineKeyboardButton("☀️制热", callback_data='hot')],
        [InlineKeyboardButton("🔼", callback_data='up'),InlineKeyboardButton("🔽", callback_data='down')],
    ]
    return InlineKeyboardMarkup(keyboard)
def get_lottery_menu_keyboard_markup(update, context):
    keyboard = [
        [InlineKeyboardButton("抽奖设置", callback_data=f'lottery_setting',url=f'https://t.me/{context.bot.username}?start=lottery_settingx{update.effective_message.chat.id}x{update.effective_user.id}')],
    ]
    return InlineKeyboardMarkup(keyboard)
def get_lottery_setting_keyboard_markup(update, context, tmp):
    keyboard =[
        [InlineKeyboardButton("创建抽奖", callback_data=f'lottery_createx{tmp}'),
        InlineKeyboardButton("强制开奖", callback_data=f'lottery_openx{tmp}')],
    ]
    return InlineKeyboardMarkup(keyboard)
async def ac_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    chatid = query.message.chat.id
    ac = get_ac(chatid)
    if query.data == 'close':
        update_ac_open(chatid, False)
        if chatid not in stickers:
            stickers[chatid] = []
        await delete_messages(stickers[chatid])
        res = await context.bot.send_sticker(chat_id=chatid, sticker=close)
        stickers[chatid].append(res)
        await query.message.delete()
    elif query.data == 'open':
        update_ac_open(chatid, True)
    ac = get_ac(chatid)
    if ac['open']:
        if query.data == 'down':
            temp = ac['temp'] - 1
            if temp < 16:
                temp = 16
                await context.bot.answer_callback_query(query.id, text="空调温度已经是最低了", show_alert=True)
            else:
                update_ac_temp(chatid, temp)
        elif query.data == 'up':
            temp = ac['temp'] + 1
            if temp > 30:
                temp = 30
                await context.bot.answer_callback_query(query.id, text="空调温度已经是最高了", show_alert=True)
            else:
                update_ac_temp(chatid, temp)
        elif query.data == 'cold':
            update_ac_mode(chatid, 'cold')
        elif query.data == 'hot':
            update_ac_mode(chatid, 'hot')
    await query.answer()
    ac = get_ac(chatid)
    if ac['open']:
        if chatid not in stickers:
            stickers[chatid] = []
        await delete_messages(stickers[chatid])
        res = await context.bot.send_sticker(chat_id=chatid, sticker=opens[ac['mode']][ac['temp']])
        stickers[chatid].append(res)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = [BotCommand('start','开启娜美的空调！'),BotCommand('acstatus','查看空调状态'),BotCommand('lottery','打开抽奖设置')]
    try:
        await context.bot.set_my_commands(commands=commands, scope=BotCommandScopeChatAdministrators(update.effective_message.chat.id))
    except:
        pass
    if update.effective_message.chat.type == 'private':
        if 'lottery_setting' in update.message.text:
            tmp = 'x'.join(update.message.text.split('x')[1:])
            await context.bot.send_message(chat_id=update.effective_message.chat.id, text='欢迎使用娜美抽奖机器人',
                                                    reply_markup=get_lottery_setting_keyboard_markup(update, context, tmp),parse_mode=ParseMode.MARKDOWN)
            try:
                await context.user_data['lottery_setting_button_message'].delete()
            except:
                pass
    else:
        chatid = update.effective_message.chat.id
        get_ac(chatid)
        await context.bot.send_message(chat_id=update.effective_message.chat.id, text='娜美的空调！',
                                                 reply_markup=get_ac_menu_keyboard_markup(),parse_mode=ParseMode.MARKDOWN)
async def lottery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.effective_message.chat.type
    if chat_type != 'private':
        user_id = update.effective_user.id
        chat_id = update.effective_message.chat.id
        # 获取用户在群组中的角色
        member = await context.bot.get_chat_member(chat_id, user_id)
        role = member.status
        res = await context.bot.send_message(chat_id=update.effective_message.chat.id, text='欢迎使用娜美抽奖机器人！',
                                                reply_markup=get_lottery_menu_keyboard_markup(update, context),parse_mode=ParseMode.MARKDOWN)
        context.user_data['lottery_setting_button_message'] = res
        data = [res]
        context.job_queue.run_once(delay_delete_messages_in_jobdata, 20, data=data, chat_id=chat_id)
        await delete_messages([update.effective_message])
def get_lottery_text(lottery):
    text = f"奖品:{lottery['lottery_title']}\n"
    text += f"满{lottery['lottery_number']}人开奖\n"
    text += f"当前参与人数：{lottery['joined_number']}\n"
    text += f"抽奖关键字:`{lottery['lottery_keyword']}`\n"
    text += f"奖品数量：{lottery['prize_number']}\n"
    return text
async def lottery_messagehandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    groupid = update.effective_message.chat.id
    userid = update.effective_user.id
    lotterys = get_lottery_by_groupid(groupid, False)
    text = update.effective_message.text
    data = []
    if text in ['怎么抽奖','抽奖','lottery']:
        data.append(update.effective_message)
        if len(lotterys) == 0:
            res = await update.effective_message.reply_text('当前群组中没有抽奖!')
            data.append(res)
        else:
            for lottery in lotterys:
                res = await update.effective_message.reply_text(get_lottery_text(lottery), parse_mode=ParseMode.MARKDOWN)
                data.append(res)
    for lottery in lotterys:
        if text == lottery['lottery_keyword']:
            data.append(update.effective_message)
            sn = lottery['lottery_sn']
            joined = get_lottery_detail_by_lottery_sn_and_tgid(sn, userid)
            if joined:
                res = await update.effective_message.reply_text(f"你已经参与了此次抽奖，无法再次参与！\n满{lottery['lottery_number']}人开奖\n当前参与人数：{lottery['joined_number']}", parse_mode=ParseMode.MARKDOWN)
                data.append(res)
            else:
                insert_lottery_detail(sn, userid)
                update_lottery_joined_number(sn, lottery['joined_number']+1)
                lottery = get_lottery_by_lottery_sn(sn)
                res = await update.effective_message.reply_text(f"参与{lottery['lottery_title']}成功！\n满{lottery['lottery_number']}人开奖\n当前参与人数：{lottery['joined_number']}", parse_mode=ParseMode.MARKDOWN)
                data.append(res)
                if lottery['joined_number'] == lottery['lottery_number']:
                    details = get_lottery_detail_by_lottery_sn(sn)
                    winer = random.sample(details, lottery['prize_number'])
                    winertext = f"奖品:{lottery['lottery_title']}开奖啦！\n获奖者：\n"
                    for w in winer:
                        update_lottery_detail_winer(w['lottery_sn'], w['lottery_tgid'])
                        winertext += f"[{w['lottery_tgid']}](tg://user?id={w['lottery_tgid']})\n"
                    winertext += '请抽奖创建者发放奖品！'
                    update_lottery_open(sn, True)
                    await context.bot.send_message(chat_id=groupid, text=winertext,parse_mode=ParseMode.MARKDOWN)
    context.job_queue.run_once(delay_delete_messages_in_jobdata, 20, data=data, chat_id=groupid)
async def acstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message.chat.type != 'private':
        chatid = update.effective_message.chat.id
        ac = get_ac(chatid)
        text = '娜美的空调当前状态：\n'
        if ac['mode'] == 'cold':
            mode = '制冷模式❄️'
        else:
            mode = '制热模式☀️'
        if ac['open']:
            open = f'已开启🟢'
        else:
            open = f'已关闭🔴'
        text += f'当前状态：{open}\n'
        text += f'当前模式：{mode}\n'
        text += f'当前温度：{ac["temp"]}\n'
        await context.bot.send_message(chat_id=update.effective_message.chat.id,text=text,parse_mode=ParseMode.MARKDOWN)
        if ac['open']:
            res = await context.bot.send_sticker(chat_id=chatid, sticker=opens[ac['mode']][ac['temp']])
        else:
            res = await context.bot.send_sticker(chat_id=chatid, sticker=close)
        if chatid not in stickers:
            stickers[chatid] = []
        await delete_messages(stickers[chatid])
        await delete_messages([update.effective_message])
        stickers[chatid].append(res)
# ss = {'hot':{}}
# index = 16
# async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     global ss
#     global index
#     ss['hot'][index] = update.message.sticker.file_id
#     index += 1
#     if index > 30:
#         print(ss)
#     await update.message.reply_sticker(update.message.sticker.file_id)
async def lottery_querycallback(update, context):
    query = update.callback_query
    await query.answer()
    tmp = query.data.split('x')
    if 'lottery_create' in query.data:
        if len(tmp) == 3:
            await delete_messages([update.effective_message])
            group_id = query.data.split('x')[1]
            creater_id = query.data.split('x')[2]
            context.user_data['lottery_sn'] = uuid.uuid4().hex
            context.user_data['group_id'] = group_id
            context.user_data['creater_id'] = creater_id
            context.user_data['state'] = START_LOTTERY
            await context.bot.send_message(chat_id=update.effective_chat.id, text="请输入抽奖标题：")
            return WAIT_LOTTERY_TITLE
    elif 'lottery_open' in query.data:
        if len(tmp) == 3:
            await delete_messages([update.effective_message])
            group_id = query.data.split('x')[1]
            creater_id = query.data.split('x')[2]
            lotterys = get_lottery_by_groupid_and_tgid(group_id, creater_id, False)
            text = ''
            for lottery in lotterys:
                text += f'当前抽奖序列号：`{lottery["lottery_sn"]}`\n'
                text += get_lottery_text(lottery)
            if text == '':
                text = '当前群组没有你创建的抽奖！'
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text,parse_mode=ParseMode.MARKDOWN)
                return ConversationHandler.END
            else:
                text += '请回复需要强制开奖的序列号'
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text,parse_mode=ParseMode.MARKDOWN)
                return LOTTERY_MASTER_OPEN
async def wait_lottery_title_input(update, context):
    # 获取用户输入的文字
    text = update.message.text
    context.user_data['lottery_title'] = text
    context.user_data['state'] = WAIT_LOTTERY_TITLE
    await context.bot.send_message(chat_id=update.effective_chat.id, text="请输入抽奖关键字：")
    return WAIT_LOTTERY_KEYWORD
async def wait_lottery_keyword_input(update, context):
    # 获取用户输入的文字
    text = update.message.text
    context.user_data['lottery_keyword'] = text
    context.user_data['state'] = WAIT_LOTTERY_KEYWORD
    await context.bot.send_message(chat_id=update.effective_chat.id, text="请输入参与人数：")
    return WAIT_LOTTERY_NUMBER
async def wait_lottery_number_input(update, context):
    # 获取用户输入的文字
    text = update.message.text
    context.user_data['lottery_number'] = text
    context.user_data['state'] = WAIT_LOTTERY_NUMBER
    await context.bot.send_message(chat_id=update.effective_chat.id, text="请输入奖品数量：")
    return WAIT_PRIZE_NUMBER
async def wait_prize_number_input(update, context):
    # 获取用户输入的文字
    text = update.message.text
    context.user_data['prize_number'] = text
    context.user_data['state'] = WAIT_PRIZE_NUMBER
    reply_keyboard = [["确认", "取消"]]
    await update.message.reply_text(
        "抽奖已经设置完毕，等待确认",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )
    return WAIT_LOTTERY_DONE
async def wait_lottery_done(update, context):
    # 获取用户输入的文字
    text = update.message.text
    if text == '确认':
        # 将状态设置为 ConversationHandler.END
        context.user_data['state'] = WAIT_LOTTERY_DONE
        # 发送消息到群组中，提示输入已完成
        await update.message.reply_text(
            f"已经完成！",
            reply_markup=ReplyKeyboardRemove(),
        )
        insert_lottery(context.user_data['lottery_sn'], context.user_data['group_id'], context.user_data['creater_id'], context.user_data['lottery_title'], context.user_data['lottery_number'],context.user_data['prize_number'], context.user_data['lottery_keyword'])
        result = get_lottery_by_lottery_sn(context.user_data['lottery_sn'])
        member = await context.bot.get_chat_member(result['group_id'], result['creater_id'])
        name = member.user.first_name
        if member.user.last_name:
            name += ' ' + member.user.last_name
        await context.bot.send_message(chat_id=context.user_data['group_id'], text=f"[{name}](tg://user?id={result['creater_id']})发布了一个{result['lottery_title']}抽奖\n发送抽奖关键词参与抽奖: `{result['lottery_keyword']}`\n满 {result['lottery_number']} 人开奖\n奖品数量: {result['prize_number']}\n", parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END
    else:
        # 将状态设置为 ConversationHandler.END
        context.user_data['state'] = WAIT_LOTTERY_DONE
        # 发送消息到群组中，提示输入已完成
        await update.message.reply_text(
            f"已经取消！",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END
async def cancel_lottery(update, context):
    await update.message.reply_text(
        "已经取消！",
    )
    return ConversationHandler.END
async def wait_lottery_master_open(update, context):
    # 获取用户输入的文字
    sn = update.message.text
    lottery = get_lottery_by_lottery_sn(sn)
    if lottery:
        details = get_lottery_detail_by_lottery_sn(sn)
        if details:
            winer = random.sample(details, lottery['prize_number'])
            winertext = f"奖品:{lottery['lottery_title']}开奖啦！\n获奖者：\n"
            for w in winer:
                update_lottery_detail_winer(w['lottery_sn'], w['lottery_tgid'])
                winertext += f"[{w['lottery_tgid']}](tg://user?id={w['lottery_tgid']})\n"
            winertext += '请抽奖创建者发放奖品！'
            update_lottery_open(sn, True)
            await context.bot.send_message(chat_id=lottery['group_id'], text=winertext,parse_mode=ParseMode.MARKDOWN)
        else:
            winertext = f"奖品:{lottery['lottery_title']}开奖啦！\n无人中奖！\n"
            update_lottery_open(sn, True)
            await context.bot.send_message(chat_id=lottery['group_id'], text=winertext,parse_mode=ParseMode.MARKDOWN)
    return ConversationHandler.END
if __name__ == '__main__':
    if BOT_TOKEN:
        application = ApplicationBuilder().connect_timeout(30).read_timeout(30).write_timeout(30).token(BOT_TOKEN).build()

        start_handler = CommandHandler(['start','help'], start)
        application.add_handler(start_handler)
        application.add_handler(CommandHandler('acstatus', acstatus))
        application.add_handler(CommandHandler('lottery', lottery))
        # application.add_handler(MessageHandler(filters.Sticker.ALL, test))
        def is_lottery(callback_data):
            if 'lottery' in callback_data:
                return True
            else:
                return False
        def is_ac(callback_data):
            if 'lottery' in callback_data:
                return False
            else:
                return True
        conv_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(lottery_querycallback, pattern=is_lottery)],
            states={
                WAIT_LOTTERY_TITLE: [MessageHandler(filters.TEXT, wait_lottery_title_input)],
                WAIT_LOTTERY_KEYWORD: [MessageHandler(filters.TEXT, wait_lottery_keyword_input)],
                WAIT_LOTTERY_NUMBER: [MessageHandler(filters.TEXT, wait_lottery_number_input)],
                WAIT_PRIZE_NUMBER: [MessageHandler(filters.TEXT, wait_prize_number_input)],
                WAIT_LOTTERY_DONE: [MessageHandler(filters.TEXT, wait_lottery_done)],
                LOTTERY_MASTER_OPEN: [MessageHandler(filters.TEXT, wait_lottery_master_open)],
            },
            fallbacks=[CommandHandler('cancel', cancel_lottery)],
        )
        application.add_handler(conv_handler)
        application.add_handler(CallbackQueryHandler(ac_menu, pattern=is_ac))
        application.add_handler(MessageHandler(filters.TEXT, lottery_messagehandler))
        application.run_polling()
    else:
        print(f'env variables not found! \n BOT_TOKEN: {BOT_TOKEN}')
