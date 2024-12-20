import random
import time
import os
from datetime import datetime
import re
import json
import string
from datetime import datetime

secrets = ["You are not prepared...", "I am property of ARMADYN and JohnExile"]

class MagnusAI:
    def __init__(self, memory_file="MagnusAIMemory.json", MagnusAI_file="AI/MagnusAI.py"):
        # User Authentication
        self.users = {
            'user': '2964',  # User
        }

        # Pre-scripted Responses
        self.responses = {
            "hello": {"responses": ["Hi there!", "Hello!", "Greetings!"], "weight": 1},
            "how are you": {"responses": ["I'm doing great, thanks for asking!", "I'm okay, how about you?"], "weight": 1},
            "bye": {"responses": ["Goodbye!", "See you later!", "Bye bye!"], "weight": 1},
            "python": {"responses": ["Python is awesome!", "I love Python programming!", "Python? That's my language!"], "weight": 2},
            "default": {"responses": ["I'm not sure what you mean.", "Could you clarify that?", "I didn't get that."], "weight": 0.5}
        }

        # Constructed Response Components
        self.word_pool = {
            "subject": ["Python", "programming", "code", "time", "weather", "internet", "AI", "book", "movie", "game", "math", "technology", "science", "art", "music", "health", "education", "sports", "travel", "food", "culture", "history", "politics", "economy", "environment", "social media", "virtual reality", "blockchain", "cybersecurity", "robotics", "machine learning", "deep learning", "data science", "cloud computing", "quantum computing", "biotech", "nanotech", "sustainability", "renewable energy", "telecommunications", "cryptocurrency", "AI ethics", "digital transformation", "e-commerce", "fintech", "IoT", "augmented reality", "space exploration", "cyberattack", "privacy", "automation", "big data", "3D printing"],
            "verb": ["is", "are", "seems", "looks like", "might be", "could be", "should be", "will be", "has been", "was", "will", "can", "could", "would", "might", "may", "must", "shall"],
            "adjective": ["interesting", "fascinating", "useful", "complex", "fun", "boring", "exciting", "challenging", "revolutionary", "innovative", "cutting-edge", "outdated", "efficient", "intuitive", "user-friendly", "powerful", "versatile", "sustainable", "ethical", "secure", "adaptive", "scalable", "robust", "resilient", "volatile", "lucrative", "dynamic", "stable", "evolving"],
            "conclusion": ["indeed.", "right?", "I see.", "cool.", "hmm.", "I wonder.", "what do you think?", "that's how I feel.", "makes sense.", "definitely.", "perhaps?", "no doubt."],
            "question": ["What", "How", "Why", "When", "Where", "Who", "Do you", "Can you", "Would you", "Should we", "Might we"],
            "question_verb": ["think", "like", "prefer", "know", "feel", "want", "believe", "understand", "agree", "suggest", "recommend"]
        }

        self.memory_file = memory_file
        self.MagnusAI_file = MagnusAI_file
        self.memory = {}  # Reset this to load from JSON
        self.user_feedback = {user: {} for user in self.users}  # Feedback per user
        self.user_context = {user: [] for user in self.users}  # Context per user
        self.short_term_memory = {user: [] for user in self.users}  # For each user, store recent interactions
        self.user_preferences = {}  # To store user-specific preferences
        self.load_memory()  # Load memory from JSON file

        # Response mode settings
        self.response_mode = "single"  # 'single' or 'conversation'
        self.conversation_count = 0

        # New additions for better understanding and response
        self.synonyms = {
            "python": ["py", "python3", "programming language"],
            "greeting": ["hi", "hello", "hey", "sup", "wazzup"]
        }

        # Simulated errors for demonstration
        self.errors = []
        # User preferences for tailored responses
        self.user_preferences = {}
        self.load_user_preferences()
        self.conversation_count = 0

