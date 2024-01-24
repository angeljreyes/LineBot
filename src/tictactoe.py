import asyncio
from random import choice
from typing import cast

import discord

import core


class JoinView(discord.ui.View):
    """View that allows other users to join a TTT game.

    JoinView.user is None is no user joined after timeout, and
    a discord.Member otherwise.
    """
    children: list[discord.ui.Button[discord.ui.View]] # type: ignore [no-redef]

    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.timeout = 180
        self._interaction = interaction
        self.user: discord.Member | None = None

    async def on_timeout(self):
        self.children[0].disabled = True
        await self._interaction.edit_original_response(view=self)

    @discord.ui.button(label='Unirse', emoji=u'\U0001f4e5', style=discord.ButtonStyle.blurple)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self._interaction.user:
            return
        self.user = cast(discord.Member, interaction.user)
        self.interaction = interaction
        button.disabled = True
        self.stop()


class TicTacToeButton(discord.ui.Button['TicTacToe']):
    """Each one of the 9 squares in the game as a Button."""
    def __init__(self, x: int, y: int):
        # A label is required, but we don't need one so a zero-width space is used
        # The row parameter tells the View which row to place the button under.
        # A View can only contain up to 5 rows -- each row can only have 5 buttons.
        # Since a Tic Tac Toe grid is 3x3 that means we have 3 rows and 3 columns.
        super().__init__(style=discord.ButtonStyle.grey, emoji=core.empty_emoji, row=y)
        self.x = x
        self.y = y

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.view is None:
            return False

        if interaction.user == self.view.players[self.view.current_player]:
            return True

        await interaction.response.defer()
        return False


    # This function is called whenever this particular button is pressed
    # This is part of the "meat" of the game logic
    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        await view.play(interaction, self.x, self.y)


# This is our actual board View
class TicTacToe(discord.ui.View):
    """Represents a TTT game."""
    # This tells the IDE or linter that all our children will be TicTacToeButtons
    # This is not required
    children: list[TicTacToeButton] # type: ignore [type-redef]
    X = -1
    O = 1
    Tie = 2

    def __init__(
            self,
            interaction: discord.Interaction,
            playerX: discord.abc.User,
            playerO: discord.abc.User
        ):
        super().__init__()
        self.interaction = interaction
        self.timeout = 90
        self.current_player = self.X
        self.playerX = playerX
        self.playerO = playerO
        self.players = {
            self.X: self.playerX,
            self.O: self.playerO
        }
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
        # Our board is made up of 3 by 3 TicTacToeButtons
        # The TicTacToeButton maintains the callbacks and helps steer
        # the actual game.
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    def get_content(self, status: str | None = None) -> str:
        """Return the content that shows info about the game.

        Status represents the current state of the game. If it is None,
        defaults to showing whose turn it is.
        """
        if status is None:
            status = f':timer: Turno de {self.players[self.current_player].mention}'
        return f'__**Tic Tac Toe**__\n:crossed_swords: **{self.playerX.name}** vs **{self.playerO.name}**\n{status}'

    def get_other_player(self, key: int | None = None) -> int:
        """Return the non-current player or the opposite of key."""
        if key is None:
            key = self.current_player
        return {self.X: self.O, self.O: self.X}[self.current_player]

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        self.stop()
        await self.interaction.edit_original_response(content=self.get_content(f':tada: **{self.players[self.current_player].name}** no realizo su jugada a tiempo. ¡**{self.players[self.get_other_player()].name}** ha ganado la partida!'), view=self)
    
    async def play(self, interaction: discord.Interaction, x: int, y: int) -> None:
        """Mark a square at the given coordinates.

        The square will be marked depending on the current player.
        """
        button = self.children[x*3 + y]
        button.style = {self.X: discord.ButtonStyle.blurple, self.O: discord.ButtonStyle.green}[self.current_player]
        button.emoji = {self.X: core.cross_emoji, self.O: core.circle_emoji}[self.current_player]
        button.disabled = True
        self.board[y][x] = self.current_player
        self.current_player = self.get_other_player()

        if self.players[self.current_player].bot:
            for child in self.children:
                child.disabled = True
        
        winner = self.check_board_winner()
        if winner is not None:
            if winner in (self.X, self.O):
                status = f':tada: ¡**{self.players[winner].name}** ha ganado la partida!'
            else:
                status = ':flag_white: La partida terminó en un empate'

            for child in self.children:
                child.disabled = True

            self.stop()
            if interaction.response.is_done():
                await interaction.edit_original_response(content=self.get_content(status), view=self)
            else:
                await interaction.response.edit_message(content=self.get_content(status), view=self)
            return

        if interaction.response.is_done():
            await interaction.edit_original_response(content=self.get_content(), view=self)
        else:
            await interaction.response.edit_message(content=self.get_content(), view=self)

        if self.current_player == self.O and self.players[self.O].bot:
            await asyncio.sleep(1.5)
            available_moves = [[x, y] if self.board[y][x] == 0 else None for x in range(3) for y in range(3)]
            available_moves_filtered = cast(
                list[list[int]],
                list(filter(lambda x: x is not None, available_moves))
            )
            button_x, button_y = choice(available_moves_filtered)
            for child in self.children:
                if self.board[child.y][child.x] not in (self.X, self.O):
                    child.disabled = False
            await self.play(interaction, button_x, button_y)

    # This method checks for the board winner -- it is used by the TicTacToeButton
    def check_board_winner(self) -> int | None:
        """Check if there is a winner and return it."""
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None
