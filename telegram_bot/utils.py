import json
from django.db import transaction
from .models import Driver, ExitReason
from .credentials import BOT_TOKEN
import requests
import re

class BotService:
    def __init__(self, update):
        self.update = update
        self.message = update.get('message', {})
        self.callback_query = update.get('callback_query', {})
        self.chat = self.message.get('chat', {})
        self.chat_type = self.chat.get('type', '')
        self.chat_id = str(self.chat.get('id', ''))
        self.user_id = self.get_user_id()
        self.message_id = self.get_message_id()
        self.user_input = self.message.get('text', '').strip()

    def get_user_id(self):
        if self.callback_query:
            return self.callback_query.get('from', {}).get('id')
        return self.message.get('from', {}).get('id')

    def get_message_id(self):
        if self.callback_query:
            return self.callback_query.get('message', {}).get('message_id')
        return self.message.get('message_id')


    def make_telegram_request(self, method, payload):
        token = BOT_TOKEN
        url = f"https://api.telegram.org/bot{token}/{method}"
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return None

    def delete_message(self, chat_id, message_id):
        payload = {
            'chat_id': chat_id,
            'message_id': message_id
        }
        res = self.make_telegram_request('deleteMessage', payload)
        print(payload)
        return res


    def send_message(self, chat_id, text, parse_mode='Markdown', reply_markup=None, remove_keyboard=False):
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        if reply_markup:
            payload['reply_markup'] = reply_markup

        return self.make_telegram_request('sendMessage', payload)
        
    def process_telegram_update(self):  
        if 'callback_query' in self.update:
            return self.process_callback_query()
        elif 'message' in self.update and self.user_input:
            if self.user_input.lower().startswith('/register '):
                return self.register_driver()
            elif self.user_input.lower().startswith('/quit '):
                return self.quit_driver()
            elif self.user_input.lower().startswith('/search '):
                return self.search_drivers()
            else:
                self.send_greeting()

    def register_driver(self):
        driver_name = self.user_input[len('/register '):].strip()
        if not driver_name:
            return False, "Please provide a name after '/register'."
        _, created = Driver.objects.get_or_create(name=driver_name)
        if created:
            return True, f"Driver {driver_name} registered successfully."
        else:
            return False, "Driver already registered."

    def quit_driver(self):
        driver_name = self.user_input[len('/quit '):].strip()
        driver = Driver.objects.filter(name=driver_name).first()
        if not driver:
            return False, f"Driver {driver_name} not found."
        driver.delete()
        return True, f"Driver {driver_name} quit successfully."

    def search_drivers(self):
        search_query = self.user_input[len('/search '):].strip()
        if not search_query:
            return False, "Please provide a search query after '/search'."
        matching_drivers = Driver.objects.filter(name__icontains=search_query)
        if not matching_drivers:
            return False, "No drivers found matching the query."
        
        for driver in matching_drivers:
            buttons = [
                {"text": "Money", "callback_data": f"exit_reason|{driver.id}|money"},
                {"text": "Miscommunication", "callback_data": f"exit_reason|{driver.id}|miscommunication"}
            ]
            reply_markup = {"inline_keyboard": [buttons]}
            self.send_message(self.chat_id, f"Driver: {driver.name}", reply_markup=json.dumps(reply_markup))
        
        return True, "Drivers listed with feedback options."


    def process_callback_query(self):
        query_data = self.callback_query.get('data', '')
        action, driver_id, reason_category = query_data.split('|')
        if action == 'exit_reason':
            return self.log_exit_reason(driver_id, reason_category)

    def log_exit_reason(self, driver_id, reason_category):
        try:
            driver = Driver.objects.get(pk=driver_id)
            exit_reason, created = ExitReason.objects.update_or_create(
                driver=driver, 
                defaults={"reason_category": reason_category}
            )
            # Delete the original message that contained the callback button
            self.delete_message(self.user_id, self.message_id)
            # Send a confirmation message
            if created:
                message = f"Exit reason for {driver.name} logged as: {reason_category}"
            else:
                message = f"Exit reason for {driver.name} updated to: {reason_category}"
            self.send_message(self.user_id, message)
            return True
        except Driver.DoesNotExist:
            self.send_message(self.user_id, "Driver not found.")
            return False



    def collect_exit_reason(self):
        reason_category = self.determine_reason_category()
        driver = Driver.objects.filter(name=self.user_input.split()[1]).first()  # Assumes driver name follows command keyword

        ExitReason.objects.create(
            driver=driver,
            reason_category=reason_category,
        )
        return True, "Thank you for providing feedback!"  # Adjust to ensure consistency

    def determine_reason_category(self):
        if 'money' in self.user_input:
            return 'money'
        elif 'miscommunication' in self.user_input:
            return 'miscommunication'
        else:
            return 'other'

    def request_detailed_reason(self):
        # This is a placeholder; managing conversation state is needed here
        self.send_message(self.chat_id, "Please provide a detailed reason.")
        # A mechanism to capture the next user input should be implemented
        return ""  # This needs to be replaced with actual input handling

    def send_greeting(self):
        success = self.send_message(self.chat_id, "Hello, how can I assist you?")
        return success  # Ensures the return is consistent with other methods