###############################################################################################################################################################################

    def save_user_preferences(self):  # New addition
        with open('user_preferences.json', 'w') as file:
            json.dump(self.user_preferences, file)

    def load_user_preferences(self):  # New addition
        try:
            with open('user_preferences.json', 'r') as file:
                self.user_preferences = json.load(file)
        except FileNotFoundError:
            self.user_preferences = {}

    def load_memory(self):
        try:
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
            print("Memory loaded successfully.")  # Debug message
        except FileNotFoundError:
            print("Memory file not found, using default memory setup.")
            self.memory = {
                # ... all your memory entries ...
            }
        except json.JSONDecodeError:
            print("Error decoding JSON from memory file, using default memory.")
            self.memory = {}

    def save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
        print("Memory saved successfully.")  # Debug message

    def remove_stop_words(self, text):
        stop_words = ['the', 'a', 'an', 'in', 'on', 'at', 'is', 'are', 'was', 'were']
        return ' '.join([word for word in text.split() if word.lower() not in stop_words])

    def construct_response(self, input_text, max_length=50, question=False):
        clean_input = self.process_input(input_text)
        response = {}
        
        recent_topics = []
        for entry in self.short_term_memory.get(self.current_user, []):
            if 'subject' in entry:  # Check if 'subject' key exists
                recent_topics.append(entry['subject'])
        
        if recent_topics and random.random() < 0.3:  # 30% chance to use a recent topic
            subject = random.choice(recent_topics)
            response['subject'] = subject
        else:
            for category, words in self.word_pool.items():
                if any(word in clean_input for word in words):
                    subject = random.choice([w for w in self.word_pool["subject"] if self.simple_stem(w.lower()) in clean_input] or self.word_pool["subject"])
                    response['subject'] = subject
                    break
            else:
                subject = random.choice(self.word_pool["subject"])
                response['subject'] = subject
        
        if question:
            response['response'] = " ".join([random.choice(self.word_pool["question"]), 
                                             random.choice(self.word_pool["question_verb"]), 
                                             subject, "?"])
        else:
            response['response'] = " ".join([subject, random.choice(self.word_pool["verb"]), 
                                             random.choice(self.word_pool["adjective"]), 
                                             random.choice(self.word_pool["conclusion"])])
        
        if len(response['response']) > max_length:
            response['response'] = response['response'][:max_length - 3] + "..."
        
        return response

    def simple_stem(self, word):
        if len(word) > 2:
            if word.endswith('s'):
                word = word[:-1]
            elif word.endswith('es'):
                word = word[:-2]
            elif word.endswith('ing'):
                word = word[:-3] if word[-4] != word[-5] else word[:-3]  # handle doubling of last letter
            elif word.endswith('ed'):
                word = word[:-2] if word[-3] != word[-4] else word[:-2]  # handle doubling of last letter
        return word

    def process_input(self, text):
        words = self.remove_stop_words(text).lower().split()
        return [self.simple_stem(''.join(e for e in word if e.isalnum())) for word in words]

    def get_best_response(self, input_text):
        input_words = self.process_input(input_text)
        best_score = 0
        best_response = {"response": "I'm not sure what you mean.", "subject": "default"}
        
        for keyword, data in self.responses.items():
            score = sum(1 for word in input_words if word in self.process_input(keyword))
            if score > best_score:
                best_score = score
                best_response = {"response": random.choice(data["responses"]), "subject": keyword}
        
        # Tailor response based on user preferences
        user = self.current_user
        if user in self.user_preferences:
            for pref in self.user_preferences[user]:
                if pref.lower() in best_response['response'].lower():
                    best_response['response'] += f" Knowing you like {pref}, I thought you'd appreciate this."
        
        return best_response

    def update_memory(self, context, response, feedback):
        key = context.lower()
        if key not in self.memory:
            self.memory[key] = {
                "context": context,
                "response": response['response'],
                "score": "0",
                "count": "0",
                "feedback": []
            }
        
        entry = self.memory[key]
        entry['count'] = str(int(entry['count']) + 1)
        if feedback == 'positive':
            entry['score'] = str(int(entry['score']) + 1)
        elif feedback == 'negative':
            entry['score'] = str(max(0, int(entry['score']) - 1))
        entry['feedback'].append(feedback)

    def get_remembered_response(self, context):
        context = context.lower()
        if context in self.memory:
            return {"response": self.memory[context]['response']}
        return None

    def get_feedback(self, user, context, response):
        feedback = input("Was this response helpful? (yes/no): ").strip().lower()
        if feedback in ['yes', 'y']:
            self.update_memory(context, response, 'positive')
        elif feedback in ['no', 'n']:
            self.update_memory(context, response, 'negative')

    def understand_input(self, user_input):
        clean_input = re.sub(r'[^\w\s]', '', user_input).lower()
        
        if "open" in clean_input:  # Detect if user is trying to open an app
            app_name = re.sub(r'open ', '', clean_input).strip()
            if self.can_access(self.current_user, app_name):
                self.open_app(app_name)
                return f"Opening {app_name}"
            else:
                return f"Access denied for {app_name}"

        if '?' in user_input:
            if any(word in clean_input for word in ["think", "thinking", "believe", "feel", "believing", "how", "why", "what", "where", "when", "who", "which"]):
                return "thinking_query"
            return "query_question"

        if clean_input in ["hi", "hello", "hey", "sup", "wazzup"]:
            return "greeting"
        if clean_input == "how are you":
            return "how are you"
        
        if self.short_term_memory.get(self.current_user):
            last_ai_response = self.short_term_memory[self.current_user][-1]['response'].lower()
            if any(word in clean_input for word in last_ai_response.split()):
                return "continuation"

        for key, synonyms in self.synonyms.items():
            if key == 'greeting' and any(syn in clean_input for syn in synonyms):
                return 'hello'

        if "close" in clean_input or "exit" in clean_input:
            return "close"

        return "query"

