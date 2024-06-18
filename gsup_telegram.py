#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
gsup_telegram.py - GeigerLog support for Telegram Messenger

!!!  MUST restrict pip module to: python-telegram-bot==13.15 !!!

include in programs with:
    include gsup_telegram
"""

###############################################################################
#    This file is part of GeigerLog.
#
#    GeigerLog is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GeigerLog is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GeigerLog.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

# NOTES:
# calling when in Telegram 'IDBot' as ullix with '/getid'
# Reply:  Your own ID is: 123456789  is equal to chat ID
# g.TelegramBot: {'id': 2008102243, 'username': 'Geiger_Bot', 'first_name': 'GeigerLog Bot'}


from gsup_utils   import *

try:
    # raise Exception("Testing import of telegram")
    import telegram
    from telegram       import Update
    from telegram.ext   import CallbackContext, MessageHandler, Filters, CommandHandler, Updater
    # rdprint("telegram installed in version: ", telegram.__version__)

    import urllib3

    # try:    from telegram import __version__        as telegram_version
    # except: telegram_version = None

    # from telegram import __version__        as telegram_version

    g.versions["telegram"]             = telegram.__version__
    g.versions["urllib3"]              = urllib3.__version__

except Exception as e:
    playSndClip("err")
    msg  = "Python module 'telegram' was not found.\n\n"
    msg += "This module is required to communicate with the Telegram Messenger.\n\n"
    msg += "Verify that 'python-telegram-bot' is installed using GeigerLog tool: 'PipCheck.sh' or 'PipCheck.bat'.\n\n"
    msg += "GeigerLog will continue, but Telegram cannot be used."
    exceptPrint(e, msg)
    g.importProblem = msg



def initTelegram(force=False):              # Force=True: bypass dialogue
    """Setup Telegram messenger (if needed) and configure its GeigerLog properties"""

    defname = "initTelegram: "
    dprint(defname)
    setIndent(1)

    # g.TelegramChatID = 175598162            # is it always correct???? is now loaded from private file
    title  = "Telegram Messenger"

    if g.TelegramBot is None:
        # initial activation

        try:
            g.TelegramBot = telegram.Bot(token=g.TelegramToken)

            dprint(defname, "g.TelegramBot: ", g.TelegramBot)
            dprint(defname, "get_me():      ", g.TelegramBot.get_me())

            # updates = g.TelegramBot.get_updates()
            # rdprint(defname, "type(updates): ", type(updates), ", len(updates): ", len(updates))
            # if len(updates) > 0:  g.TelegramChatID = updates[0].message.from_user.id
            # rdprint(defname, "g.TelegramChatID: ", g.TelegramChatID)

            updater    = Updater(token=g.TelegramToken, use_context=True)
            dispatcher = updater.dispatcher


            def start(update: Update, context: CallbackContext):
                """setting command '/start' of Geiger_Bot"""

                defname = "start: "
                g.TelegramChatID = update.effective_chat.id

                text = "I'm your bot, how may I help you?"
                context.bot.send_message(chat_id=g.TelegramChatID, text=text)

                rdprint(defname, "ChatID: ", g.TelegramChatID, "  CMD: '/start' text: ", text)


            def data(update: Update, context: CallbackContext):
                """setting command '/data' of Geiger_Bot"""

                defname = "data: "
                g.TelegramChatID = update.effective_chat.id

                rawtext = getData4Telegram()
                text = "<pre>" + rawtext + "</pre>"
                context.bot.send_message(chat_id=g.TelegramChatID, text=text, parse_mode = "HTML")
                rdprint(defname, "ChatID: ", g.TelegramChatID, "  CMD: '/data' sending data: {}".format(rawtext[:rawtext.find("\n")]))


            def graph(update: Update, context: CallbackContext):
                """setting command '/graph' of Geiger_Bot"""

                defname  = "graph: "
                g.TelegramChatID = update.effective_chat.id

                rdprint(defname, "ChatID: ", g.TelegramChatID, "  CMD: '/graph' requesting graph")

                g.TelegramNeedsPic = True


            def x(update: Update, context: CallbackContext):
                """setting command '/x' of Geiger_Bot"""

                defname  = "x: "

                rdprint(defname, "CMD: '/x' sending data & graph")
                if g.logging:
                    graph(update, context)
                    # data (update, context)
                else:
                    success  = sendTextToMessenger(text="To see Log graph and data you must be logging", parse_mode = "HTML")


            def echo(update: Update, context: CallbackContext):
                """setting command '/echo' of Geiger_Bot"""

                defname = "echo: "
                g.TelegramChatID = update.effective_chat.id

                rdprint(defname, "ChatID: ", g.TelegramChatID, "  CMD: '/echo' : ", update.message.text)

                context.bot.send_message(chat_id=g.TelegramChatID, text="You entered: " + update.message.text)


            start_handler = CommandHandler('start', start)
            dispatcher.add_handler(start_handler)

            data_handler  = CommandHandler('data', data)
            dispatcher.add_handler(data_handler)

            graph_handler = CommandHandler('graph', graph)
            dispatcher.add_handler(graph_handler)

            x_handler = CommandHandler('x', x)
            dispatcher.add_handler(x_handler)

            echo_handler  = MessageHandler(Filters.text & (~Filters.command), echo)
            dispatcher.add_handler(echo_handler)

            updater.start_polling()

        except Exception as e:
            exceptPrint(e, "FAILURE activating telegram Bot")

    sendTextToMessenger("I'm your bot, how may I help you?")

    if not force: setTelegramProperties(title)

    setIndent(0)


def setTelegramProperties(title):
    """Calls the dialog to set activation and cycle time and print to NotePad"""

    defname = "setTelegramProperties: "
    setIndent(1)

    retval = getTelegramProperties()
    if retval == 0:
        dprint(defname + "Cancelled, Properties unchanged")
    else:
        newMsg = "My new settings: Activation: {}  UpdateCycle: {} sec.".format(g.TelegramActivation, g.TelegramUpdateCycle)
        dprint(defname, newMsg)
        fprint(header(title))
        fprint("Activation:",   "{}"    .format("Yes" if g.TelegramActivation else "No"))
        fprint("Update Cycle:", "{} sec".format(g.TelegramUpdateCycle))

        try:
            g.TelegramBot.send_message(chat_id=g.TelegramChatID, text=newMsg + "\n\nUpdates will be seen when activated and logging.")
        except Exception as e:
            exceptPrint(e, "Telegram Send Msg - Flood Control?")

        g.TelegramLastUpdate = 0 # reset so it will be updated on next log

    setIndent(0)


def getTelegramProperties():
    """Set activation and cycle time"""

    defname = "getTelegramProperties: "

    lmean = QLabel("Activate Updates")
    lmean.setAlignment(Qt.AlignLeft)
    lmean.setMinimumWidth(200)

    r01=QRadioButton("Yes")
    r02=QRadioButton("No")
    r01.setChecked(False)
    r02.setChecked(False)
    r01.setToolTip("Activate 'Yes' to send Updates to Telegram in regular intervals")
    r02.setToolTip("Activate 'No' to never send Updates to Telegram")
    powergroup = QButtonGroup()
    powergroup.addButton(r01)
    powergroup.addButton(r02)
    hbox0=QHBoxLayout()
    hbox0.addWidget(r01)
    hbox0.addWidget(r02)
    hbox0.addStretch()
    if g.TelegramActivation:   r01.setChecked(True)
    else:                      r02.setChecked(True)

    lctime = QLabel("Update Cycle Time [sec]\n(at least 1 sec)")
    lctime.setAlignment(Qt.AlignLeft)
    ctime  = QLineEdit()
    ctime.setToolTip('Enter X to update Telegram every X seconds')
    ctime.setText("{:0.5g}".format(g.TelegramUpdateCycle))

    graphOptions=QGridLayout()
    graphOptions.addWidget(lmean,          0, 0)
    graphOptions.addLayout(hbox0,          0, 1)
    graphOptions.addWidget(lctime,         1, 0)
    graphOptions.addWidget(ctime,          1, 1)
    graphOptions.addWidget(QLabel(""),     2, 0)

    d = QDialog() # set parent to None to popup in center of screen
    d.setWindowIcon(g.iconGeigerLog)
    d.setFont(g.fontstd)
    d.setWindowTitle("Telegram Messenger Properties")
    d.setWindowModality(Qt.NonModal)
    d.setMinimumWidth(300)

    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
    bbox.accepted.connect(lambda: d.done(100))
    bbox.rejected.connect(lambda: d.done(0))

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(graphOptions)
    layoutV.addWidget(bbox)

    retval = d.exec()
    #print("reval:", retval)

    if retval > 0:
        # Activation
        if r01.isChecked():
            g.TelegramActivation = True
            g.exgg.TelegramAction.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_Telegram.png'))))
        else:
            g.TelegramActivation = False
            g.exgg.TelegramAction.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_Telegram_inactive.png'))))

        # Update Cycle Time
        uctime = ctime.text().replace(",", ".")  #replace any comma with dot
        try:    dt  = max(round(abs(float(uctime)), 2), 1)
        except: dt  = g.TelegramUpdateCycle
        g.TelegramUpdateCycle = dt

    return retval


def getData4Telegram():
    """assemble the data from Last recorded values"""

    defname = "getData4Telegram: "

    if g.logTime is None: return "No data"

    strdata   = ""
    strdata  += "   {:16s}: #{}\n"  .format("Record", g.TelegramData[0])
    strdata  += "   {}:\n"          .format("Values in Record")

    try:
        myformat = "   {:16s}: {:0.3f}\n"
        for i, vname in enumerate(g.VarsCopy):
            if g.varsSetForLog[vname]:
                strdata += myformat.format(vname, g.TelegramData[1][i])

    except Exception as e:
        playSndClip("err")
        msg  = defname + "No proper data available.\n\n"
        exceptPrint(e, msg)
        strdata += msg

    return strdata


def sendTextToMessenger(text, parse_mode = "HTML"):
    """Sends a text message to Telegram"""

    defname  = "sendTextToMessenger: "
    response = None

    try:
        response = g.TelegramBot.send_message(chat_id=g.TelegramChatID, text=text, parse_mode = parse_mode)
    except Exception as e:
        exceptPrint(e, "Telegram Send Text Msg '{}' failed".format(text))

    return True # testing


def sendDataToMessenger(type=0):
    """send data update to telegram"""

    defname  = "sendDataToMessenger: "
    response = None

    try:
        text     = "<pre>" + getData4Telegram() + "</pre>"
        response = g.TelegramBot.send_message(chat_id=g.TelegramChatID, text=text, parse_mode = "HTML")
    except Exception as e:
        exceptPrint(e, "Telegram Send Data  '{}' failed".format(text))

    return True # testing


def sendGraphToMessenger(type=0):
    """send graph update to telegram"""

    # strange: memsave is slower than filesave !!!

    defname  = "sendGraphToMessenger: "
    response = None

    try:
        tpic     = g.TelegramPicBytes.getvalue()
        caption  = None     # "GeigerLog Main Graph"
        response = g.TelegramBot.send_photo(chat_id=g.TelegramChatID, photo=tpic, caption=caption)   # dur: 100 ... 500 ms
        g.TelegramPicBytes.close()
    except Exception as e:
        exceptPrint(e, "Telegram Send Graph failed")

    return True # testing



########################################################################################################
# code from geigerlog.cfg
#
#
# [Telegram]
# # to use the Telegram Messenger to receive and request data from
# # GeigerLog.

# # Telegram ACTIVATION
# # to use (yes) or not use (no) Telegram
# #
# # Options:           yes | no
# # Default          = no
# TelegramActivation = no

# # Telegram Token
# # The token required to use Telegram. See the GeigerLog manual
# # for how to obtain such a token. It will look similar to this:
# #       2018112141:AAHGvfZ1l12345asdfghtljemsgog73kslQ
# #
# # Options:      <the token obtained by Telegram after registering>
# # Default:    = <empty>
# TelegramToken =


# # Telegram UpdateCycle
# # a default message will be send to Telegram after UpdateCycle seconds
# # have passed.
# #
# # Option auto defaults to 3600 (sec)
# #
# # Options:            auto | <any number >1 >
# # Default:          = auto
# TelegramUpdateCycle = auto

# # Telegram ChatID
# # A ChatID is provided by the Telegram IDBot (see GeigerLog manual).
# # Alternatively, it becomes available to GeigerLog after the uses send
# # a command on the GeigerLog Bot
# #
# # Options:       <the ChatID provided by Telegram>
# # Default:       <empty>
# TelegramChatID =

