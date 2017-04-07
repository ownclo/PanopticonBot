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

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, Job
import logging
import re

from jira import JIRA

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

JIRA_URL = "http://jira.mara.local/"
PREFIX_LIST = ["PANSERV", "PAN", "DUTY", "DONG"]
PREFIX_PATTERN = "|".join(PREFIX_LIST)

J = JIRA(JIRA_URL)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Hi!')


def help(bot, update):
    update.message.reply_text('''
        /unblocked username -- all not closed user tasks with all closed blockers
    ''')

def unblocked(bot, update):
    user = update.message.text.split(' ')[1]
    reply = 'Unblocked Tasks: \n' + findUnblockedTasks(user)
    update.message.reply_text(reply)

def hyperlinky(msg):
    return "http://jira.mara.local/browse/" + msg

def describe(taskName):
    url = hyperlinky(taskName)
    error = None
    try:
        issue = J.issue(taskName).fields
        name = issue.summary
        assignee = issue.assignee.displayName
        status = issue.status.name
        return pprint([('url', url), ('name', name), ('assignee', assignee), ('status', status)])
    except Exception as e:
        print e
        error = e
        return pprint([('url', url), ('error', error)])


def findUnblockedTasks(userName):
    issues = J.search_issues('assignee = ' + userName + ' AND status != Closed AND status != Resolved ORDER BY updated DESC')
    unblockedTasks = ''
    for issue in issues:
        isUnblocked = True
        containsBlocker = False
        for link in issue.fields.issuelinks:
            # 10000 -> Blocked
            if link.type.id == '10000':
                try:
                    blocker = link.inwardIssue
                    # 6 -> Closed
                    if blocker.fields.status.id != '6':
                        isUnblocked = False
                    containsBlocker = True
                except:
                    pass
        if isUnblocked == True and containsBlocker == True:
            unblockedTasks =  unblockedTasks + describe(issue.key)
    if unblockedTasks == '':
        return 'None'
    return unblockedTasks


def pprint(tuples):
    res = ""
    for (k, v) in tuples:
        res += k.encode('utf-8') + ": " + v.encode('utf-8') + "\n"
    return res


def hyperlinize(bot, update):
    text = update.message.text
    tasks = findTasks(text, PREFIX_PATTERN)
    taskDesc = [describe(task) for task in tasks]
    if len(taskDesc) > 0:
        reply = "\n".join(taskDesc)
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
    dp.add_handler(CommandHandler("unblocked", unblocked))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, hyperlinize))

    # log all errors
    dp.add_error_handler(error)

    job_minute = Job(callback_minute, 10.0)
    updater.job_queue.put(job_minute)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

def callback_minute(bot, job):
    import requests
    link = "http://bettingservice.knk.local:8080/bettingservice/health"
    f = requests.get(link)
    json = f.text
    if "WARNING" in json or "ERROR" in json:
        bot.sendMessage(chat_id='@panopticon_warn', text='Health status is not OK: \n' + json)

if __name__ == '__main__':
    main()