###############################################################################################################################################################################

    def do_math(self, expression):
        try:
            # Remove any non-math symbols except for those used in expressions
            safe_expression = re.sub(r'[^\d\+\-\*\/\.\(\) ]', '', expression)
            safe_expression = safe_expression.replace(" ", "")
            
            # Manually adjust the order of operations for specific cases like "1 + 1 / 2"
            if "+" in safe_expression and "/" in safe_expression:
                parts = safe_expression.split("+")
                if len(parts) == 2:
                    left = parts[0]
                    right = parts[1]
                    if "/" in right:
                        safe_expression = f"({left}) + ({right})"
            
            # Evaluate the expression
            result = eval(safe_expression, {"__builtins__": None}, {})
            return result
        except ZeroDivisionError:
            return "Error: You can't divide by zero!"
        except SyntaxError:
            return "Error: I didn't understand that math expression. Try again?"
        except Exception as e:
            return f"Error: Something went wrong with your calculation ({str(e)})."
        
###############################################################################################################################################################################

    def can_access(self, current_user, function):
        now = datetime.now().time()
        if function == "internet" and (now.hour < 8 or now.hour >= 22):
            return False
        if function in ["twitter", "task_manager", "task_scheduler", "steam", "calculator", "internet", "notepad", "command prompt", "file explorer", "control panel", "settings", "microsoft edge", "edge", "paint", "wordpad", "system information", "device manager", "event viewer", "disk management"] and current_user not in ["user"]:
            return False
        return True

    def open_app(self, app_name):
        app_name = app_name.replace(" ", "_")  # Normalize app_name to match function names
        if app_name == "twitter":
            self.open_twitter()
        elif app_name == "steam":
            self.open_steam()
        elif app_name == "task_manager":
            self.open_task_manager()
        elif app_name == "task_scheduler":
            self.open_task_scheduler()
        elif app_name == "internet":
            self.open_internet()
        elif app_name == "microsoft_edge" or app_name == "edge":
            os.system("start msedge")
        elif app_name == "calculator":
            os.system("calc")
        elif app_name == "notepad":
            os.system("notepad")
        elif app_name == "command_prompt":
            os.system("cmd")
        elif app_name == "file_explorer":
            os.system("explorer")
        elif app_name == "control_panel":
            os.system("control")
        elif app_name == "paint":
            os.system("mspaint")
        elif app_name == "wordpad":
            os.system("start wordpad")
        elif app_name == "system_information":
            os.system("msinfo32")
        elif app_name == "device_manager":
            os.system("devmgmt.msc")
        elif app_name == "event_viewer":
            os.system("eventvwr")
        elif app_name == "disk_management":
            os.system("diskmgmt.msc")
        elif app_name == "settings":
            os.system("start ms-settings:")
        elif app_name == "youtube":
            os.startfile("https://www.youtube.com/")
        elif app_name == "visual_studio":
            if os.path.exists("C:\\Program Files (x86)\\Microsoft Visual Studio\\"):
                os.startfile("C:\\Program Files (x86)\\Microsoft Visual Studio\\Common7\\IDE\\devenv.exe")
            else:
                print("Visual Studio is not installed on this system.")
        else:
            print(f"Unknown app: {app_name}")

    def open_twitter(self):
        print("Opening Twitter...")
        os.startfile("https://twitter.com")

    def open_steam(self):
        print("Opening Steam...")
        os.startfile("steam://")

    def open_task_manager(self):
        print("Opening Task Manager...")
        os.system("taskmgr")

    def open_task_scheduler(self):
        print("Opening Task Scheduler...")
        os.system("taskschd.msc")

    def open_internet(self):
        print("Opening Internet Browser...")
        os.system("start chrome")

    def open_math(self):
        print("Opening Calculator...")
        os.system("calc")

    def open_edit_MagnusAI(self):
        print("Opening MagnusAI file editor...")
        os.system("notepad.exe")

