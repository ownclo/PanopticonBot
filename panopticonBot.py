#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler
import logging
import re

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PREFIX_LIST = ["PANSERV", "PAN", "DUTY", "DONG"]
PREFIX_PATTERN = "|".join(PREFIX_LIST)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Hi!')


def help(bot, update):
    update.message.reply_text('Help!')


def hyperlinky(msg):
    return "http://jira.mara.local/browse/" + msg


def hyperlinize(bot, update):
    text = update.message.text
    tasks = findTasks(text, PREFIX_PATTERN)
    taskUrls = [hyperlinky(task) for task in tasks]
    if len(taskUrls) > 0:
        reply = "\n".join(taskUrls)
        update.message.reply_text(reply)

# => findTasks("sdlgkfdjg PAN-1234 fsfgPAN-4321 https://s/PAN-678", ["PAN"])
# ["PAN-1234"]
def findTasks(string, prefixPattern):
    fs = re.findall("(?![\/])(?:^|\W)((" + prefixPattern + ")-\d+)", string)
    return [f[0] for f in fs]

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("230320568:AAHRYmQ4CP2ZK49KfZOdxqHRrmjvJF1r3mA")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, hyperlinize))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
