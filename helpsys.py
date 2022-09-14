import discord, asyncio, botdata


descs = {
	'ping': 'Muestra lo que tarda el bot en enviar un mensaje desde que mandaste el comando en milisegundos',
	'help': 'Muestra una página de ayuda general o de un comando específico///[comando]',
	'soy': 'Descubre quién eres',
	'say': 'Haz que el bot diga algo///<texto>',
	'emojitext': 'Devuelve el texto transformado en emojis///<texto>',
	'replace': 'Reemplaza el texto del primer parámetro por el segundo parametro en un tercer parámetro. Usa comillas para para los 2 primeros parámetros para usar espacios: `"text 1" "texto 2" texto 3`///<reemplazar esto> <por esto> <en este texto>',
	'spacedtext': 'Devuelve el texto enviado con cada letra espaciada el número de veces indicado///<número de espacios> <texto>',
	'vaporwave': 'Devuelve el texto en vaporwave///<texto>',
	'choose': 'Devuelve una de las opciones dadas, o "Si" o "No" si no le das opciones. Las opciones se separan por comas///[opciones]',
	'poll': 'Crea encuestas de manera sencilla. Los emojis se separan por espacios poniendo `-e` delante, si no se epecifican emojis e usaran :+1: y :-1:///<cuerpo de la encuesta> [-e emojis]',
	'kao': 'Devuelve una lista de kaomojis o un kaomoji específico///[kaomoji] [delete]',
	'purge': 'Elimina la cantidad de mensajes indicada///<número de mensajes a eliminar>',
	'avatar': 'Obtiene tú foto de perfil o la de otro usuario///[usuario]',
	'kick': 'Kickea o expulsa a un miembro del servidor///<miembro> [razón]',
	'ban': 'Banea a un miembro del servidor///<miembro> [razón]',
	'unban': 'Revoca el baneo a un usuario///<ID del usuario> [razón]',
	'defemoji': 'Envia emojis en el estado por defecto de tu dispositivo: \\😂. Si el emoji es personalizado de un server, se enviará su ID///<emojis>',
	'sarcastic': 'ConVIeRtE el TEXtO a SarcAStiCO///<texto>',
	'iq': 'Calcula tu IQ o el de otra persona///[miembro]',
	'tag': 'Añade o usa tags tuyos o de otras personas///<nombre del tag>\ntoggle\ngift <usuario>\nrename <tag> <nuevo nombre>\nedit <tag> <nuevo contenido>\nadd <nombre del tag> <contenido del tag> [flags: -img, -nsfw]\nremove <nombre del tag>\nowner <tag>\nlist [usuario]\nserverlist',
	'links': 'Obtén los links oficiales del bot',
	'someone': 'Menciona a alguien aleatorio del server',
	'ocr': 'Transcribe el texto de la última imagen enviada en el chat///[URL|imagen]',
	'joke': 'Envia un chiste que da menos risa que los de Siri///[ID del chiste] [-img]',
	'nothing': 'Literalmente no hace nada -s',
	'gay': 'Detecta como de homosexual eres///[usuario]',
	'prefix': 'Cambia el prefijo del bot a nivel de server. Para crear un prefijo con espacios, escribelo entre comillas: `"prefijo"`///<prefijo>',
	'changelog': 'Revisa el registro de cambios de cada versión del bot, o de la última dejando en blanco los parámetros///[versión]\nlist',
	'color': 'Cambia el color de los embeds del bot///<color>\nlist\ndefault',
	'wiktionary': 'Busca una palabra en inglés en el diccionario de Wiktionary///<palabra o expresión>',
	'dle': 'Busca una palabra en español en el Diccionario de la lengua española///<palabra>',
	'die': 'Apaga el bot -s',
	'getmsg': 'Obtiene los datos de un mensaje///<id> -s',
	'eval': 'Ejecuta código///<código> -s',
	'reload': 'Recarga un módulo///<módulo> -s',
	'unload': 'Descarga un módulo///<módulo> -s',
	'load': 'Carga un módulo///<módulo> -s',
	'binary': 'Codifica o decodifica código binario///encode <texto>\ndecode <texto>',
	'morse': 'Codifica o decodifica código morse///encode <texto>\ndecode <texto>',
	'hackban': 'Banea a un usuario sin necesidad de que esté en el server///<ID del usuario> [razón]',
	'userinfo': 'Obtiene información de un usuario. Habrá más información si este usuario se encuentra en este servidor///[usuario]',
	'roleinfo': 'Obtiene información de un rol///<rol>',
	'channelinfo': 'Obtiene la información de un canal de cualquier tipo o una categoría///[canal o categoría]',
	'serverinfo': 'Obtiene la información de este servidor',
	'blacklist': 'Mete o saca a un usuario de la blacklist///<user> -s',
	'uppercase': 'Convierte un texto a mayúsculas///<texto>',
	'lowercase': 'Convierte un texto a minúsculas///<texto>',
	'swapcase': 'Intercambia las minúsculas y las mayúsculas de un texto///<texto>',
	'capitalize': 'Convierte la primera letra de cada palabra a mayúsculas///<texto>',
	'count': 'Cuenta cuantas veces hay una letra o palabra dentro de otro texto. Recuerda que puedes usar comillas para usar espacios en el primer texto. Puedes pasar comillas vacías ("") para contar caracteres y palabras en general en un texto///<letra o palabras> <texto>',
	'botinfo': 'Obtiene información sobre el bot',
	'tictactoe': 'Juega una partida de Tic Tac Toe contra la maquina o contra un amigo///[usuario]',
	'reverse': 'Revierte un texto///<texto>',
	'randomnumber': 'Obtiene un número aleatorio entre el intervalo especificado. Puedes usar número negativos///<desde el 0 hasta este número>\n<desde este número> <hasta este>',
	'8ball': 'Preguntale algo el bot para que te responda///<pregunta>',
	'didyoumean': 'Escribe un texto que te corrija Google a otro. Separa los 2 textos por punto y coma entre espacios: ` ; `///<Texto 1> ; <Texto 2>',
	'drake': 'Haz un meme con la plantilla de drake. Separa los 2 textos por punto y coma entre espacios: ` ; `///<Texto 1> ; <Texto 2>',
	'bad': 'Ta mal///[imagen]',
	'amiajoke': 'Am I a joke to you?///[imagen]',
	'jokeoverhead': 'El que no entendía la broma///[imagen]',
	'salty': 'El ardido///[imagen]',
	'birb': 'Random birb',
	'dog': 'Imagen random de un perro',
	'cat': 'Imagen random de un gato',
	'sadcat': 'Imagen random de un gato triste',
	'calling': 'Tom llamando hm///<texto>',
	'captcha': 'Cursed captcha///<texto>',
	'facts': 'facts///<texto>',
	'supreme': 'Texto con fuente de Supreme///<light o dark> <texto>',
	'commandstats': 'Muestra cuales son los comandos más usados o cuantos veces se ha usado un comando///[comando]',
	'r34': 'Busca en rule34.xxx. Deja vacío para buscar imagenes aleatorias///[búsqueda]',
	'mcskin': 'Busca una skin de Minecraft según el nombre del usuario que pases///<usuario>',
	'percentencoding': 'Codifica o decodifica código porcentaje o código URL///encode <texto>\ndecode <texto>'
}


