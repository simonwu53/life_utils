import sys
sys.path.insert(0, '/Users/simonwu/PycharmProjects/life_utils/EMTA')
import check_room

import telepot
from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open
import time
import logging
logging.basicConfig(filename='./logs/LOG.log', filemode='w', format='%(asctime)s - %(levelname)s:  %(message)s', level=logging.DEBUG)


class TG_Bot_Server():
    def __init__(self, token):
        self.__bot = bot = telepot.DelegatorBot(TOKEN,
                                                [pave_event_space()
                                                 (per_chat_id(), create_open, MessageHandler, timeout=60)])
        MessageLoop(self.__bot).run_as_thread()
        logging.debug('Bot server has been started.')
        return

    def stop_listening(self):
        return


class MessageHandler(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)
        self._count = 0
        self.spy_started = False

    def on_chat_message(self, msg):
        self._count += 1

        content_type, chat_type, chat_id = telepot.glance(msg)
        logging.debug('Received msg-> content_type: %s, chat_type: %s, chat_id: %d' %
                      (content_type, chat_type, chat_id))

        # if received a text message
        if content_type == 'text':
            # if start spy command received
            if msg['text'] == '/startspy':
                logging.debug('Received a request to start spy. from: %s' % msg['username'])

                self.spy_started = True
                self.sender.sendMessage('OK, please tell me your name. (the name displayed on the website)')
                return
            # get the name to start spy
            if self.spy_started == True:
                name, status = self.check_name(msg['text'])
                if status == 1:
                    logging.debug('Spy run! name: %s, username: %s' % (name, msg['username']))
                    check_room.run_spy(name, debug=False)
                    logging.debug('Spy finished task.')
                    self.spy_started = False
                elif status == -1:
                    logging.debug('Name err: bad format.')
                    self.sender.sendMessage('Format should be: First Last!')
                elif status == 0:
                    logging.debug('Name err: bad format.')
                    self.sender.sendMessage('Last name only use first character!')
                return

            self.sender.sendMessage('Thanks for message. I will improve later!')

    def check_name(self, name):
        first_last = name.split(' ')
        if len(first_last) == 2:
            first = first_last[0]
            last = first_last[1]
            if len(last) == 1:
                return name.upper(), 1
            else:
                return '', 0
        else:
            return '', -1

    def get_name_timer(self, t=30):
        time.sleep(t)
        self.sender.sendMessage('Request name timeout!')
        self.spy_started = False
        return


if __name__ == '__main__':
    TOKEN = sys.argv[1]  # get token from command-line
    bot = TG_Bot_Server(TOKEN)
    try:
        while 1:
            time.sleep(10)
    except KeyboardInterrupt as e:
        print('bye:)')
        del bot