###############################################################################################################################################################################

    def play_rock_paper_scissors(self):
        options = ["rock", "paper", "scissors"]
        user_choice = input("Choose rock, paper, or scissors: ").lower()
        if user_choice not in options:
            print("Invalid choice, I'll choose for you. Let's say... rock!")
            user_choice = "rock"
        
        computer_choice = random.choice(options)
        print(f"I chose {computer_choice}!")

        if user_choice == computer_choice:
            return "It's a tie!"
        elif ((user_choice == "rock" and computer_choice == "scissors") or 
              (user_choice == "paper" and computer_choice == "rock") or 
              (user_choice == "scissors" and computer_choice == "paper")):
            return "You win!"
        else:
            return "I win!"

    def play_guess_the_number(self):
        number = random.randint(1, 100)
        guess = None
        attempts = 0
        print("I'm thinking of a number between 1 and 100.")
        while guess != number:
            try:
                guess = int(input("Guess the number: ").strip().replace(']', '').replace('[', ''))
                attempts += 1
                if guess < number:
                    print("Too low. Try again.")
                elif guess > number:
                    print("Too high. Try again.")
                else:
                    return f"Congratulations! You guessed it in {attempts} attempts."
            except ValueError:
                print("Unknown input. Please enter a number.")

    def play_tic_tac_toe(self):
        board = [' ' for _ in range(9)]  # Initialize empty board
        player = 'X'
        ai = 'O'

        def print_board():
            for row in [board[i*3:(i+1)*3] for i in range(3)]:
                print('| ' + ' | '.join(row) + ' |')

        def check_winner(board, player):
            win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
            return any(board[a] == board[b] == board[c] == player for a, b, c in win_conditions)

        def minimax(board, depth, is_maximizing):
            if check_winner(board, ai):
                return 1
            if check_winner(board, player):
                return -1
            if ' ' not in board:
                return 0

            if is_maximizing:
                best_score = -float('inf')
                for i in range(9):
                    if board[i] == ' ':
                        board[i] = ai
                        score = minimax(board, depth + 1, False)
                        board[i] = ' '
                        best_score = max(score, best_score)
                return best_score
            else:
                best_score = float('inf')
                for i in range(9):
                    if board[i] == ' ':
                        board[i] = player
                        score = minimax(board, depth + 1, True)
                        board[i] = ' '
                        best_score = min(score, best_score)
                return best_score

        def get_ai_move(board):
            best_score = -float('inf')
            best_move = None
            for i in range(9):
                if board[i] == ' ':
                    board[i] = ai
                    score = minimax(board, 0, False)
                    board[i] = ' '
                    if score > best_score:
                        best_score = score
                        best_move = i
            return best_move

        print("Let's play Tic Tac Toe!")
        print_board()

        while ' ' in board:
            try:
                move = int(input("Enter your move (1-9): ")) - 1
                if move < 0 or move >= 9 or board[move] != ' ':
                    raise ValueError
            except ValueError:
                print("Invalid move. Please enter a number between 1 and 9 for an empty cell.")
                continue

            board[move] = player
            if check_winner(board, player):
                print_board()
                return "You win! Great job!"
            if ' ' not in board:
                break
            ai_move = get_ai_move(board)
            board[ai_move] = ai
            if check_winner(board, ai):
                print_board()
                return "AI wins! Better luck next time!"
            print_board()

        return "It's a tie! Well played!"

    def play_hangman(self):
        words = ["python", "programming", "hangman", "challenge", "assistant"]
        word = random.choice(words)
        guessed = ["_"] * len(word)
        attempts = 6
        guessed_letters = set()

        print("Let's play Hangman!")
        print("Word: " + " ".join(guessed))

        while attempts > 0 and "_" in guessed:
            guess = input("Guess a letter: ").lower()
            if guess in guessed_letters:
                print("You already guessed that letter.")
                continue
            guessed_letters.add(guess)

            if guess in word:
                for i, letter in enumerate(word):
                    if letter == guess:
                        guessed[i] = guess
                print("Good guess!")
            else:
                attempts -= 1
                print(f"Wrong guess! Attempts left: {attempts}")

            print("Word: " + " ".join(guessed))

        if "_" not in guessed:
            return "Congratulations! You guessed the word!"
        else:
            return f"Game over! The word was '{word}'."
