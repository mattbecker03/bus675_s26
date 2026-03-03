"""
Lab 1: Text-Based Adventure RPG
================================
YOUR NAME HERE

Build your game here! This file contains all the starter code from the lab notebook.
Fill in the TODOs, add your own classes, and make it your own.

Run with: python game.py
"""

import random


# =============================================================================
# Dice Utilities
# =============================================================================

def roll_d20():
    """Roll a 20-sided die."""
    return random.randint(1, 20)

def roll_dice(num_dice, sides):
    """Roll multiple dice and return the total. E.g., roll_dice(2, 6) for 2d6."""
    return sum(random.randint(1, sides) for _ in range(num_dice))


class Character:
    """Base class for all characters in the game."""
    
    def __init__(self, name, health, max_health, strength, defense):
        # TODO: Initialize attributes
        self.name = name
        self.health = health
        self.max_health = max_health
        self.strength = strength
        self.defense = defense
        pass
    
    def is_alive(self):
        self.alive = True
        return True if self.health > 0 else False
        pass
    
    def take_damage(self, amount):
        # TODO: Reduce health, but don't go below 0
        self.health -= amount
        
        if self.health < 0:
            self.health = 0
        print(f"{self.name} took {amount} damage! HP: {self.health} \n")
        if self.health == 0:
            print(f"{self.name} died")
            # Print a message about the damage taken
    
    def attack(self, target):
         # 1. Roll d20, add strength
        roll = roll_d20()
        total = roll + self.strength
        print(f"{self.name} rolled a {roll} + {self.strength} = {total}")
        # 2. Compare to target's defense
        if total > target.defense:
            damage = (total - target.defense)
            print(f"Hit! Dealt {damage} damage to {target.name}")
            # 3. If hit, deal damage to target
            target.take_damage(damage)
        else:
            # 4. Print combat messages!
            print(f"Missed! {target.name} defended against the attack.")
        pass
    
    def __str__(self):
        return f"{self.name} (HP: {self.health}/{self.max_health})"
# YOUR CODE: Build Player and Enemy classes here

class Player(Character):
    """The player character."""
    
    def __init__(self, name):
        self.name = name
        # TODO: Call parent __init__ with appropriate starting stats
        super().__init__(name, health=10, max_health=10, strength=5, defense=10)
        # TODO: Initialize inventory as empty list
        self.inventory = []
        pass
    
    def pick_up(self, item):
        self.inventory.append(item)
        print(f"Picked up {item}")

    def use_item(self, item):
        print("Use an item from inventory by name.")
        target_name = item.lower().strip()

        for item in self.inventory:
            if item.lower() != target_name:
                continue

            if item == "Health Potion":
                self.max_health += 10
                self.health = min(self.max_health, self.health + 20)
                self.inventory.remove(item)
                print(
                    f"{self.name} used {item}: +20 health, +10 max health "
                    f"({self.health}/{self.max_health} HP)."
                )
                return True

            if item == "Strength Potion":
                self.strength += 10
                self.inventory.remove(item)
                print(f"{self.name} used {item}: +10 strength (STR: {self.strength}).")
                return True
            
            if item == "Shield":
                self.defense += 10
                self.inventory.remove(item)
                print(f"{self.name} used {item}: +10 defense (DEF: {self.defense}).")
                return True

            print(f"{item} can't be used right now.")
            return False

        print(f"{item} is not in your inventory.")
        return False

    
    def show_inventory(self):
        if self.inventory:
            print(f"Inventory of {self.name}: {', '.join(self.inventory)}")
        else:
            print(f"{self.name} has no items in inventory.")
        pass


class Enemy(Character):
    """Base class for enemies."""
    
    def __init__(self, name, health, max_health, strength, defense, xp_value=10):
        # TODO: Call parent __init__
        # TODO: Set xp_value
        super().__init__(name, health, max_health, strength, defense)
        self.xp_value = xp_value
        pass


# TODO: Create specific enemy types (Minion, Elite, Boss)
# Example:
# class Goblin(Enemy):
#     def __init__(self):
#         super().__init__("Goblin", health=15, strength=3, defense=8, xp_value=5)

class Tree_Spirit(Enemy):
    def __init__(self):
        super().__init__("Tree Spirit", health=20, max_health=20, strength=0, defense=0, xp_value=10)

