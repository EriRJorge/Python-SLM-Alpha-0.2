import json
import os
import random

class ConversationAI:
    def __init__(self, data_file='word_meanings.json'):
        self.data_file = data_file
        self.predefined_responses = {
            "how are you": [
                "I'm just a bunch of code, but I'm here to help!",
                "I'm fine, thanks!",
                "Feeling digital as always!"
            ],
            "what is your name": [
                "I'm Eliana Alpha0.2.",
                "You can call me Eliana.",
                "I'm Eliana, your friendly AI.",
                "I'm Eliana, but you can call me daddy."
            ],
            "what do you do": [
                "I tell you what I know.",
                "I'm here to talk to you because you are lonely.",
                "I give you the meaning of words and talk."
            ],
            "hello": [
                "Hello! What do you want?",
                "Hi there! What can I do for you?",
                "Hey! How's it going?"
            ],
            "hi": [
                "Hello! What do you want?",
                "Hi there! What can I do for you?",
                "Hey! How's it going?"
            ],
            "hey": [
                "Hello! What do you want?",
                "Hi there! What can I do for you?",
                "Hey! How's it going?"
            ]
        }
        self.response_counters = {key: 0 for key in self.predefined_responses.keys()}
        self.word_meanings = self.load_data()
        self.context_history = []
        self.user_patterns = []
        self.grammar_words = {"what", "is", "a", "the", "of", "and", "to", "in", "for", "with", "how", "where", "when", "who", "why"}
        self.question_templates = {
            "what is": "{} is {}.",
            "tell me about": "{} is {}."
        }
        self.learning_mode = False  # Flag to indicate if learning mode is active

    def preprocess_text(self, text):
        """Convert text to lowercase and remove punctuation."""
        return text.lower().strip().rstrip('?').rstrip('.').rstrip('!')

    def get_meaning(self, word):
        """Get the meaning of a word from the dictionary."""
        return self.word_meanings.get(word, None)
    
    def add_meaning(self, word, meaning):
        """Add a new word-meaning pair to the dictionary and save."""
        self.word_meanings[word] = meaning
        self.save_data()
    
    def extract_subject(self, text):
        """Extract the subject from the input text based on question patterns."""
        words = self.preprocess_text(text).split()
        
        for key in self.question_templates.keys():
            key_words = key.split()
            if ' '.join(words[:len(key_words)]) == key:
                return ' '.join(words[len(key_words):]).strip()
        return None
    
    def generate_response(self, text):
        """Generate a response based on the meanings of words in the input text."""
        if self.learning_mode:
            return "I am in learning mode. Please provide the word and its meaning or type 'nevermind' to cancel."

        subject = self.extract_subject(text)
        
        if subject:
            subject_meaning = self.get_meaning(subject)
            if subject_meaning:
                template = next((tmpl for q, tmpl in self.question_templates.items() if text.lower().startswith(q)), None)
                if template:
                    return template.format(subject, subject_meaning)
                else:
                    return f"I don't know the meaning of {subject}. Could you please tell me its meaning?"

        # Handle predefined responses
        preprocessed_text = self.preprocess_text(text)
        if preprocessed_text in self.predefined_responses:
            response_list = self.predefined_responses[preprocessed_text]
            index = self.response_counters[preprocessed_text]
            response = response_list[index % len(response_list)]
            self.response_counters[preprocessed_text] += 1
            return response

        # Handle unknown greetings
        if any(word in preprocessed_text.split() for word in ["hello", "hi", "hey"]):
            self.learning_mode = True
            return "I don't recognize this greeting. Please provide a response for it or type 'nevermind' to cancel."

        # If no subject or pattern matched, default to a generic response
        words = preprocessed_text.split()
        unknown_words = [word for word in words if word not in self.grammar_words and not self.get_meaning(word)]

        if unknown_words:
            return f"I don't know the meaning of {', '.join(unknown_words)}. Could you please tell me their meanings?"

        response_parts = [self.get_meaning(word) if self.get_meaning(word) else word for word in words if word not in self.grammar_words]
        response = ' '.join(response_parts) if response_parts else "How am I supposed to know. I don't have any information on that."
        
        return response
    
    def handle_unknown_words(self, text):
        """Handle user input to learn new words."""
        if text.lower().startswith("learn:"):
            parts = text[6:].strip().split(' ', 1)
            if len(parts) == 2:
                word, meaning = parts
                if self.validate_meaning(meaning):
                    self.add_meaning(word, meaning)
                    return f"Thank you so much! I've learned the meaning of '{word}' as '{meaning}'."
                else:
                    return "I'm not too sure about that. Please provide a valid meaning."
            else:
                return "No that's wrong. Use 'learn: word meaning'."
        return ""

    def handle_new_greeting(self, text):
        """Handle user input to learn new greetings."""
        if text.lower().startswith("learn greeting:"):
            parts = text[15:].strip().split(' ', 1)
            if len(parts) == 2:
                greeting, response = parts
                greeting = self.preprocess_text(greeting)
                if greeting in self.predefined_responses:
                    self.predefined_responses[greeting].append(response)
                else:
                    self.predefined_responses[greeting] = [response]
                self.response_counters[greeting] = 0
                self.save_data()
                return f"Thank you! I've learned a new greeting: '{greeting}' with response '{response}'."
            else:
                return "No that's wrong. Use 'learn greeting: greeting response'."
        return ""

    def learn_speech_patterns(self, text):
        """Learn and store user's speech patterns."""
        self.user_patterns.append(text)
        if len(self.user_patterns) > 50:  # Limit the number of stored patterns
            self.user_patterns.pop(0)
    
    def generate_user_style_response(self):
        """Generate a response based on learned user speech patterns."""
        if not self.user_patterns:
            return "I'm not sure how to respond. Could you please tell me more?"

        # Simple approach: Randomly pick a response from stored patterns
        return random.choice(self.user_patterns)

    def load_data(self):
        """Load the dictionary from a JSON file."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as file:
                data = json.load(file)
                self.predefined_responses.update(data.get('predefined_responses', {}))
                return data.get('word_meanings', {})
        return {
            "help": "At least say please.",
            "order": "A request for something to be made, supplied, or served.",
            "anime": "Top tier entertainment",
            "god is good": "All the time"
        }

    def save_data(self):
        """Save the dictionary and predefined responses to a JSON file."""
        data = {
            'word_meanings': self.word_meanings,
            'predefined_responses': self.predefined_responses
        }
        with open(self.data_file, 'w') as file:
            json.dump(data, file, indent=4)

    def validate_meaning(self, meaning):
        """Validate the meaning to ensure it's appropriate."""
        return len(meaning.strip()) > 0

    def update_context_history(self, text):
        """Update the context history with the latest conversation."""
        self.context_history.append(text)
        if len(self.context_history) > 10:  # Limit the context history size
            self.context_history.pop(0)

    def run(self):
        """Run the interactive conversation loop."""
        print("Welcome to Eliana Alpha0.2. Type 'bye bye' to end the conversation.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'bye bye':
                print("Okay, bye!")
                break

            if user_input.lower() == 'nevermind':
                if self.learning_mode:
                    self.learning_mode = False
                    print("Learning mode canceled.")
                else:
                    print("No action is in progress to cancel.")
                continue

            if self.learning_mode:
                response = self.handle_unknown_words(user_input)
                if response:
                    print("Eliana:", response)
                    continue

            if user_input.lower().startswith("learn greeting:"):
                response = self.handle_new_greeting(user_input)
                if response:
                    print("Eliana:", response)
                    continue

            self.update_context_history(user_input)
            self.learn_speech_patterns(user_input)
            
            if user_input.lower().startswith("learn:"):
                self.learning_mode = True
                response = self.handle_unknown_words(user_input)
            elif "look up" in user_input.lower():
                response = "I don't have internet access right now. Please provide the meaning or ask something else."
            else:
                response = self.generate_response(user_input)
                if not response:
                    response = self.generate_user_style_response()
            
            print("Eliana:", response)

# Example usage
if __name__ == "__main__":
    ai = ConversationAI()
    # Run the interactive conversation loop
    ai.run()
