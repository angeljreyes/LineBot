import discord
import core
import db

class Page:
	__slots__ = ('content', 'embed')

	def __init__(self, content: str=None, *, embed: discord.Embed=None):
		self.content = content
		self.embed = embed

	@staticmethod
	def from_list(interaction, title:str, iterable: list, *, colour=None):
		formated = []
		count = 0
		if colour == None:
			colour = db.default_color(interaction)
		for i in iterable:
			count += 1
			formated.append(f'{count}. {i}')

		pages = []
		for i in range(int((len(formated) - 1)//20 + 1)):
			pages.append(Page(embed=discord.Embed(
				title=title,
				description='\n'.join(formated[i*20:i*20+20]),
				colour=colour
			)))
		return pages



class Paginator(discord.ui.View):
	def __init__(self, interaction:discord.Interaction, *, pages:list=[], entries:int=None, timeout:float=180.0):
		super().__init__(timeout=timeout)
		self.interaction = interaction
		self.page_num = 1
		self.page = None
		self.pages = []
		self.entries = entries
		self.add_pages(pages)


	def add_pages(self, pages:list):
		count = 0
		for page in pages:
			count += 1
			if page.embed != None:
				page.embed.set_footer(text=(f'Página {len(self.pages)+count} de {len(pages) + len(self.pages)}' if len(self.pages)+len(pages) > 1 else '') + f'{(str(" ("+str(self.entries)+" resultados)")) if self.entries != None else ""}' + (f' | {page.embed.footer.text}' if page.embed.footer.text != None else ""))
		self.pages += pages


	async def interaction_check(self, interaction: discord.Interaction):
		return self.interaction.user.id == interaction.user.id


	@discord.ui.button(emoji=core.first_emoji, style=discord.ButtonStyle.blurple, disabled=True)
	async def first(self, interaction: discord.Interaction, button: discord.ui.Button):
		await self.set_page(interaction, button, 1)

	@discord.ui.button(emoji=core.back_emoji, style=discord.ButtonStyle.blurple, disabled=True)
	async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
		await self.set_page(interaction, button, self.page_num - 1)

	@discord.ui.button(emoji=core.next_emoji, style=discord.ButtonStyle.blurple)
	async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
		await self.set_page(interaction, button, self.page_num + 1)

	@discord.ui.button(emoji=core.last_emoji, style=discord.ButtonStyle.blurple)
	async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
		await self.set_page(interaction, button, len(self.pages))

	@discord.ui.button(emoji=core.search_emoji, style=discord.ButtonStyle.blurple)
	async def search(self, interaction: discord.Interaction, button: discord.ui.Button):
		total_pages = len(self.pages)

		class SearchModal(discord.ui.Modal, title='Escribe un número de página'):
			answer = discord.ui.TextInput(
				label=f'Escribe un número de página (1-{total_pages})',
				required=True,
				min_length=1,
				max_length=len(str(total_pages))
			)

		async def on_submit(modal):
			async def func(interaction: discord.Interaction):
				try:
					value = int(modal.answer.value)
					if 0 < value <= total_pages:
						await self.set_page(interaction, button, value)
					else:
						await interaction.response.send_message(core.Warning.error(f'Escribe un número entre el 1 y el {total_pages}'), ephemeral=True)
				except ValueError:
					await interaction.response.send_message(core.Warning.error('Valor incorrecto. Escribe un número'), ephemeral=True)
			return func

		modal = SearchModal()
		modal.timeout = self.timeout
		modal.on_submit = await on_submit(modal)
		await interaction.response.send_modal(modal)

	
	async def on_timeout(self):
		self.children[0].disabled = True
		self.children[1].disabled = True
		self.children[2].disabled = True
		self.children[3].disabled = True
		self.children[4].disabled = True
		await self.interaction.edit_original_response(view=self)


	async def set_page(self, interaction:discord.Interaction, button:discord.ui.Button, page:int, interact=True):
		self.page = self.pages[page-1]
		self.page_num = page
		self.children[0].disabled = self.page_num == 1
		self.children[1].disabled = self.page_num == 1
		self.children[2].disabled = self.page_num == len(self.pages)
		self.children[3].disabled = self.page_num == len(self.pages)
		await interaction.response.defer()
		await self.interaction.edit_original_response(content=self.page.content, embed=self.page.embed, view=self)