class Knights_Calvary(Enemy):
    def __init__(self):
        super().__init__("Knights Calvary", health=25, max_health=25, strength=0, defense=0, xp_value=20)

class Magma_Wyrm(Enemy):
    def __init__(self):
        super().__init__("Magma Wyrm", health=30, max_health=30, strength=0, defense=0, xp_value=40)

class margit(Enemy):
    def __init__(self):
        super().__init__("Margit", health=50, max_health=50, strength=4, defense=10, xp_value=100)

class Commander_ONeil(Enemy):
    def __init__(self):
        super().__init__("Commander O'Neil", health=60, max_health=60, strength=20, defense=25, xp_value=200)

class Ancient_Dragon_Lansseax(Enemy):
    def __init__(self):
        super().__init__("Ancient Dragon Lansseax", health=100, max_health=100, strength=30, defense=30, xp_value=400)



# =============================================================================
# Location Class
# =============================================================================
# YOUR CODE: Create your game world

# YOUR CODE: Build the Location class

class Location:
    """New Area Discovered"""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.connections = {}  # {"north": Location, "south": Location, etc.}
        self.enemies = []      # List of enemies in this location
        self.items = []        # List of items in this location
    
    def describe(self):
        """located in the southwest of the Lands Between"""
        print(f"\n{'='*50}")
        print(f"📍 {self.name}")
        print(f"{'='*50}")
        print(self.description)
        
        # TODO: Show enemies if present
        if self.enemies:
            print("Enemies present:")
            for enemy in self.enemies:
                print(f"  - {enemy.name}")
        
        # TODO: Show items if present
        if self.items:
            print("Items present:")
            for item in self.items:
                print(f"  - {item}")
        
        # TODO: Show available exits
        exits = self.get_exits()
        if exits:
            print("Available exits:")
            for direction in exits:
                print(f"  - {direction}")
    
    def get_exits(self):
        """Return a list of available directions."""
        return list(self.connections.keys())
    
    def add_connection(self, direction, location):
        """Connect this location to another."""
        self.connections[direction] = location

# =============================================================================
# World Builder
# =============================================================================

def create_world():
    """Create and connect all locations. Returns the starting location."""
    
    # Create locations
    limgrave = Location(
        "Limgrave",
        "Lush, temperate, and expansive opening region of Elden Ring, located in the southwest of the Lands Between"
    )
    stormveil = Location(
        "Stormveil Boss",
        "The first major stronghold in Elden Ring, located in the north of Limgrave"
    )
    caelid = Location(
        "Caelid",
        "A scarlet rot infested region east of Limgrave with dangerous enemies"
    )
    redmane_castle = Location(
        "Redmane Castle Boss",
        "An intermediate stronghold located in Caelid"
    )
    altus_plateau = Location(
        "Altus Plateau",
        "A more advanced region with powerful enemies and valuable loot"
    )
    volcano_manor = Location(
        "Volcano Manor Final Boss",
        "The final stronghold where the Ancient Dragon awaits"
    )
    Round_Table_hold = Location(
        "Round Table Hold",
        "A secure, non-combat hub realm existing outside the main map, serving as a sanctuary for Tarnished seeking to become Elden Lord"
    )
    Liurnia = Location(
        "Liurnia",
        "A region of the Lands Between with a mix of forests and open plains"
    )
    Cathedrial_of_Dragon_Communion = Location(
        "Cathedral of Dragon Communion",
        "A sacred place where the Tarnished can commune with dragons"
    )
    Mountain_top_of_the_Giants = Location(
        "Mountain Top of the Giants",
        "A snowy, mountainous region where the giants reside"
    )

    # Connect locations (both directions)
    limgrave.add_connection("south", stormveil)
    limgrave.add_connection("east", Round_Table_hold)


    Round_Table_hold.add_connection("west", limgrave)
    

    stormveil.add_connection("north", limgrave)
    stormveil.add_connection("east", caelid)
    stormveil.add_connection("west", Liurnia)

    Liurnia.add_connection("east", stormveil)

    caelid.add_connection("west", stormveil)
    caelid.add_connection("south", redmane_castle)
    caelid.add_connection("east", Cathedrial_of_Dragon_Communion)

    Cathedrial_of_Dragon_Communion.add_connection("west", caelid)

    redmane_castle.add_connection("north", caelid)
    redmane_castle.add_connection("south", altus_plateau)

    altus_plateau.add_connection("north", redmane_castle)
    altus_plateau.add_connection("south", volcano_manor)
    altus_plateau.add_connection("east", Mountain_top_of_the_Giants)

    Mountain_top_of_the_Giants.add_connection("west", altus_plateau)

    volcano_manor.add_connection("north", altus_plateau)
    
    # Add enemies to locations
    limgrave.enemies = [Tree_Spirit(), Tree_Spirit()]
    stormveil.enemies = [margit()]
    caelid.enemies = [Knights_Calvary(), Knights_Calvary()]
    redmane_castle.enemies = [Commander_ONeil()]
    altus_plateau.enemies = [Magma_Wyrm(), Magma_Wyrm()]
    volcano_manor.enemies = [Ancient_Dragon_Lansseax()]
    
    # TODO: Add items to locations (optional)
    limgrave.items = ["Strength Potion"]

    Round_Table_hold.items = ["Health Potion"]

    stormveil.items = ["Health Potion"]

    Liurnia.items = ["Shield"]

    caelid.items = []

    Cathedrial_of_Dragon_Communion.items = ["Health Potion", "Strength Potion"]

    redmane_castle.items = ["Health Potion", "Shield"]

    altus_plateau.items = ["Strength Potion"]

    Mountain_top_of_the_Giants.items = ["Health Potion"]
   
    volcano_manor.items = ["Health Potion"]

    
    # Return the starting location
    return limgrave