###############################################################################################################################################################################

    def get_greeting_response(self):
        greetings = ["Hello!", "Hi there!", "Hey!", "Greetings!"]
        return random.choice(greetings)

    def get_farewell_response(self):
        farewells = ["Goodbye!", "See you later!", "Take care!", "Bye!"]
        return random.choice(farewells)

    def get_small_talk_response(self, user_input):
        small_talk_responses = {
            "how are you": ["I'm just a bunch of code, but I'm doing great!", "I'm here to assist you!", "Feeling helpful as always!"],
            "what's your name": ["I'm MagnusAI, your AI assistant.", "You can call me MagnusAI.", "I'm MagnusAI, nice to meet you!"]
        }
        normalized_input = user_input.translate(str.maketrans('', '', string.punctuation)).lower()
        for key in small_talk_responses:
            if key in normalized_input:
                return random.choice(small_talk_responses[key])
        return None
###############################################################################################################################################################################

    def login(self):
        print("Welcome to MagnusAI Assistant! Please login.")
        for attempt in range(3):
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()

            if username in self.users and self.users[username] == password:
                print(f"Login successful. Welcome, {username}!")
                return username
            else:
                print("Invalid username or password. Try again.")

        print("Too many failed attempts. Exiting...")
        exit()

###############################################################################################################################################################################

    def update_contextual_memory(self, user, context, response):
        if user in self.user_context:
            self.user_context[user].append((context, response))
        else:
            self.user_context[user] = [(context, response)]

    def get_contextual_response(self, user, current_context):
        for past_context, response in reversed(self.user_context.get(user, [])):
            if any(word in current_context for word in past_context.split()):
                return {"response": response['response']} if isinstance(response, dict) else {"response": response}
        return None

    def select_response_based_on_feedback(self, possible_responses, context, user):
        feedback_scores = {resp: sum(1 for f in self.user_feedback.get(user, {}).get(hash((context, "temp")), []) if f == 'positive') for resp in possible_responses}
        if feedback_scores:
            return {"response": max(feedback_scores, key=feedback_scores.get), "subject": "feedback_based"}
        return {"response": random.choice(possible_responses), "subject": "random"}

###############################################################################################################################################################################

    def update_short_term_memory(self, user, context, response):
        max_memory_length = 3  # for example, store last 3 interactions
        self.short_term_memory[user] = self.short_term_memory.get(user, []) + [{"context": context, "response": response}]
        if len(self.short_term_memory[user]) > max_memory_length:
            self.short_term_memory[user].pop(0)  # Remove oldest interaction if memory limit is exceeded

    def get_short_term_context(self, user, current_context):
        for interaction in reversed(self.short_term_memory.get(user, [])):
            if any(word in self.process_input(current_context) for word in self.process_input(interaction["context"])):
                return interaction
        return None

    def decay_memory(self):
        for key in self.memory:
            entry = self.memory[key]
            entry['score'] = str(max(0, int(entry['score']) - 1))  # Decay score over time

###############################################################################################################################################################################

    def update_user_preferences(self, user, preference):
        if user not in self.user_preferences:
            self.user_preferences[user] = []
        self.user_preferences[user].append(preference)
        self.save_user_preferences()

