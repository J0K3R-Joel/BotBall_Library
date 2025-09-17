#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-07-28

try:
    import socket
    import threading
    import json
    import time
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)


class RobotCommunicator:
    def __init__(self, ip, port, is_server=False, pause_event=None):
        self.ip = ip
        self.port = port
        self.is_server = is_server

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = None
        self.connected = False

        self.all_messages = []
        self.message_queue = []
        self.latest_message = None
        self.new_message_flag = False

        self.position_history = []

        self.high_priority_callback = None
        self.high_priority_args = ()
        self.high_priority_kwargs = {}

        self.new_main_callback = None
        self.new_main_args = ()
        self.new_main_kwargs = {}

        self.pause_event = pause_event

        self.__start_connection()

    # ======================== SET INSTANCES ========================

    def set_pause_event_instance(self, p_event: threading.Event) -> None:
        '''
        create or overwrite the existance of the pause event

        Args:
            p_event (threading.Event): the instance of the pause event

       Returns:
            None
        '''
        self.pause_event = p_event

    # ======================== CHECK INSTANCES ========================

    def check_pause_event_instance(self) -> bool:
        '''
        inspect the existance of the pause event

        Args:
            None

       Returns:
            if there is an instance of the pause event in existance
        '''
        if not isinstance(self.pause_event, threading.Event):
            log('pause_event is not defined!', in_exception=True)
            raise Exception('pause_event is not defined!')
        return True

    # ======================== PRIVATE METHODS ========================

    def __start_connection(self) -> None:
        '''
        starting the connection with the server or client, depends on which was set when initializing this class

        Args:
            None

       Returns:
            None, but connects with the other roboter
        '''
        # Disconnect if already connected
        if self.conn or self.connected:
            log("Existing connection detected. Disconnecting first...")
            self.disconnect()

        if self.is_server:
            self.sock.bind((self.ip, self.port))
            self.sock.listen(1)
            log("Waiting for connection ...")
            self.conn, _ = self.sock.accept()
            self.connected = True
        else:
            log("Trying to connect ...")
            while not self.connected:
                try:
                    self.sock.connect((self.ip, self.port))
                    self.conn = self.sock
                    self.connected = True
                except:
                    time.sleep(1)

        log("Connected!")
        threading.Thread(target=self.__receive_loop, daemon=True).start()

    def __receive_loop(self) -> None:
        '''
        loop after connecting to be able to receive all the messages

        Args:
            None

       Returns:
            None
        '''
        while self.connected:
            try:
                if not self.conn:
                    break

                data = self.conn.recv(1024).decode()
                if not data:
                    log("Connection closed by peer.")
                    self.disconnect()
                    break

                msg_obj = json.loads(data)
                msg = msg_obj.get("message", "")
                priority = msg_obj.get("priority", "normal")

                self.latest_message = msg
                self.new_message_flag = True
                self.all_messages.append(msg)
                self.message_queue.append((msg, priority))

                if priority == "pos":
                    self.position_history.append(msg[4:])
                elif priority == "high" and self.high_priority_callback:
                    self.__handle_high_priority(msg)
                elif priority == "new_main" and self.new_main_callback:
                    self.__handle_new_main(msg)

            except Exception as e:
                log(str(e), important=True, in_exception=True)
                self.disconnect()
                break

    def __handle_high_priority(self, msg: str) -> None:
        '''
        Function to handle high priority messages.
        Only passes exactly what the user registered via on_high_priority().
        '''
        self.check_pause_event_instance()
        if self.pause_event:
            self.pause_event.clear()

        if self.high_priority_callback:
            try:
                # msg einfach anzeigen
                log(f"[HIGH PRIORITY] {msg}", important=True)

                # Callback mit exakt den registrierten Args/Kwargs ausführen
                self.high_priority_callback(
                    *self.high_priority_args,
                    **self.high_priority_kwargs
                )

            except Exception as e:
                log(f'Exception in high_priority_callback: {str(e)}',
                    important=True, in_exception=True)

        if self.pause_event:
            self.pause_event.set()

    def __handle_new_main(self, msg: str) -> None:
        '''
        == EXPERIMENTAL == (not yet tested)
        Function to determine what should happen if there was a new_main priority message.
        Will stop the main() thread and start a new one instead.

        Args:
            msg (str): the message sent from the sender

        Returns:
            None
        '''
        log("new main will be executed...")
        if self.new_main_callback:
            try:
                log(f"[NEW MAIN] {msg}", important=True)

                self.new_main_callback(
                    *self.new_main_args,
                    **self.new_main_kwargs
                )

            except Exception as e:
                log(f'Exception in new_main_callback: {str(e)}',
                    important=True, in_exception=True)

        log("new main has finished. Exiting thread...")
        os._exit(0)

    # ======================== PUBLIC METHODS ========================

    def send(self, message, priority="normal") -> None:
        '''
        function to pass a message to the receiver

        Args:
            message: the message sent from the sender that the receiver should get
            priority (str): the importance / background of the message.
                            Options:
                                "normal"   -> (default), just sending a message in the background
                                "high"     -> will pause the main() and lets you execute a function before the main() resumes
                                "new_main" -> == EXPERIMENTAL == (not yet tested) will forget what happens after the current main() and another function / new main will be executed until the end of the program / function / new main

       Returns:
            None
        '''
        try:
            if not self.connected or not self.conn:
                log("Cannot send: not connected.", important=True)
                return
            payload = json.dumps({"message": message, "priority": priority})
            self.conn.send(payload.encode())
        except Exception as e:
            log(str(e), important=True, in_exception=True)
            self.disconnect()

    def has_new_message(self) -> bool:
        '''
        check if theres a message that wasn't read yet

        Args:
            None

       Returns:
            if there is a message that is not read yet (True), or if every received message was read
        '''
        return self.new_message_flag

    def get_latest(self) -> str:
        '''
        Returns the last sent message

        Args:
            None

       Returns:
            The latest message that was sent by (other) the sender
        '''
        self.new_message_flag = False
        return self.latest_message

    def remove_message(self, msg) -> None:
        '''
        deletes a message from the message queue

        Args:
            msg (str): the message from the (other) sender that has to be removed from the history of messages

       Returns:
            None
        '''
        self.message_queue = [m for m in self.message_queue if m[0] != msg]

    def get_safed_messages(self) -> list:
        '''
        lets you see all messages that the (other) sender sent until now, except the deleted ones.

        Args:
            None

       Returns:
            List of all messages ever sent from the (other) sender
        '''
        return self.message_queue

    def get_all_messages(self) -> list:
        '''
        lets you see all messages that the (other) sender sent until now. (Even the deleted ones will show up here)

        Args:
            None

       Returns:
            List of all messages ever sent from the (other) sender
        '''
        return self.all_messages

    def on_high_priority(self, callback, *args, **kwargs) -> None:
        '''
        Register a function to be called on high-priority messages

        Args:
            callback: function name of the function that has to be executed

       Returns:
            None
        '''
        self.high_priority_callback = callback
        self.high_priority_args = args
        self.high_priority_kwargs = kwargs

    def on_new_main(self, callback, *args, **kwargs) -> None:
        '''
        == EXPERIMENTAL == (not yet tested)
        Register a function to be called on high-priority messages

        Args:
            callback: function name of the function that has to be executed

       	Returns:
            None
        '''
        self.new_main_callback = callback
        self.new_main_args = args
        self.new_main_kwargs = kwargs

    def get_positions(self) -> list:
        '''
        lets you see all the position priority messages

        Args:
            None

       Returns:
            List of all the positions that were sent from the (other) sender
        '''
        return self.position_history

    def get_position_len(self) -> int:
        '''
        returns how many positions were sent from the (other) sender until now

        Args:
            None

       Returns:
            The amount a position priority message was sent by the (other) sender
        '''
        return len(self.position_history)

    def get_position_at(self, i) -> str:
        '''
        lets you see the message of a position priority message at a certain point

        Args:
            i (int): the element from all positions in the position history that you want to access

       Returns:
            the chosen element on the chosen place
        '''
        if 0 <= i < len(self.position_history):
            return self.position_history[i]
        log(f'position history has a length of {len(self.position_history)} and you try to access the {str(i)} element of it -> NOT VALID!')
        return None

    def is_connected(self) -> bool:
        '''
        tells you, if it is connected with another robot.

        Args:
            None

        Returns:
            If it is currently connected (True), or not (False)
        '''
        return self.connected


    def disconnect(self) -> None:
        '''
        will kill the communication with the other device

        Args:
            None

       Returns:
            None
        '''
        try:
            self.connected = False
            if self.conn:
                try:
                    self.conn.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                self.conn.close()
                self.conn = None
            if self.sock:
                self.sock.close()
                self.sock = None
            log('Disconnected successfully.')
        except Exception as e:
            log(f'Error during disconnect: {str(e)}', important=True, in_exception=True)