# Test your world
# starting_location = create_world()
# starting_location.describe()
# =============================================================================
# Combat System
# =============================================================================
# YOUR CODE: Implement the combat system

class Combat:
    """Manages turn-based combat between player and enemy."""
    
    # Combat states
    PLAYER_TURN = "player_turn"
    ENEMY_TURN = "enemy_turn"
    COMBAT_END = "combat_end"
    
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.state = Combat.PLAYER_TURN
        self.combat_log = []
    
    def start(self):
        """Begin combat and run until someone wins/loses/flees."""
        print(f"\n⚔️ COMBAT BEGINS! ⚔️")
        print(f"{self.player.name} vs {self.enemy.name}!")
        
        while self.state != Combat.COMBAT_END:
            if self.state == Combat.PLAYER_TURN:
                self.player_turn()
            elif self.state == Combat.ENEMY_TURN:
                self.enemy_turn()
        
        return self.get_result()
    
    def player_turn(self):
        """Handle player's turn in combat."""
        print(f"\n{self.player} | {self.enemy}")
        print("What do you do? (attack / run)")
        
        action = input("> ").lower().strip()
        
        if action == "attack":
            self.player.attack(self.enemy)
            if not self.enemy.is_alive():
                print(f"\n🎉 {self.enemy.name} has been defeated!")
                self.state = Combat.COMBAT_END
            else:
                self.state = Combat.ENEMY_TURN
        
        elif action == "run":
            # 50% chance to escape
            if random.random() < 0.5:
                print("You successfully fled!")
                self.state = Combat.COMBAT_END
            else:
                print("Couldn't escape!")
                self.state = Combat.ENEMY_TURN
        
        else:
            print("Invalid action. Try 'attack' or 'run'.")
    
    def enemy_turn(self):
        """Handle enemy's turn in combat."""
        print(f"\n{self.enemy.name}'s turn...")
        self.enemy.attack(self.player)
        
        if not self.player.is_alive():
            print(f"\n💀 {self.player.name} has fallen!")
            self.state = Combat.COMBAT_END
        else:
            self.state = Combat.PLAYER_TURN
    
    def get_result(self):
        """Return the combat result: 'victory', 'defeat', or 'fled'."""
        if not self.enemy.is_alive():
            return "victory"
        elif not self.player.is_alive():
            return "defeat"
        else:
            return "fled"


# =============================================================================
# Main Game Class
# =============================================================================

# YOUR CODE: Build the main Game class

