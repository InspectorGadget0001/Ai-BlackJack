import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.core.window import Window
from kivy.uix.spinner import Spinner
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import ScreenManager, Screen
import random
import logging
import openai
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image


Window.size = (1500, 900)


kivy.require('1.0.9')

openai.api_key = 'You're API key here'  # Replace with your API key

# Set up logging
logging.basicConfig(filename='blackjack.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Set the background color to white
Window.clearcolor = (1, 1, 1, 1)




class TexturedButton(Button):
    def __init__(self, **kwargs):
        super(TexturedButton, self).__init__(**kwargs)
        self.background_normal = '/Users/tannermiller/Desktop/Blackjack app/istockphoto-848403320-612x612.jpg'


Builder.load_string("""
<CustomDropDown>:
""" + "\n".join([
    f"""
    Button:
        text: '{i}'
        size_hint_y: None
        height: 44
        on_release: root.select('{i}')
    """ for i in range(50, 1050, 50)
]) + """
""")

class Background(Widget):
    def __init__(self, **kwargs):
        super(Background, self).__init__(**kwargs)
        self.image = Image(source='/Users/tannermiller/Desktop/Blackjack app/istockphoto-848403320-612x612.jpg', size=self.size, allow_stretch=True)
        self.add_widget(self.image)

class CustomDropDown(DropDown):
    def open(self, widget):
        self._attach_to = widget
        super().open(widget)
        # position the drop-down menu above the button
        self.y = widget.top

class ColorScheme:
    primary = [0.00, 0.48, 0.98, 1]  # Bright Blue
    primary_light = [0.00, 0.71, 0.84, 1]  # Light Blue
    text_primary = [0.00, 0.00, 0.00, 1]  # Black
    text_secondary = [0.60, 0.60, 0.60, 1]  # Grey
    error = [0.91, 0.30, 0.24, 1]  # Red
    secondary = [0.96, 0.80, 0.26, 1]  # Yellow
    tertiary = [0.18, 0.80, 0.44, 1]  # Green



class BlackjackApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(DepositScreen(name='deposit'))
        sm.add_widget(BetScreen(name='bet'))
        sm.add_widget(Blackjack(name='blackjack'))
        return sm


class Blackjack(Screen, BoxLayout):
    player_hand = ListProperty([])
    dealer_hand = ListProperty([])
    player_score = ListProperty([])
    dealer_score = NumericProperty(0)
    status = StringProperty("")
    balance = NumericProperty(0)
    bet = NumericProperty(0)
    current_hand_index = NumericProperty(0)

    def __init__(self, initial_balance=0, **kwargs):
        super(Blackjack, self).__init__(**kwargs)
        self.balance = initial_balance
        self.orientation = "vertical"
        self.padding = 10
        self.spacing = 10

        # Create labels
        self.player_label = Label(text="Player's Hand:", font_size=30, color=[0, 0, 0, 1])
        self.dealer_label = Label(text="Dealer's Hand:", font_size=30, color=[0, 0, 0, 1])
        self.balance_label = Label(text="Balance: $" + str(self.balance), font_size=30, color=[0, 0, 0, 1])
        self.dealer_commentary_label = Label(font_size=24, color=[0, 0, 0, 1])
        self.end_game_label = Label(font_size=30, color=[0, 0, 0, 1])

        # Updated dealer_commentary_label
        self.dealer_commentary_label_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        self.dealer_commentary_label = Label(
            text_size=(self.width, None),
            shorten=True,
            font_size=24, 
            color=[0, 0, 0, 1], 
            halign='center', 
            valign='middle'
)
        self.dealer_commentary_label.bind(size=self.dealer_commentary_label.setter('text_size'))      
        self.end_game_label = Label(font_size=30, color=[0, 0, 0, 1])


        # Create buttons
        self.split_button = TexturedButton(text="Split", font_size=18, color=ColorScheme.text_primary, background_color=ColorScheme.primary, disabled=True)
        self.split_button.bind(on_release=self.split)
        self.double_down_button = TexturedButton(text="Double Down", font_size=18, color=ColorScheme.text_primary, background_color=ColorScheme.primary, disabled=True)
        self.double_down_button.bind(on_release=self.double_down)
        self.hit_button = TexturedButton(text="Hit", font_size=18, color=ColorScheme.text_primary, background_color=ColorScheme.primary, disabled=True)
        self.hit_button.bind(on_release=self.hit)
        self.stand_button = TexturedButton(text="Stand", font_size=18, color=ColorScheme.text_primary, background_color=ColorScheme.primary, disabled=True)
        self.stand_button.bind(on_release=self.stand)
        self.deal_button = TexturedButton(text="Deal", font_size=18, color=ColorScheme.text_primary, background_color=ColorScheme.primary, disabled=False)
        self.deal_button.bind(on_release=self.deal)

        # Create layout for buttons
        self.button_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.2))
        self.button_layout.add_widget(self.split_button)
        self.button_layout.add_widget(self.double_down_button)
        self.button_layout.add_widget(self.hit_button)
        self.button_layout.add_widget(self.stand_button)
        self.button_layout.add_widget(self.deal_button)
        # Create new game button
        self.new_game_button = TexturedButton(text="New Game", font_size=18, color=ColorScheme.primary_light, background_color=ColorScheme.primary, disabled=True)
        self.new_game_button.bind(on_release=self.new_game)
        self.button_layout.add_widget(self.new_game_button)


        # Create bet button
        self.bet_button = Button(text ='Select Bet', size_hint = (None, None), size =(200, 44))
        dropdown = CustomDropDown()
        dropdown.attach_to = self.bet_button  # Attach the dropdown to the bet button
        self.bet_button.bind(on_release=lambda instance: dropdown.open(instance))
        dropdown.bind(on_main_release=lambda instance, x: setattr(self.bet_button, 'text', x))  

        # Bind the change_bet method to the dropdown's on_select event
        dropdown.bind(on_select=self.change_bet)

        # Bind the dropdown to the button
        dropdown.bind(on_select=lambda instance, x: setattr(self.bet_button, 'text', x))

        self.button_layout.add_widget(self.bet_button)

        # Create layout for each label
        self.player_label_layout = BoxLayout()
        self.dealer_label_layout = BoxLayout()
        self.balance_label_layout = BoxLayout()
        self.dealer_commentary_label_layout = BoxLayout()
        self.end_game_label_layout = BoxLayout()

        # Add labels to their respective layouts
        self.player_label_layout.add_widget(self.player_label)
        self.dealer_label_layout.add_widget(self.dealer_label)
        self.balance_label_layout.add_widget(self.balance_label)
        self.dealer_commentary_label_layout.add_widget(self.dealer_commentary_label)
        self.end_game_label_layout.add_widget(self.end_game_label)

        # Create main layout and add all the layouts
        self.main_layout = BoxLayout(orientation='vertical')
        self.main_layout.add_widget(self.player_label_layout)
        self.main_layout.add_widget(self.dealer_label_layout)
        self.main_layout.add_widget(self.balance_label_layout)
        self.main_layout.add_widget(self.dealer_commentary_label_layout)
        self.main_layout.add_widget(self.end_game_label_layout)
        self.main_layout.add_widget(self.button_layout)

        # Add main layout to the root widget
        self.add_widget(self.main_layout)
    
    def change_bet(self, instance, x):
        bet_amount = int(x)  # Use the selected value to set the bet amount
        if bet_amount > self.balance:
            self.status = "Insufficient balance for this bet."
            self.update_labels()
        else:
            self.bet = bet_amount  # Set the new bet


    def draw_card(self):
        return random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11])

    def calculate_score(self):
        def score(hand):
            total = sum(hand)
            num_aces = hand.count(11)
            while total > 21 and num_aces > 0:
                total -= 10  # Count the current Ace as 1 instead of 11
                num_aces -= 1
            return total
        if any(isinstance(i, list) for i in self.player_hand):
            self.player_score = [score(hand) for hand in self.player_hand]
        else:
            self.player_score = [score(self.player_hand)]
        self.dealer_score = score(self.dealer_hand)

    def get_dealer_commentary(self):
        try:
            context = f"The player's hand: {', '.join(str(card) for card in self.player_hand)}\n" \
                    f"The dealer's hand: {', '.join(str(card) for card in self.dealer_hand)}\n" \
                    f"The player's score: {', '.join(str(score) for score in self.player_score)}\n" \
                    f"The dealer's score: {self.dealer_score}"
            prompt = f"{context}\n\nTake on the role of an expert blackjack dealer  in the movie the wolf on wallstreet who provides brief, game-specific commentary. Limit response to 100 characters or less"
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that says Fuck a lot."},
                    {"role": "user", "content": prompt}
                ]
            )
            commentary = response['choices'][0]['message']['content'].strip()
            # Truncate the commentary to the first 2 sentences or 280 characters, whichever comes first
            commentary = '. '.join(commentary.split('. ')[:2])
            commentary = commentary[:280]
            return commentary
        except Exception as e:
            logging.error(f"Error getting dealer commentary: {e}")
            return ""
        
    def update_labels(self):
        self.player_label.text = f"Player's hand: {', '.join(str(card) for card in self.player_hand)}; Score: {', '.join(str(score) for score in self.player_score)}"
        self.dealer_label.text = f"Dealer's hand: {', '.join(str(card) for card in self.dealer_hand)}; Score: {self.dealer_score}"
        self.balance_label.text = f"Balance: ${self.balance}"
        self.dealer_commentary_label.text = self.get_dealer_commentary()
        self.end_game_label.text = ""  # Reset end game message


    

    def check_blackjack(self, hand):
        return len(hand) == 2 and sum(hand) == 21

    def deal(self, instance=None):
        # Disable Hit and Stand buttons at the start of a new hand
        self.hit_button.disabled = True
        self.stand_button.disabled = True  # This line is already present in your code
    

        if self.bet > self.balance:
            self.status = "Insufficient balance"
            return
        self.balance -= self.bet  
        self.player_hand = [self.draw_card() for _ in range(2)]
        self.dealer_hand = [self.draw_card()]  
        self.calculate_score()
        self.update_labels()
        if self.check_blackjack(self.player_hand):
            if self.check_blackjack(self.dealer_hand):
                self.status = "Both player and dealer have blackjack! It's a tie!"
                self.balance += self.bet
            else:
                self.status = "Player has blackjack! Player wins!"
                self.balance += 2.5 * self.bet
            self.display_end_game_message()  # Display end game message
        else:
            self.split_button.disabled = len(self.player_hand) != 2 or self.player_hand[0] != self.player_hand[1]
            self.double_down_button.disabled = len(self.player_hand) != 2
            self.hit_button.disabled = False  # Enable the "Hit" button
            self.stand_button.disabled = False  # Enable the "Stand" button

    def hit(self, instance=None):
        if isinstance(self.player_hand[0], list):
            self.player_hand[self.current_hand_index].append(self.draw_card())
        else:
            self.player_hand.append(self.draw_card())
        self.calculate_score()
        self.split_button.disabled = True
        self.double_down_button.disabled = True
        if any(score > 21 for score in self.player_score):
            self.status = "Player busts! Dealer wins!"
            self.update_labels()
            self.display_end_game_message()  # Display end game message
        else:
            self.update_labels()

    def split(self, instance):
        if len(self.player_hand) != 2 or self.player_hand[0] != self.player_hand[1]:
            print("Player can't split")
            return
        if self.bet > self.balance:
            print("Insufficient balance to split")
            return
        self.balance -= self.bet
        second_hand_card = self.player_hand.pop()
        self.player_hand = [self.player_hand, [second_hand_card]]
        self.current_hand_index = 0  # Start with the first hand after a split
        self.calculate_score()
        self.update_labels()

    def double_down(self, instance):
        if len(self.player_hand) != 2:
            print("Player can't double down")
            return
        if self.bet > self.balance:
            print("Insufficient balance to double down")
            return
        self.balance -= self.bet
        self.bet *= 2
        self.hit()
        self.stand()
    def stand(self, instance=None):
        if isinstance(self.player_hand[0], list) and self.current_hand_index < len(self.player_hand) - 1:
            # If there are still hands left to play after a split, move to the next hand
            self.current_hand_index += 1
            self.update_labels()
        else:
            # Dealer's turn
            while True:
                if len(self.dealer_hand) < 2 or self.dealer_score < 17:
                    self.dealer_hand.append(self.draw_card())
                    self.calculate_score()
                elif self.dealer_score == 17 and 11 in self.dealer_hand:
                    self.dealer_hand.append(self.draw_card())
                    self.calculate_score()
                else:
                    break
            self.update_labels()
            self.split_button.disabled = True
            self.double_down_button.disabled = True
            if self.check_blackjack(self.dealer_hand):
                self.status = "Dealer has blackjack! Dealer wins!"
            elif self.dealer_score > 21 or any(player_score > self.dealer_score for player_score in self.player_score):
                self.status = "Dealer busts! Player wins!"
                self.balance += 2 * self.bet
            elif any(player_score == self.dealer_score for player_score in self.player_score):
                self.status = "It's a tie!"
                self.balance += self.bet
            else:
                self.status = "Dealer wins!"
            
            if self.status == "Dealer wins!" and self.balance == 0:
                self.end_game_label.text = "GAME OVER!"  # Set the text of the end game message
            else:
                self.display_end_game_message()  # Display end game message

    
    def display_end_game_message(self):
        self.end_game_label.text = "Game Over!"  # Set the text of the end game message
        self.stand_button.disabled = True  # Disable the stand button
        # If the player's balance has run out, enable the new game button
        if self.balance == 0:
            self.new_game_button.disabled = False
    
    def new_game(self, instance=None):
            self.manager.transition.direction = "right"
            self.manager.current = "deposit"
            self.bet = 0
            self.player_hand = []
            self.dealer_hand = []
            self.player_score = []
            self.dealer_score = 0
            self.status = ""
            self.new_game_button.disabled = True  # Disable the new game button
            self.deal_button.disabled = False  # Enable the deal button
            self.update_labels()

            self.end_game_label.text = "Game Over!"  # Set the text of the end game message



