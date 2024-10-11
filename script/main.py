from javascript import require, On, off
from simple_chalk import chalk
from utils_p.vec3_conversion import vec3_to_str

# Requires ./utils_p/vec3_conversion.py

# Import the javascript libraries
mineflayer = require("mineflayer")
mineflayer_pathfinder = require("mineflayer-pathfinder")
vec3 = require("vec3")

# Global bot parameters
server_host = "localhost"
server_port = 50450
reconnect = True


class MCBot:

    def __init__(self, bot_name):
        self.bot_args = {
            "host": server_host,
            "port": server_port,
            "username": bot_name,
            "hideErrors": False,
        }
        self.reconnect = reconnect
        self.bot_name = bot_name
        self.start_bot()

    # Tags bot username before console messages
    def log(self, message):
        print(f"[{self.bot.username}] {message}")


    def pathfind_to_goal(self, goal_location):
        try:
            self.bot.pathfinder.setGoal(
                mineflayer_pathfinder.pathfinder.goals.GoalNear(
                    goal_location["x"], goal_location["y"], goal_location["z"], 1
                )
            )

        except Exception as e:
            self.log(f"Error while trying to run pathfind_to_goal: {e}")

    # Start mineflayer bot
    def start_bot(self):
        self.bot = mineflayer.createBot(self.bot_args)
        self.bot.loadPlugin(mineflayer_pathfinder.pathfinder)

        self.start_events()

    # Attach mineflayer events to bot
    def start_events(self):

        # Login event: Triggers on bot login
        @On(self.bot, "login")
        def login(this):
            self.bot_socket = self.bot._client.socket
            self.log(
                chalk.green(
                    f"Logged in to {self.bot_socket.server if self.bot_socket.server else self.bot_socket._host }"
                )
            )

        # Spawn event: Triggers on bot entity spawn
        @On(self.bot, "spawn")
        def spawn(this):
            self.bot.chat("Bot logged!")

        # Kicked event: Triggers on kick from server
        @On(self.bot, "kicked")
        def kicked(this, reason, loggedIn):
            if loggedIn:
                self.log(chalk.redBright(f"Kicked whilst trying to connect: {reason}"))

        # Chat event: Triggers on chat message

        @On(self.bot, "messagestr")
        def messagestr(this, message, messagePosition, jsonMsg, sender, verified=None):
            if messagePosition == "chat":
                # Обработка команды "move to"
                if message.startswith("move"):
                    coords = message.split(" ")
                    if len(coords) == 4:  # Ожидаем "move to x y z"
                        try:
                            x = float(coords[1])
                            y = float(coords[2])
                            z = float(coords[3])
                            goal_location = {"x": x, "y": y, "z": z}
                            self.log(chalk.magenta(f"Pathfinding to coordinates {goal_location}"))
                            self.pathfind_to_goal(goal_location)

                            # Move the bot to the specified coordinates
                            self.bot.setControlState("forward", False)
                            self.bot.setControlState("back", False)
                            self.bot.setControlState("left", False)
                            self.bot.setControlState("right", False)
                            self.bot.setControlState("jump", False)
                            self.bot.setControlState("sprint", False)
                            self.bot.setControlState("dig", False)
                            self.bot.setControlState("place", False)
                            self.bot.lookAt(x, y, z, True)  # Fixed: Added True
                            self.bot.move(x, y, z)
                        except ValueError:
                            self.bot.chat("Invalid coordinates provided! Please use numbers.")
                    else:
                        self.bot.chat("Please provide exactly three coordinates: x, y, and z.")

                # Обработка команды "come to me"
                elif "come to me" in message:
                    # ...
                    player_location = self.bot.entity.position  # Assuming self.bot.entity.position exists
                    self.bot.lookAt(player_location.x, player_location.y, player_location.z, True)  # Fixed: Added True
                    self.bot.move(player_location.x, player_location.y, player_location.z)
        # End event: Triggers on disconnect from server
        @On(self.bot, "end")
        def end(this, reason):
            self.log(chalk.red(f"Disconnected: {reason}"))

            # Turn off old events
            off(self.bot, "login", login)
            off(self.bot, "spawn", spawn)
            off(self.bot, "kicked", kicked)
            off(self.bot, "messagestr", messagestr)

            # Reconnect
            if self.reconnect:
                self.log(chalk.cyanBright(f"Attempting to reconnect"))
                self.start_bot()

            # Last event listener
            off(self.bot, "end", end)


# Run function that starts the bot(s)
bot = MCBot("pathfinder-bot")