class Game:
    """Main game controller."""
    
    # Game states
    EXPLORING = "exploring"
    IN_COMBAT = "in_combat"
    GAME_OVER = "game_over"
    VICTORY = "victory"
    FINAL_BOSS_NAME = "Ancient Dragon Lansseax"
    
    def __init__(self):
        self.player = None
        self.current_location = None
        self.state = Game.EXPLORING
        self.game_running = True
    
    def start(self):
        """Initialize and start the game."""
        self.show_intro()
        self.create_player()
        self.current_location = create_world()  # Your function from earlier
        self.current_location.describe()
        
        # Main game loop
        while self.game_running:
            if self.state == Game.EXPLORING:
                self.exploration_loop()
            elif self.state == Game.GAME_OVER:
                self.show_game_over()
                break
            elif self.state == Game.VICTORY:
                self.show_victory()
                break
    
    def show_intro(self):
        """Display the game introduction."""
        print("\n" + "="*60)
        print("         YOUR GAME TITLE HERE")
        print("="*60)
        print("\nYour epic intro text goes here...")
        print("Set the scene! What's happening? Why is the player here?")
        print("\n" + "="*60)
    
    def create_player(self):
        """Create the player character."""
        print("\nWhat is your name, adventurer?")
        name = input("> ")
        self.player = Player(name)
        print(f"\nWelcome, {name}! Your adventure begins...")
    
    def exploration_loop(self):
        """Handle player input during exploration."""
        print("\nWhat do you do? (type 'help' for commands)")
        command = input("> ").lower().strip()
        
        # Parse the command
        parts = command.split()
        if not parts:
            return
        
        action = parts[0]
        
        if action == "help":
            self.show_help()
        
        elif action == "look":
            self.current_location.describe()
        
        elif action == "go" and len(parts) > 1:
            direction = parts[1]
            self.move(direction)
        
        elif action in ["north", "south", "east", "west", "up", "down"]:
            self.move(action)
        
        elif action in ["fight", "attack"]:
            self.initiate_combat()
        
        elif action in ["inventory", "i"]:
            self.player.show_inventory()

        elif action in ["loot", "pickup", "pick", "take"] and len(parts) > 1:
            item_name = " ".join(parts[1:])
            self.pick_up_item(item_name)

        elif action == "use" and len(parts) > 1:
            item_name = " ".join(parts[1:])
            self.player.use_item(item_name)
        
        elif action == "quit":
            print("Thanks for playing!")
            self.game_running = False
        
        else:
            print("I don't understand that command. Type 'help' for options.")
    
    def move(self, direction):
        """Move the player in the specified direction."""
        if direction in self.current_location.connections:
            self.current_location = self.current_location.connections[direction]
            self.current_location.describe()
            # TODO: Check for automatic combat triggers?
        else:
            print(f"You can't go {direction} from here.")

    def pick_up_item(self, item_name):
        """Pick up an item from the current location by name."""
        normalized = item_name.lower().strip()
        for item in list(self.current_location.items):
            if item.lower() == normalized:
                self.player.pick_up(item)
                self.current_location.items.remove(item)
                return
        print(f"There is no '{item_name}' here.")

    
    def initiate_combat(self):
        """Start combat with an enemy in the current location."""
        if not self.current_location.enemies:
            print("There's nothing to fight here.")
            return
        
        enemy = self.current_location.enemies[0]  # Fight first enemy
        battle = Combat(self.player, enemy)
        result = battle.start()
        
        if result == "victory":
            self.current_location.enemies.remove(enemy)
            # TODO: Check for victory condition (e.g., boss defeated)
            if enemy.name == Game.FINAL_BOSS_NAME and not enemy.is_alive():
                self.state = Game.VICTORY

        elif result == "defeat":
            self.state = Game.GAME_OVER
    
    def show_help(self):
        """Display available commands."""
        print("\n📜 AVAILABLE COMMANDS:")
        print("  go [direction] - Move in a direction (north, south, east, west)")
        print("  look          - Examine your surroundings")
        print("  fight         - Attack an enemy in this location")
        print("  inventory     - Check your inventory")
        print("  loot [item]   - Pick up an item from the location")
        print("  use [item]    - Use an item from your inventory")
        print("  help          - Show this help message")
        print("  quit          - Exit the game")



    
    def show_game_over(self):
        """Display game over message."""
        print("\n" + "="*60)
        print("                    GAME OVER")
        print("="*60)
        print("\nYou have fallen. The adventure ends here...")
        print("\n(But you can always try again!)")
    
    def show_victory(self):
        """Display victory message."""
        print("\n" + "="*60)
        print("                    🎉 VICTORY! 🎉")
        print("="*60)
        print("\nCongratulations! You have completed your quest!")
        # TODO: Add your custom victory text


# =============================================================================
# Run the Game
# =============================================================================

if __name__ == "__main__":
    game = Game()
    game.start()
