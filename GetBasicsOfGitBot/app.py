import logging
from time import sleep
from credentials import BOT_TOKEN
from questions import Questions
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

global letgoButton

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global letgoButton
    username = update.effective_user.name
    letgo = InlineKeyboardButton("Start 🚀", callback_data="send_message")
    letgoButton = InlineKeyboardMarkup([[letgo]])

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    sleep(1)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Hi *{username}* 👋, \nI'm **@GetBasicsOfGitBot**.\nI'll help you revise what you've learned on Gi& GitHub based on my writing.",
        parse_mode="Markdown"
    )

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    sleep(1)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"I'll ask you a question, and you'll need to find the solution to get the next question. \n\n*Example:*\n*Question:* How to display the version history for the current branch in Git?\n*Expected Answer:* _git log_",
        reply_markup=letgoButton,
        parse_mode="Markdown"
    )

# c_q_id === current_question_id
c_q_id = 0
score = 0

async def askQuestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global c_q_id, Questions
    question = f"*Question : * {Questions[c_q_id][0]}"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"*{question}*",
        parse_mode="Markdown"
    )

async def getResponse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global c_q_id, score, Questions, letgoButton

    if update.message is not None and update.message.text is not None:
        answer = update.message.text.lower()
        correct_answer = Questions[c_q_id][1].lower()
        c_q_id = (c_q_id + 1) % len(Questions)

        if correct_answer == answer and c_q_id == len(Questions) - 1:
            score = score + 1
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Final score : *{score}/{len(Questions)}*.\nYou can try again ;)",
                reply_markup=letgoButton,
                parse_mode="Markdown"
            )

            c_q_id = 0
            score = 0

            return


        elif correct_answer == answer and c_q_id < len(Questions) - 1:
            score = score + 1
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Score : *{score}/{len(Questions)}*",
                parse_mode="Markdown"
            )

            sleep(1)
            await askQuestion(update=update, context=context)

        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"🚨 The correct answer is : *{correct_answer}*.\nScore : *{score}/{len(Questions)}*",
                parse_mode="Markdown"
            )

            sleep(1)
            await askQuestion(update=update, context=context)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"An issue occurred while processing your request 🚨"
        )

async def letgoButtonOpenFAQ(update: Update, context: ContextTypes.DEFAULT_TYPE):
    getQuery = update.callback_query

    if getQuery.data == "send_message":
       await askQuestion(update=update, context=context)

if __name__ == "__main__":
    gitbot = ApplicationBuilder().token(BOT_TOKEN).build()

    startHandler = CommandHandler("start", start)
    letgoHandler = CallbackQueryHandler(letgoButtonOpenFAQ)
    getResponseHandler = MessageHandler(filters.TEXT & (~filters.COMMAND), getResponse)

    gitbot.add_handler(startHandler)
    gitbot.add_handler(letgoHandler)
    gitbot.add_handler(getResponseHandler)

    gitbot.run_polling()