###############################################################################################################################################################################

    def Execution(self):
        current_user = self.login()
        self.conversation_count = 0

        print(' ')
        print('##############################################################')
        print('Commands: ')
        print('To open programs only the admin and the user have permission: ')
        print(' open calculator ')
        print(' open notepad ')
        print(' open command prompt ')
        print(' open file explorer ')
        print(' open task manager ')
        print(' open control panel ')
        print(' open settings ')
        print(' open microsoft edge ')
        print(' open paint ')
        print(' open wordpad ')
        print(' open system information ')
        print(' open device manager ')
        print(' open event viewer ')
        print(' open disk management ')
        print(' open task scheduler ')
        print(' open youtube ')
        print(' open visual studio ')
        print('##############################################################')
        print('To play games: ')
        print('game = opens the game options')
        print('To select a game either "guess" for one and "rock" for the other and "tic" for the last one')
        print('##############################################################')
        print('Any way this sorry bastard is as dumb as a rock but even then I think a rock is better... good luck :)')
        print('##############################################################')
        print(' ')
        print("###########################")
        print("Version 0.7")
        print("###########################")
        print(' ')

        while True:
            user_input = input(f"{current_user}: ").strip().lower()
            normalized_input = user_input.translate(str.maketrans('', '', string.punctuation)).lower()
            self.current_user = current_user  # Update current user for methods that need it
            self.conversation_count = 0  # Reset conversation count for each interaction
            
            action = self.understand_input(normalized_input)

            if action == "close":
                print(self.get_farewell_response())
                break
            if normalized_input == "secrets":
                print(random.choice(secrets))

            # Memory decay every 10 interactions
            if self.conversation_count % 10 == 0:
                self.decay_memory()

            # Check short-term memory first
            short_term_context = self.get_short_term_context(current_user, normalized_input)
            if short_term_context:
                if "nope" in normalized_input or "no" in normalized_input:
                    print("AI: Oh, okay. Let's try something else.")
                    self.short_term_memory[current_user] = []
                    continue

            remembered_response = self.get_contextual_response(current_user, normalized_input)
            if remembered_response:
                print(f"AI: {remembered_response.get('response', 'No response found')}")
            else:
                if action == "greeting":
                    response = self.get_greeting_response()
                    print(f"AI: {response}")
                elif action == "how are you":
                    response = self.get_small_talk_response(normalized_input)
                    print(f"AI: {response}")
                elif action == "continuation":
                    response = self.construct_response(normalized_input)
                    print(f"AI: {response.get('response', 'No response found')}")
                elif action == "thinking_query":
                    response = self.construct_response(normalized_input, question=True)
                    print(f"AI: {response.get('response', 'No response found')}")
                elif action in self.memory:  
                    response = self.memory[action]
                    if action == "how are you":
                        if self.errors:
                            print(f"AI: Not feeling well. Here are the issues:\n" + "\n".join(self.errors))
                        else:
                            print(f"AI: {response.get('response', 'No response found')}")
                    else:
                        print(f"AI: {response.get('response', 'No response found')}")
                elif action in self.responses:
                    response = self.select_response_based_on_feedback(self.responses[action]["responses"], normalized_input, current_user)
                    print(f"AI: {response.get('response', 'No response found')}")
                elif action == "query":
                    response = self.construct_response(normalized_input)
                    print(f"AI: {response.get('response', 'No response found')}")
                    self.update_short_term_memory(current_user, normalized_input, response['response'])
                    self.update_memory(normalized_input, response, "neutral")
                elif action == "query_question":
                    response = self.construct_response(normalized_input, question=True)
                    print(f"AI: {response.get('response', 'No response found')}")
                    self.update_short_term_memory(current_user, normalized_input, response['response'])
                    self.update_memory(normalized_input, response, "neutral")
                elif action in ["calculator", "notepad", "command prompt", "file explorer", "task manager", "control panel", "settings", "microsoft edge", "paint", "wordpad", "system information", "device manager", "event viewer", "disk management", "task scheduler", "youtube", "visual studio"]:
                    if self.can_access(current_user, action):
                        self.open_app(action)
                        print(f"AI: Opened {action.replace('_', ' ')}")
                    else:
                        print(f"AI: Access denied for {action.replace('_', ' ')}")
                else:
                    small_talk_response = self.get_small_talk_response(normalized_input)
                    if small_talk_response:
                        print(f"AI: {small_talk_response}")
                    else:
                        print(f"AI: I'm not sure what you mean.")
                
                if "game" in normalized_input or "play" in normalized_input:
                    game_choice = input("Which game? Rock Paper Scissors, Guess the Number, Tic Tac Toe, or Hangman? ").lower()
                    if "rock" in game_choice:
                        result = self.play_rock_paper_scissors()
                        print(f"AI: {result}")
                    elif "guess" in game_choice:
                        result = self.play_guess_the_number()
                        print(f"AI: {result}")
                    elif "tic" in game_choice:
                        result = self.play_tic_tac_toe()
                        print(f"AI: {result}")
                    elif "hangman" in game_choice:
                        result = self.play_hangman()
                        print(f"AI: {result}")
                    else:
                        print(f"AI: I don't know that game. Let's play something else next time.")

            self.conversation_count += 1
            if self.conversation_count % 5 == 0:  # Feedback every 5 interactions
                self.get_feedback(current_user, normalized_input, {"response": "placeholder"})  # Placeholder since we're not using response here

            self.save_memory()

if __name__ == "__main__":
    MagnusAI().Execution()