def new_game(self, instance=None):
    # Reset the game
    self.balance = 1000  # Reset to a default balance
    self.bet = 0
    self.player_hand = []
    self.dealer_hand = []
    self.player_score = []
    self.dealer_score = 0
    self.status = ""
    self.new_game_button.disabled = True  # Disable the new game button
    self.deal_button.disabled = False  # Enable the deal button
    self.update_labels()

class DepositScreen(Screen):
    def __init__(self, **kwargs):
        super(DepositScreen, self).__init__(**kwargs)

        # Create a BoxLayout
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.title = Label(text="Welcome to Blackjack", font_size=24, color=[1, 1, 1, 1])  # white
        layout.add_widget(self.title)

        self.instructions = Label(text="Please select your deposit amount to get started.", font_size=16, color=ColorScheme.primary_light)
        layout.add_widget(self.instructions)

        # Create the dropdown
        dropdown = CustomDropDown()

        # Create the main button
        self.deposit_button = Button(text ='Select Deposit', size_hint = (None, None), size =(200, 44))
        self.deposit_button.bind(on_release=dropdown.open)

        # Bind the dropdown to the button
        dropdown.bind(on_select=lambda instance, x: setattr(self.deposit_button, 'text', x))

        layout.add_widget(self.deposit_button)

        self.next_button = TexturedButton(text="Next", font_size=18, color=ColorScheme.primary_light, background_color=ColorScheme.primary)
        self.next_button.bind(on_release=self.next)
        layout.add_widget(self.next_button)

        # Add the layout to the screen
        self.add_widget(layout)

    def next(self, instance):
        deposit_amount = int(self.deposit_button.text)
        self.manager.transition.direction = "left"
        self.manager.current = "bet"
        self.manager.get_screen("bet").deposit_amount = deposit_amount


