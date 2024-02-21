from datetime import timedelta
from random import choice, randrange
from re import findall, search
from urllib.parse import quote, unquote

import discord
from discord import app_commands
from discord.ext import commands
from scraper import scrape

import core
import db
import pagination


class Util(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.morse_dict = {
            'A': '.-',
            'B': '-...',
            'C': '-.-.',
            'D': '-..',
            'E': '.',
            'F': '..-.',
            'G': '--.',
            'H': '....',
            'I': '..',
            'J': '.---',
            'K': '-.-',
            'L': '.-..',
            'M': '--',
            'N': '-.',
            'Ñ': '--.--',
            'O': '---',
            'P': '.--.',
            'Q': '--.-',
            'R': '.-.',
            'S': '...',
            'T': '-',
            'U': '..-',
            'V': '...-',
            'W': '.--',
            'X': '-..-',
            'Y': '-.--',
            'Z': '--..',
            '1': '.----',
            '2': '..---',
            '3': '...--',
            '4': '....-',
            '5': '.....',
            '6': '-....',
            '7': '--...',
            '8': '---..',
            '9': '----.',
            '0': '-----',
            ',': '--..--',
            '.': '.-.-.-',
            '?': '..--..',
            '!': '--..--',
            '/': '-..-.',
            '-': '-....-',
            '(': '-.--.',
            ')': '-.--.-',
            '"': '.-..-.',
            ':': '---...',
            ';': '-.-.-.',
            "'": '.----.',
            '=': '-...-',
            '&': '.-...',
            '+': '.-.-.',
            '_': '..--.-',
            '$': '...-..-',
            '@': '.--.-.',
            ' ': '/',
        }

    # choose
    @app_commands.command()
    @app_commands.checks.cooldown(1, 3)
    @app_commands.rename(
        option1='opción1',
        option2='opción2',
        option3='opción3',
        option4='opción4',
        option5='opción5',
        option6='opción6',
        option7='opción7',
        option8='opción8',
        option9='opción9',
        option10='opción10',
    )
    async def choose(
        self,
        interaction: discord.Interaction,
        option1: str,
        option2: str,
        option3: str | None,
        option4: str | None,
        option5: str | None,
        option6: str | None,
        option7: str | None,
        option8: str | None,
        option9: str | None,
        option10: str | None,
    ):
        """Devuelve una de las opciones dadas"""
        options = [
            option1,
            option2,
            option3,
            option4,
            option5,
            option6,
            option7,
            option8,
            option9,
            option10,
        ]
        desc: str = choice(list(filter(lambda x: x is not None, options)))
        embed = discord.Embed(
            title='Mi elección es...',
            description=desc,
            colour=db.default_color(interaction),
        )
        await interaction.response.send_message(embed=embed)

    # poll
    @app_commands.command()
    @app_commands.checks.cooldown(1, 10)
    @app_commands.rename(
        description='descripción',
        option1='opción1',
        option2='opción2',
        option3='opción3',
        option4='opción4',
        option5='opción5',
        option6='opción6',
        option7='opción7',
        option8='opción8',
        option9='opción9',
        option10='opción10',
    )
    async def poll(
        self,
        interaction: discord.Interaction,
        description: app_commands.Range[str, 1, 256],
        option1: str,
        option2: str,
        option3: str | None,
        option4: str | None,
        option5: str | None,
        option6: str | None,
        option7: str | None,
        option8: str | None,
        option9: str | None,
        option10: str | None,
    ):
        """Crea encuestas de manera sencilla

        description
            Una pregunta, tema o afirmación que describa la encuesta
        """
        options = [
            option1,
            option2,
            option3,
            option4,
            option5,
            option6,
            option7,
            option8,
            option9,
            option10,
        ]
        emojis = [f'{number}\ufe0f\u20e3' for number in range(1, 10)] + [
            '\U0001f51f',
        ]
        display_options: list[str] = list(filter(lambda x: x is not None, options))
        desc = '\n'.join([
            f'{emojis[option]} {display_options[option]}' for option in range(len(display_options))
        ])

        embed = discord.Embed(
            title=description,
            description=desc,
            colour=db.default_color(interaction),
        ).set_author(
            name=f'Encuesta hecha por {interaction.user.name}',
            icon_url=interaction.user.display_avatar.url,
        )
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        for option in range(len(display_options)):
            await message.add_reaction(emojis[option])

    # avatar
    @app_commands.command()
    @app_commands.checks.cooldown(1, 3)
    async def avatar(
        self,
        interaction: discord.Interaction,
        user: discord.User | discord.Member | None,
    ):
        """Obtiene tú foto de perfil o la de otro usuario"""
        if user is None:
            user = interaction.user
        await interaction.response.send_message(
            embed=discord.Embed(
                title=f'Avatar de {str(user)}',
                colour=db.default_color(interaction),
            ).set_image(url=user.display_avatar.url),
        )

    # someone
    @app_commands.checks.cooldown(3, 10)
    @app_commands.command()
    @app_commands.rename(mention='mencionar')
    @app_commands.guild_only()
    async def someone(self, interaction: discord.Interaction, mention: bool = False):
        """Menciona a alguien aleatorio del servidor

        mention
            Determina si mencionar o no al usuario. Requiere permiso para hacer @everyone
        """
        assert (
            isinstance(interaction.user, discord.Member)
            and isinstance(interaction.guild, discord.Guild)
            and interaction.channel is not None
        )
        if mention and interaction.channel.permissions_for(interaction.user).mention_everyone:
            await interaction.response.send_message(choice(interaction.guild.members).mention)
        else:
            await interaction.response.send_message(str(choice(interaction.guild.members)))

    define_group = app_commands.Group(
        name='define',
        description='Busca el significado de una palabra en Wiktionary',
    )

    async def handle_define(self, interaction: discord.Interaction, query: str, lang: str):
        await interaction.response.defer()

        try:
            word = scrape(lang, lang, query)
        except FileNotFoundError:
            try:
                word = scrape(lang, lang, query.lower())
            except FileNotFoundError:
                word = None

        if word is None or not word['meanings']:
            await interaction.followup.send(core.Warning.error(f'Palabra no encontrada: `{query}`'))
            return

        def base_page() -> pagination.Page:
            return pagination.Page(embed=discord.Embed(
                title=query,
                colour=db.default_color(interaction),
            ).set_author(
                name='Wiktionary',
                icon_url=interaction.user.display_avatar.url,
            ))

        pages: list[pagination.Page] = []
        included_parts_of_speech: set[str] = set()
        curr_page = base_page()
        assert curr_page.embed is not None
        entry_count = 0

        # Slightly lower max lengths just to be safe
        max_embed_length = 5800
        max_field_length = 1000

        def add_field(embed: discord.Embed):
            name = meaning.get('part_of_speech', 'Unknown part of speech').capitalize()
            embed.add_field(
                name=name if name not in included_parts_of_speech else ' ',
                value=field_value,
                inline=False,
            )
            included_parts_of_speech.add(name)

        for meaning in word['meanings']:
            if not meaning['definitions']:
                continue

            if meaning['etymology']:
                field_value = meaning['etymology'] + '\n'
            else:
                field_value = ''

            for i, definition in enumerate(meaning['definitions'], start=1):
                entry = f'{i}. ' + definition['text']
                first_eol = entry.find('\n')
                if first_eol != -1:
                    entry = entry[:first_eol]
                entry += '\n'

                if len(curr_page.embed) + len(entry) + len(field_value) > max_embed_length:
                    add_field(curr_page.embed)
                    pages.append(curr_page)
                    curr_page = base_page()
                    assert curr_page.embed is not None
                    field_value = ''

                if len(field_value) + len(entry) + len(field_value) > max_field_length:
                    add_field(curr_page.embed)
                    field_value = ''

                entry_count += 1
                field_value += entry

            add_field(curr_page.embed)

        pages.append(curr_page)

        paginator = pagination.Paginator.optional(interaction, pages=pages, entries=entry_count)
        assert pages[0].embed is not None
        if isinstance(paginator, core.Missing):
            pages[0].embed.set_footer(text=f'{entry_count} resultados')
        await interaction.followup.send(embed=pages[0].embed, view=paginator)  # type: ignore

    # define spanish
    @app_commands.checks.cooldown(1, 10)
    @define_group.command(name='spanish')
    @app_commands.rename(query='búsqueda')
    async def define_spanish(
        self,
        interaction: discord.Interaction,
        query: app_commands.Range[str, 1, 256],
    ):
        """Busca el significado de una palabra en español en Wiktionary

        query
            Palabra en español
        """
        await self.handle_define(interaction, query, 'es')

    # define english
    @app_commands.checks.cooldown(1, 10)
    @define_group.command(name='english')
    @app_commands.rename(query='búsqueda')
    async def define_english(
        self,
        interaction: discord.Interaction,
        query: app_commands.Range[str, 1, 256],
    ):
        """Busca el significado de una palabra en inglés en Wiktionary

        query
            Palabra en inglés
        """
        await self.handle_define(interaction, query, 'en')

    # binary
    binary_group = app_commands.Group(
        name='binary',
        description='Codifica o decodifica código binario',
    )

    # binary encode
    @app_commands.checks.cooldown(1, 3)
    @binary_group.command(name='encode')
    @app_commands.rename(text='texto')
    async def binary_encode(self, interaction: discord.Interaction, text: str):
        """Convierte texto a código binario

        text
            El texto que será codificado
        """
        string = ' '.join(bin(ord(char)).split('b')[1].rjust(8, '0') for char in text)
        await interaction.response.send_message(f'```{string}```')

    # binary decode
    @app_commands.checks.cooldown(1, 3)
    @binary_group.command(name='decode')
    @app_commands.rename(text='texto')
    async def binary_decode(self, interaction: discord.Interaction, text: str):
        """Convierte código binario a texto

        text
            El texto que será decodificado
        """
        text = text.replace(' ', '')
        if search(r'[^0-1]', text):
            await interaction.response.send_message(
                core.Warning.error('El texto debe ser binario (unos y ceros)'),
                ephemeral=True,
            )
            return

        string = ' '.join(text[i:i+8] for i in range(0, len(text), 8))
        string = ''.join(chr(int(byte, base=2)) for byte in string.split(' '))
        ctx = await self.bot.get_context(interaction)
        content = f'```{await commands.clean_content().convert(ctx, string)}```'
        await interaction.response.send_message(content)

    # morse
    morse_group = app_commands.Group(name='morse', description='Codifica o decodifica código morse')

    # morse encode
    @app_commands.checks.cooldown(1, 3)
    @morse_group.command(name='encode')
    @app_commands.rename(text='texto')
    async def morse_encode(self, interaction: discord.Interaction, text: str):
        """Convierte texto a código morse

        text
            El texto que será codificado
        """
        string = ''
        text = text.upper()
        for letter in text:
            if letter in self.morse_dict:
                string += self.morse_dict[letter] + ' '

        content = (
            f'```{string}```'
            if string
            else core.Warning.error('Los caracteres especificados son incompatibles')
        )
        await interaction.response.send_message(content)

    # morse decode
    @app_commands.checks.cooldown(1, 3)
    @morse_group.command(name='decode')
    @app_commands.rename(text='texto')
    async def morse_decode(self, interaction: discord.Interaction, text: str):
        """Convierte código morse a texto

        text
            El texto que será decodificado
        """
        text += ' '
        string = ''
        citext = ''
        for letter in text:
            if letter != ' ':
                citext += letter
            else:
                if citext in list(self.morse_dict.values()):
                    string += list(self.morse_dict.keys())[
                        list(self.morse_dict.values()).index(citext)
                    ]
                citext = ''

        ctx = await self.bot.get_context(interaction)
        if string:
            content = '```{}```'.format(
                (await commands.clean_content().convert(ctx, string)).capitalize(),
            )
        else:
            content = core.Warning.error('Los caracteres especificados son incompatibles')
        await interaction.response.send_message(content)

    # percentencoding
    percent_group = app_commands.Group(
        name='percent-encoding',
        description='Codifica o decodifica código porcentaje o código URL',
    )

    # percentencoding encode
    @app_commands.checks.cooldown(1, 3)
    @percent_group.command(name='encode')
    @app_commands.rename(text='texto')
    async def percentencoding_encode(self, interaction: discord.Interaction, text: str):
        """Convierte texto a código porcentaje o código URL

        text
            El texto que será codificado
        """
        await interaction.response.send_message(f'```{quote(text)}```')

    # percentencoding decode
    @app_commands.checks.cooldown(1, 3)
    @percent_group.command(name='decode')
    @app_commands.rename(text='texto')
    async def percentencoding_decode(self, interaction: discord.Interaction, text: str):
        """Convierte código porcentaje o código URL a texto

        text
            El texto que será decodificado
        """
        ctx = await self.bot.get_context(interaction)
        content = f'```{await commands.clean_content().convert(ctx, unquote(text))}```'
        await interaction.response.send_message(content)

    # userinfo
    @app_commands.checks.cooldown(1, 5)
    @app_commands.command()
    @app_commands.rename(user='usuario')
    @app_commands.guild_only()
    async def userinfo(
        self,
        interaction: discord.Interaction,
        user: discord.Member | discord.User | None,
    ):
        """Obtiene información de un usuario. Habrá más información si el usuario se encuentra en
        el servidor
        """
        if user is None:
            user = interaction.user

        embed = discord.Embed(
            title='Información del usuario',
            colour=db.default_color(interaction),
        ).set_thumbnail(url=user.display_avatar.url)

        activity_descriptions = {
            discord.ActivityType.unknown: 'Desconocido ',
            discord.ActivityType.playing: 'Jugando a ',
            discord.ActivityType.streaming: 'Transmitiendo ',
            discord.ActivityType.listening: 'Escuchando ',
            discord.ActivityType.watching: 'Viendo ',
            discord.ActivityType.custom: '',
        }

        status_descriptions = {
            discord.Status.online: 'En linea',
            discord.Status.offline: 'Desconectado',
            discord.Status.idle: 'Ausente',
            discord.Status.dnd: 'No molestar',
        }

        user_type = 'Bot' if user.bot else 'Usuario'
        if user.system:
            user_type += ' del sistema'
        user_creation = core.fix_date(user.created_at, elapsed=True, newline=True)

        (
            embed.add_field(name='Usuario', value=str(user))
            .add_field(name='ID', value=user.id)
            .add_field(name='Tipo de cuenta', value=user_type, inline=False)
            .add_field(name='Fecha de creación de la cuenta', value=user_creation)
        )

        if isinstance(user, discord.Member):
            if user.nick:
                embed.insert_field_at(1, name='Apodo', value=user.nick)

            if user.joined_at is not None:
                joined_at = core.fix_date(user.joined_at, elapsed=True, newline=True)
                embed.add_field(name='Fecha de entrada al servidor', value=joined_at)

            if isinstance(interaction.channel, discord.abc.GuildChannel):
                permissions = interaction.channel.permissions_for(user)
                true_permissions = [f'`{perm}`' for perm, value in permissions if value]
                permission_list = ', '.join(true_permissions)
                perm_field_val = f'Integer: `{permissions.value}`\n{permission_list}'
                embed.add_field(name='Permisos en este canal', value=perm_field_val, inline=False)

            if user.premium_since is not None:
                boost_date = core.fix_date(user.premium_since, elapsed=True, newline=True)
                embed.add_field(name='Boosteando desde', value=boost_date)

            if user.activities:
                activity_list = [
                    f'- {custom}'
                    for custom in user.activities
                    if custom.type == discord.ActivityType.custom
                ] + [
                    f'- {activity_descriptions[activity.type]} **{activity.name}**'
                    for activity in user.activities
                ]
                embed.add_field(name='Actividades', value='\n'.join(activity_list))

            embed.add_field(name='Color', value=str(user.color))

            client_emojis = (
                (':desktop:', user.desktop_status),
                (':iphone:', user.mobile_status),
                (':globe_with_meridians:', user.web_status),
            )

            statuses = [
                f'{client} {status_descriptions[status]}'
                for client, status in client_emojis
            ]

            embed.add_field(name='Estados', value='\n'.join(statuses))

        await interaction.response.send_message(embed=embed)

    # roleinfo
    @app_commands.checks.cooldown(1, 3)
    @app_commands.command()
    @app_commands.rename(role='rol')
    @app_commands.guild_only()
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        """Obtiene información de un rol"""
        embed = discord.Embed(title='Información del rol', colour=db.default_color(interaction))

        (
            embed.add_field(name='Nombre', value=role.name)
            .add_field(name='Mención', value=role.mention)
            .add_field(name='ID', value=role.id)
        )

        if interaction.guild is not None:
            (
                embed.add_field(
                    name='Posición',
                    value=f'{role.position} de {len(interaction.guild.roles)-1}',
                ).add_field(
                    name='Cantidad de usuarios',
                    value=f'{len(role.members)} de {len(interaction.guild.members)}',
                )
            )

        (
            embed.add_field(name='Mencionable', value=core.bools[role.mentionable])
            .add_field(name='Aparece separado', value=core.bools[role.hoist])
            .add_field(name='Manejado por una integración', value=core.bools[role.managed])
            .add_field(name='Color', value=str(role.color))
            .add_field(
                name='Fecha de creación',
                value=core.fix_date(role.created_at, elapsed=True, newline=True),
            )
        )

        permissions = role.permissions
        perm_list = [f'`{perm}`' for perm, value in permissions if value]
        embed.add_field(
            name='Permisos',
            value=f'Integer: `{permissions.value}`\n{", ".join(perm_list)}',
            inline=False,
        )

        await interaction.response.send_message(embed=embed)

    # channelinfo
    @app_commands.checks.cooldown(1, 3)
    @app_commands.command()
    @app_commands.rename(channel='canal')
    @app_commands.guild_only()
    async def channelinfo(
        self,
        interaction: discord.Interaction,
        channel: discord.abc.GuildChannel | None,  # type: ignore
    ):
        """Obtiene la información de un canal de cualquier tipo o una categoría"""
        channel: (
            discord.abc.GuildChannel
            | discord.DMChannel
            | discord.GroupChannel
            | discord.Thread
            | None
        )

        embed = discord.Embed(title='Información del canal', colour=db.default_color(interaction))

        if channel is None:
            channel = interaction.channel

        if channel is None:
            await interaction.response.send_message(core.Warning.error('Canal inválido'))
            return

        if interaction.guild is None:
            await interaction.response.send_message(core.Warning.error('Servidore inválido'))
            return
        guild = interaction.guild

        if isinstance(channel, app_commands.AppCommandChannel):
            channel = await channel.fetch()

        if not channel.created_at:
            created_at = 'Desconocido'
        else:
            created_at = core.fix_date(channel.created_at, elapsed=True, newline=True)

        types = {
            discord.ChannelType.text: 'Canal de texto',
            discord.ChannelType.voice: 'Canal de voz',
            discord.ChannelType.private: 'Mensaje directo',
            discord.ChannelType.group: 'Grupo',  # This should be impossible
            discord.ChannelType.category: 'Categoría',
            discord.ChannelType.news: 'Canal de noticias',
            discord.ChannelType.stage_voice: 'Escenario',
            discord.ChannelType.news_thread: 'Hilo de noticias',
            discord.ChannelType.public_thread: 'Hilo público',
            discord.ChannelType.private_thread: 'Hilo privado',
            discord.ChannelType.forum: 'Foro',
        }

        (
            embed.add_field(name='Nombre', value=str(channel))
            .add_field(name='ID', value=channel.id)
            .add_field(name='Fecha de creación', value=created_at)
            .add_field(name='Tipo de canal', value=types[channel.type])
        )

        # Discord.py API is so dumb that I just have to spam type: ignore
        data_dict = {}

        if channel.type in (discord.ChannelType.text, discord.ChannelType.news):
            thread_hide = core.fix_delta(
                timedelta(minutes=channel.default_auto_archive_duration),  # type: ignore
                compact=False,
            )
            slowmode = core.fix_delta(
                timedelta(seconds=channel.slowmode_delay),  # type: ignore
                compact=False,
            )
            data_dict.update({
                'Posición': f'{channel.position+1} de {len(guild.text_channels)}',  # type: ignore
                'Categoría': channel.category,  # type: ignore
                'Cantidad de hilos activos': len(channel.threads),  # type: ignore
                'Hilos se ocultan después de:': thread_hide,
                'Tema': channel.topic,  # type: ignore
                'Slowmode': slowmode,
                'Miembros que pueden ver el canal':
                    f'{len(channel.members)} de {len(interaction.guild.members)}',  # type: ignore
                'Es NSFW': core.bools[channel.nsfw],  # type: ignore
            })

        elif channel.type in (
            discord.ChannelType.news_thread,
            discord.ChannelType.public_thread,
            discord.ChannelType.private_thread,
        ):
            slowmode = core.fix_delta(
                timedelta(seconds=channel.slowmode_delay),  # type: ignore
                compact=False,
            )
            data_dict.update({
                'Categoría': channel.category,  # type: ignore
                'Archivado': core.bools[channel.archived],  # type: ignore
                'Bloqueado': core.bools[channel.locked],  # type: ignore
                'Dueño': str(channel.owner),  # type: ignore
                'Canal principal': str(channel.parent),  # type: ignore
                'Slowmode': slowmode,
            })

        elif channel.type == discord.ChannelType.stage_voice:
            user_count = (
                (
                    f'{len(channel.members)} usuarios\n'  # type: ignore
                    f'{len(channel.speakers)} oradores\n'  # type: ignore
                    f'{len(channel.listeners)} oyentes\n'  # type: ignore
                    f'{len(channel.moderators)} moderadores\n'  # type: ignore
                    f'{len(channel.requesting_to_speak)} solicitudes para hablar'  # type: ignore
                )
                if channel.members  # type: ignore
                else None
            )  # type: ignore

            data_dict.update({
                'Posición': f'{channel.position+1} de {len(interaction.guild.stage_channels)}',
                'Categoría': channel.category,
                'Es NSFW': core.bools[channel.nsfw],  # type: ignore
                'Bitrate': f'{channel.bitrate//1000}kbps',  # type: ignore
                'Límite de usuarios': channel.user_limit  # type: ignore
                    if channel.user_limit != 0  # type: ignore
                    else 'Sin límite',
                'Cantidad de usuarios en el canal': user_count,
            })

        elif channel.type == discord.ChannelType.forum:
            thread_hide = core.fix_delta(
                timedelta(minutes=channel.default_auto_archive_duration),  # type: ignore
                compact=False,
            )
            layout = {
                discord.ForumLayoutType.not_set: 'Sin seleccionar',
                discord.ForumLayoutType.list_view: 'Vista de lista',
                discord.ForumLayoutType.gallery_view: 'Vista de galería',
            }[channel.default_layout]  # type: ignore

            data_dict.update({
                'Posición': f'{channel.position+1} de {len(interaction.guild.text_channels)}',
                'Categoría': channel.category,
                'Cantidad de hilos activos': len(channel.threads),  # type: ignore
                'Emoji de reacción por defecto': channel.default_reaction_emoji,  # type: ignore
                'Hilos se ocultan después de:': thread_hide,
                'Layout': layout,
                'Slowmode': core.fix_delta(
                    timedelta(seconds=channel.slowmode_delay),  # type: ignore
                    compact=False,
                ),
                'Es NSFW': core.bools[channel.nsfw],  # type: ignore
            })

        elif channel.type == discord.ChannelType.voice:
            if channel.members:  # type: ignore
                user_count = f'{len(channel.members)} de {len(interaction.guild.members)}'  # type: ignore
            else:
                user_count = None

            data_dict.update({
                'Posición': f'{channel.position+1} de {len(interaction.guild.voice_channels)}',
                'Categoría': channel.category,
                'Bitrate': f'{channel.bitrate//1000}kbps',  # type: ignore
                'Límite de usuarios': channel.user_limit  # type: ignore
                    if channel.user_limit != 0  # type: ignore
                    else 'Sin límite',
                'Cantidad de usuarios en el canal': user_count,
            })

        elif channel.type == discord.ChannelType.category:
            channel_count = (
                f'De texto: {len(channel.text_channels)}\n'  # type: ignore
                f'De voz: {len(channel.voice_channels)}\n'  # type: ignore
                f'Total: {len(channel.channels)}'  # type: ignore
            )

            data_dict.update({
                'Posición': f'{channel.position+1} de {len(interaction.guild.channels)}',
                'Es NSFW': core.bools[channel.nsfw],  # type: ignore
                'Cantidad de canales': channel_count,
            })

        embed = core.add_fields(embed, data_dict)
        await interaction.response.send_message(embed=embed)

    # serverinfo
    @app_commands.checks.cooldown(1, 3)
    @app_commands.command()
    @app_commands.guild_only()
    async def serverinfo(self, interaction: discord.Interaction):
        """Obtiene la información de este servidor"""
        guild = interaction.guild
        assert guild is not None

        embed = discord.Embed(
            title='Información del servidor',
            colour=db.default_color(interaction),
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        created_at = core.fix_date(guild.created_at, elapsed=True)
        afk_limit = core.fix_delta(timedelta(seconds=guild.afk_timeout), compact=False)

        if guild.afk_channel:
            afk_channel = guild.afk_channel.mention
        else:
            afk_channel = 'Ninguno'

        if guild.system_channel:
            system_channel = guild.system_channel.mention
        else:
            system_channel = 'Ninguno'

        mfa = core.bools[guild.mfa_level == discord.MFALevel.require_2fa]

        verification_level = {
            discord.VerificationLevel.none: 'Ninguno',
            discord.VerificationLevel.low:
                'Bajo: Los miembros deben tener un email verificado en su cuenta',
            discord.VerificationLevel.medium:
                'Medio: Los miembros deben tener un email verificado '
                'y estar registrados por más de 5 minutos',
            discord.VerificationLevel.high:
                'Alto: Los miembros deben tener un email verificado, estar registrados '
                'por más de 5 minutos y estar en el servidor por más de 10 minutos',
            discord.VerificationLevel.highest:
                'Muy alto: Los miembros deben tener un teléfono verificado en su cuenta',
        }[guild.verification_level]

        content_filter = {
            discord.ContentFilter.disabled: 'Deshabilitado',
            discord.ContentFilter.no_role:
                'Analizar el contenido multimedia de los miembros sin rol',
            discord.ContentFilter.all_members:
                'Analizar el contenido multimedia de todos los miembros',
        }[guild.explicit_content_filter]

        nsfw_level = {
            discord.NSFWLevel.default: 'Por defecto: El servidor aún no ha sido categorizado',
            discord.NSFWLevel.safe: 'Seguro: El servidor no tiene contenido NSFW',
            discord.NSFWLevel.explicit: 'Explícito: El servidor tiene contenido NSFW',
            discord.NSFWLevel.age_restricted:
                'Restringido por edad: El servidor podría tener contenido NSFW',
        }[guild.nsfw_level]

        features = ', '.join([f'`{feature}`' for feature in guild.features])

        channel_count = (
            f'De texto: {len(guild.text_channels)}\n'
            f'De voz: {len(guild.voice_channels)}\n'
            f'Escenarios: {len(guild.stage_channels)}\n'
            f'Foros: {len(guild.forums)}\n'
            f'Categorías: {len(guild.categories)}\n'
            f'Total: {len(guild.channels)}'
        )

        member_count = (
            f'Usuarios: {len(tuple(filter(lambda x: not x.bot, guild.members)))}\n'
            f'Bots: {len(tuple(filter(lambda x: x.bot, guild.members)))}\n'
            f'Total: {len(guild.members)}'
        )

        (
            embed.add_field(name='Nombre', value=guild.name)
            .add_field(name='ID', value=guild.id)
            .add_field(name='Fecha de creación', value=created_at, inline=False)
            .add_field(name='Límite AFK', value=afk_limit)
            .add_field(name='Canal AFK', value=afk_channel)
            .add_field(name='Canal de mensajes del sistema', value=system_channel)
            .add_field(name='Dueño', value=guild.owner.mention if guild.owner else 'Ninguno')
            .add_field(name='Límite de miembros', value=guild.max_members)
            .add_field(name='Descripción', value=guild.description)
            .add_field(name='Autenticación de 2 factores', value=mfa)
            .add_field(name='Nivel de verificación', value=verification_level, inline=False)
            .add_field(name='Filtro de contenido explícito', value=content_filter, inline=False)
            .add_field(name='Nivel NSFW', value=nsfw_level, inline=False)
            .add_field(name='Características', value=features, inline=False)
            .add_field(name='Cantidad de canales', value=channel_count)
            .add_field(name='Cantidad de miembros', value=member_count)
            .add_field(name='Cantidad de roles', value=len(guild.roles))
        )

        await interaction.response.send_message(embed=embed)

    # count
    @app_commands.checks.cooldown(1, 2)
    @app_commands.command()
    @app_commands.rename(to_count='contar', text='texto')
    async def count(self, interaction: discord.Interaction, text: str, to_count: str | None):
        """Cuenta cuantas veces hay una letra o palabra dentro de otro texto

        text
            El texto en el que buscar palabras o caracteres
        to_count
            Palabra que contar en el texto. Dejar vacío para contar cualquier palabra o carácter
        """
        embed = discord.Embed(title='Contador de palabras', colour=db.default_color(interaction))
        word = r'\w+'

        if to_count is None:
            count = len(text)
            (
                embed.add_field(name='Cantidad de caracteres', value=count)
                .add_field(name='Cantidad de palabras', value=len(findall(word, text)))
            )

        else:
            if to_count.startswith('"') and to_count.endswith('"'):
                to_count = to_count[1:-1]

            count = text.count(to_count)

            matching_chars = len(to_count) * count
            text_len = len(text)
            chars_percent = round(100 / (text_len / matching_chars), 4) if count > 0 else 0

            (
                embed.add_field(name='Término a contar', value=f'"{to_count}"', inline=False)
                .add_field(
                    name='Caracteres que coinciden',
                    value=f'{matching_chars} de {text_len}\n{chars_percent}%',
                )
            )

            if len(to_count) > 1:
                all_word_count = len(findall(word, text))
                word_percent = round(100 / (all_word_count / count), 4) if count > 0 else 0
                embed.add_field(
                    name='Palabras que coinciden',
                    value=f'{count} de {all_word_count}\n{word_percent}%',
                )

        await interaction.response.send_message(embed=embed)

    # randomnumber
    @app_commands.command()
    @app_commands.rename(start='mínimo', stop='máximo', step='salto')
    async def randomnumber(
        self,
        interaction: discord.Interaction,
        start: int,
        stop: int,
        step: app_commands.Range[int, 1] = 1,
    ):
        """Obtiene un número aleatorio entre el intervalo especificado. Puedes usar números
        negativos

        start
            Mínimo valor posible, se incluye en el rango
        stop
            Máximo valor posible, se excluye del rango
        step
            Distancia entre cada número del rango, el valor por defecto es 1
        """
        if start >= stop:
            await interaction.response.send_message(
                core.Warning.error(
                    'Intervalo inválido. Revisa que el primer número sea menor que el segundo',
                ),
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            embed=discord.Embed(
                title=f'Número aleatorio entre {start} y {stop}',
                description=str(randrange(start, stop, step)),
                colour=db.default_color(interaction),
            ),
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Util(bot), guilds=core.bot_guilds)  # type: ignore
