from javascript import require, On, Once, AsyncTask, once, off
from simple_chalk import chalk
from utils_p.vec3_conversion import vec3_to_str

# Requires ./utils/vec3_to_str.py

# Import the javascript libraries
mineflayer = require("mineflayer")
vec3 = require("vec3")

# Global bot parameters
server_host = "localhost"
server_port = 3000
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

    # Start mineflayer bot
    def start_bot(self):
        self.bot = mineflayer.createBot(self.bot_args)

        self.start_events()

    # Mineflayer: Run and jump
    def run_and_jump(self):
        try:

            @AsyncTask(start=True)
            def async_run_and_jump(task):
                self.bot.setControlState("forward", True)
                self.bot.waitForTicks(1)
                self.bot.setControlState("sprint", True)
                self.bot.setControlState("jump", True)
                self.bot.waitForTicks(11)
                self.bot.clearControlStates()

        except Exception as e:
            bot.chat(f"Error while trying to run run_and_jump: {e}")

    # Attach mineflayer events to bot
    def start_events(self):

        # Login event: Triggers on bot login
        @On(self.bot, "login")
        def login(this):

            # Displays which server you are currently connected to
            self.bot_socket = self.bot._client.socket
            self.log(
                chalk.green(
                    f"Logged in to {self.bot_socket.server if self.bot_socket.server else self.bot_socket._host }"
                )
            )

        # Spawn event: Triggers on bot entity spawn
        @On(self.bot, "spawn")
        def spawn(this):
            self.bot.chat("Hi!")

        # Kicked event: Triggers on kick from server
        @On(self.bot, "kicked")
        def kicked(this, reason, loggedIn):
            if loggedIn:
                self.log(chalk.redBright(f"Kicked whilst trying to connect: {reason}"))

        # Chat event: Triggers on chat message
        @On(self.bot, "messagestr")
        def messagestr(this, message, messagePosition, jsonMsg, sender, verified=None):
            if messagePosition == "chat":
                if "quit" in message:
                    self.bot.chat("Goodbye!")
                    self.reconnect = False
                    this.quit()
                elif "look at me" in message:

                    # Find all nearby players
                    local_players = self.bot.players

                    # Search for our specific player
                    for el in local_players:
                        player_data = local_players[el]
                        if player_data["uuid"] == sender:
                            vec3_temp = local_players[el].entity.position
                            player_location = vec3(
                                vec3_temp["x"], vec3_temp["y"] + 1, vec3_temp["z"]
                            )

                    # Feedback
                    if player_location:
                        self.log(chalk.magenta(vec3_to_str(player_location)))
                        self.bot.lookAt(player_location)
                        self.run_and_jump()
                    else:
                        self.log(f"Player not found.")

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
bot = MCBot("jumper-bot")