class BetScreen(Screen):
    deposit_amount = NumericProperty(0)

    def __init__(self, **kwargs):
        super(BetScreen, self).__init__(**kwargs)

        # Create a BoxLayout
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.title = Label(text="Place Your Bet", font_size=24, color=[1, 1, 1, 1])  # white
        layout.add_widget(self.title)

        self.instructions = Label(text="Please select your bet amount. You have ${}".format(self.deposit_amount), font_size=16, color=ColorScheme.primary_light)
        layout.add_widget(self.instructions)

        # Create the dropdown
        dropdown = CustomDropDown()

        # Create the main button
        self.bet_button = Button(text ='Select Bet', size_hint = (None, None), size =(200, 44))
        self.bet_button.bind(on_release=dropdown.open)

        # Bind the dropdown to the button
        dropdown.bind(on_select=lambda instance, x: setattr(self.bet_button, 'text', x))

        layout.add_widget(self.bet_button)

        self.next_button = TexturedButton(text="Next", font_size=18, color=ColorScheme.primary_light, background_color=ColorScheme.primary)
        self.next_button.bind(on_release=self.next)
        layout.add_widget(self.next_button)

        # Add the layout to the screen
        self.add_widget(layout)

    def next(self, instance):
        bet_amount = int(self.bet_button.text)
        if bet_amount > self.deposit_amount:
            self.instructions.text = "Insufficient balance for this bet."
        else:
            self.manager.transition.direction = "left"
            self.manager.current = "blackjack"
            blackjack_screen = self.manager.get_screen("blackjack")
            blackjack_screen.balance = self.deposit_amount  # Set the balance
            blackjack_screen.bet = bet_amount  # Set the bet



if __name__ == "__main__":
    BlackjackApp().run()