def get_cmd(ctx, command=None):
	if command == None:
		command = ctx.command
	else:
		command = ctx.bot.get_command(command)
	if command.description == '': 
		content = ['Detalles no disponibles']
	else:
		content = command.description.split('///')
		if content[-1].endswith('-s'):
			content[-1] = content[-1][:-2].strip()
	command_name = command.name
	embed = discord.Embed(title=command_name,
		description=f'{content[0]}.',
		colour=botdata.default_color(ctx)
		).set_footer(text='<arg> = obligatorio  |  [arg] = opcional')
	if len(content) == 2:
		syntax = content[1].replace('\n', f'`\n`{ctx.prefix}{command_name} ')
		embed.add_field(name='Sintáxis', value=f'`{ctx.prefix}{command_name} {syntax}`')
	if len(command.aliases) > 0:
		embed.add_field(name='Otros nombres', value=', '.join(command.aliases), inline=False)

	return embed


def get_all(ctx):
	final_categories = {
		'Modtxt': 'Modificación de texto',
		'Mod': 'Moderación',
		'Util': 'Utilidad',
		'Fun': 'Entretenimiento',
		'Image': 'Imágenes',
		'About': 'Sobre el bot',
		'Owner': 'Comandos del owner'
	}
	categories = {}
	for category in final_categories:
		categories.update({category: []})

	help_list = discord.Embed(
		title='Listado de comandos',
		description=f'NOTA: Usa `{ctx.prefix}help [comando]` para mas ayuda sobre dicho comando. Para usar espacios en parámetros que no lo permiten, usa comillas alrededor del parámetro en el que quieres usar espacios.',
		colour=botdata.default_color(ctx)
		).set_footer(text=f'Line {botdata.bot_mode.capitalize()} v{botdata.bot_version} - Cantidad de comandos: {len(ctx.bot.commands)}')
	
	for command in ctx.bot.commands:
		if command.hidden: 
			continue
		content = command.description.split('///')
		command_category = command.cog.qualified_name
		if command_category in categories:
			categories[command_category].append(command.name)

	for category in categories:
		if categories[category] == []:
			continue
		categories[category].sort()
		help_list.add_field(name=final_categories[category], value=', '.join(categories[category]), inline=False)
	
	return help_list
