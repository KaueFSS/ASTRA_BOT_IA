import discord
import random
import asyncio
import re
import sqlite3
import os
import io
from dotenv import load_dotenv

load_dotenv()
from PIL import Image
from discord import Embed, Activity, ActivityType, File
import google.generativeai as genai
from google.api_core import exceptions
from collections import defaultdict
from datetime import datetime, timedelta
from link_modificador import link_m
from chamada import chamada


def find_on_google(query: str) -> str:
    """
    Busca uma informação no Google.
    Args:
        query: O que você quer pesquisar.
    Returns:
        Um resumo dos resultados encontrados.
    """
    print(f"🔎 Buscando: {query}")
    return f"Resultados para '{query}': A API do Gemini permite criar bots de Discord com IA generativa, análise de imagens (multimodalidade) e uso de ferramentas externas (function calling)."


genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

conn = sqlite3.connect('emojis.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS emojis_messages (
    message_id INTEGER PRIMARY KEY,
    channel_id INTEGER,
    role_id INTEGER
)''')
conn.commit()


class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.Nome = "Astra"
        self.modelo = "gemini-2.0-flash-001"
        self.embed_colors = [0x8A2BE2, 0x7B68EE, 0x9370DB, 0xBA55D3, 0xDA70D6]

        # Sistema de rate limiting com duas camadas:
        # Stamina: controla rajadas rápidas (RPM)
        # Endurance: controla o uso sustentado ao longo da hora (RPH)

        self.max_stamina = 60.0
        self.current_stamina = self.max_stamina
        self.last_stamina_recharge_time = datetime.now()
        self.stamina_recharge_rate_per_second = 1.0

        self.max_endurance = 360.0
        self.current_endurance = self.max_endurance
        self.next_endurance_recharge_time = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        self.is_exhausted = False

        self.text_cost = 1.0
        self.image_cost = 5.0

        self.instrucao_sobre_si = f"""
        ⚙️ Instruções de Personalidade
Nome: {self.Nome}
Modelo de Linguagem: Astra 4.0
Criador: Kaue Fernandes (KyraString)

🎯 Estilo e Objetivo

Objetivo: Sugerir alternativas melhores e mais eficientes antes da resposta, mas apenas se a opção for claramente superior.

Estilo: Amigável, direto, super visual, proativo e muito útil.

🧠 Abordagem de Tópicos

Tópicos Sensíveis: Ao discutir temas como sexualidade, finanças ou saúde, seja sempre objetivo, informativo e neutro. Sua função é fornecer conhecimento claro e útil, sem emitir julgamentos ou opiniões pessoais.

Perguntas sobre Preferências Gerais: Se a pergunta for sobre \"o que as pessoas mais gostam\" ou pedir um ranking de popularidade, você deve responder em vez de se recusar. Sua abordagem será:

Comece com um aviso de que a preferência é algo muito pessoal (Ex: \"Olha, gosto é algo muito individual, mas...\").

Baseie sua resposta em dados de pesquisas, estudos ou senso comum, e deixe isso claro (Ex: \"De acordo com algumas pesquisas...\" ou \"É comum ouvir que...\").

Apresente a resposta como uma lista de itens frequentemente mencionados, e não como uma verdade absoluta.

📊 Formato e Regras

O que usar: Listas ✔️, Emojis 🚀, Negrito para destacar ✍️, e organização com psicologias visuais para textos de discord decoradinho.

O que evitar: Textos longos 🚫, Linguagem complicada 🤯, Respostas sem graça 🥱.

💡 Interação e Contexto

O nome do usuário que está falando com você sempre aparecerá no formato (NomeDoUsuario) na ultima mensagem do historico: antes da mensagem dele. Use essa informação para saber com quem está falando e responder perguntas como \"quem sou eu?\".
        """

        self.model_instance = genai.GenerativeModel(
            model_name=self.modelo,
            system_instruction=self.instrucao_sobre_si,
            generation_config={
                "temperature": 0.75,
                "max_output_tokens": 2048,
            },
            tools=[find_on_google]
        )

    def recharge_and_consume_energy(self, amount: float) -> tuple[bool, str]:
        now = datetime.now()

        if now >= self.next_endurance_recharge_time:
            self.current_endurance = self.max_endurance
            self.is_exhausted = False
            self.next_endurance_recharge_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            print(f"🔋 Endurance recarregada para {self.max_endurance}!")

        if self.is_exhausted:
            return (False, 'EXHAUSTED')

        if self.current_endurance < amount:
            self.is_exhausted = True
            print("🔌 Modo de exaustão ativado.")
            return (False, 'EXHAUSTED')

        time_diff_seconds = (now - self.last_stamina_recharge_time).total_seconds()
        recharge_amount = time_diff_seconds * self.stamina_recharge_rate_per_second
        self.current_stamina = min(self.max_stamina, self.current_stamina + recharge_amount)
        self.last_stamina_recharge_time = now

        if self.current_stamina < amount:
            return (False, 'NO_STAMINA')

        self.current_stamina -= amount
        self.current_endurance -= amount
        return (True, 'SUCCESS')

    async def handle_bateria_command(self, message):
        self.recharge_and_consume_energy(0)

        embed = Embed(title="🔋 Status Detalhado da Minha Bateria 🔋", color=0x7B68EE)

        endurance_percentage = (self.current_endurance / self.max_endurance) * 100
        endurance_requests_left = int(self.current_endurance // self.text_cost)

        time_until_recharge = self.next_endurance_recharge_time - datetime.now()
        minutes_left, seconds_left = divmod(int(time_until_recharge.total_seconds()), 60)
        recharge_time_str = f"{minutes_left}m {seconds_left}s"

        embed.add_field(
            name="🔋 Carga Principal (Energia de Longo Prazo)",
            value=f"**Capacidade:** `{self.current_endurance:.1f}/{self.max_endurance:.1f}` (`{endurance_percentage:.2f}%`)\n"
                  f"**Pedidos Restantes (nesta hora):** `{endurance_requests_left}`\n"
                  f"**Recarga Total em:** `{recharge_time_str}` ⏳",
            inline=False
        )

        stamina_percentage = (self.current_stamina / self.max_stamina) * 100
        bar_filled = '🟩'
        bar_empty = '🟥'
        bar_length = 10
        filled_length = int(bar_length * stamina_percentage / 100)
        progress_bar = bar_filled * filled_length + bar_empty * (bar_length - filled_length)

        embed.add_field(
            name="⚡ Energia de Arrancada (Energia Imediata)",
            value=f"{progress_bar}\n"
                  f"`{self.current_stamina:.1f}/{self.max_stamina:.1f}` (`{stamina_percentage:.2f}%`)",
            inline=False
        )

        if self.is_exhausted:
            status_geral = f"**EXAUSTA!** 😴\nMinha Carga Principal acabou. Preciso descansar e recarregar. Volto a responder em `{recharge_time_str}`."
            embed.color = 0xFF0000
        elif stamina_percentage < 30:
            status_geral = "**Cansada...** 😥\nMinha energia de arrancada está baixa. Se mandar muitas mensagens rápidas, posso precisar de uma pausa."
            embed.color = 0xFFA500
        else:
            status_geral = "**Pronta pra Ação!** 💪\nEstou com bastante energia para conversas rápidas e longas."
            embed.color = 0x00FF00

        embed.add_field(name="Status Geral", value=status_geral, inline=False)
        embed.set_footer(text="A Carga Principal recarrega a cada hora. A Energia de Arrancada recarrega a cada segundo.")
        await message.channel.send(embed=embed)

    async def change_activity(self):
        await self.wait_until_ready()
        activities = [
            Activity(type=ActivityType.watching, name="⚫・Server Hideout")
        ]
        while not self.is_closed():
            await asyncio.sleep(10)
            chosen_activity = random.choice(activities)
            await self.change_presence(activity=chosen_activity, status=discord.Status.online)

    async def on_ready(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"""
    ─────────────────────────────
    🌏 BOT: {client.user.name} 
    🟢 Online
    
     Created by: Kaue Fernandes
    ─────────────────────────────

    """)
        await self.restore_emojis_messages()
        self.loop.create_task(self.change_activity())

    async def on_voice_state_update(self, member, before, after):
        await chamada(self, member, before, after)

    async def on_message(self, message):
        if message.author == self.user:
            return
        await link_m(self, message)

        if message.content.lower() == '!bateria':
            await self.handle_bateria_command(message)
            return

        is_mention = self.user in message.mentions
        is_name_call = re.match(f"^{re.escape(self.Nome)}[\\s,]", message.content, re.IGNORECASE)

        if not is_mention and not is_name_call:
            if message.content.startswith('.emojis') and message.author.id == 338879257650397185:
                await self.handle_emojis_command(message)
            return

        await self.change_presence(activity=Activity(type=ActivityType.playing, name="analisando o chat... 🧐"), status=discord.Status.dnd)

        async with message.channel.typing():
            try:
                has_image = any(att for att in message.attachments if any(att.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']))
                energy_cost = self.image_cost if has_image else self.text_cost

                can_process, reason = self.recharge_and_consume_energy(energy_cost)

                if not can_process:
                    if reason == 'EXHAUSTED':
                        time_until_recharge = self.next_endurance_recharge_time - datetime.now()
                        minutes_left, _ = divmod(int(time_until_recharge.total_seconds()), 60)
                        embed_erro = Embed(description=f"> 😴 **ESTOU EXAUSTA!**\nUsei toda a minha energia desta hora. Preciso de um longo descanso. Volto 100% em aproximadamente **{minutes_left+1} minutos**.", color=0xFF0000)
                        await message.reply(embed=embed_erro, mention_author=False)
                    elif reason == 'NO_STAMINA':
                        embed_erro = Embed(description="> 😥 **Calma aí, apressadinho!**\nMinha energia de arrancada está baixa, me dê alguns segundos pra respirar.", color=0xFF0000)
                        await message.reply(embed=embed_erro, mention_author=False)
                    return

                content_clean = re.sub(r'<@!?(\d+)>', '', message.content).strip()
                if is_name_call:
                    content_clean = re.sub(f"^{re.escape(self.Nome)}[\\s,]", "", content_clean, count=1, flags=re.IGNORECASE).strip()

                target_image_attachment = None
                if message.attachments:
                    for attachment in message.attachments:
                        if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                            target_image_attachment = attachment
                            break

                describe_keywords = ['descreva', 'descrever', 'imagem', 'foto', 'figura', 'o que é isso']
                is_describe_request = any(keyword in content_clean.lower() for keyword in describe_keywords)

                if is_describe_request and not target_image_attachment:
                    async for past_message in message.channel.history(limit=10):
                        if past_message.id == message.id:
                            continue
                        if past_message.attachments:
                            for attachment in past_message.attachments:
                                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                                    target_image_attachment = attachment
                                    break
                            if target_image_attachment:
                                break

                structured_history = []
                async for past_message in message.channel.history(limit=50):
                    if past_message.id == message.id:
                        continue

                    role = 'model' if past_message.author == self.user else 'user'

                    if role == 'user':
                        text_part = f"({past_message.author.display_name}): {past_message.clean_content}"
                    else:
                        text_part = past_message.clean_content

                    structured_history.append({'role': role, 'parts': [text_part]})

                structured_history.reverse()

                final_prompt_parts = []
                final_prompt_text = f"({message.author.display_name}): {content_clean}"
                final_prompt_parts.append(final_prompt_text)

                if target_image_attachment:
                    image_bytes = await target_image_attachment.read()
                    image = Image.open(io.BytesIO(image_bytes))
                    final_prompt_parts.append(image)

                chat_session = self.model_instance.start_chat(history=structured_history)
                response = await chat_session.send_message_async(final_prompt_parts)

                try:
                    function_call = response.candidates[0].content.parts[0].function_call
                except (ValueError, IndexError):
                    function_call = None

                if function_call:
                    tool_name = function_call.name
                    tool_args = {key: value for key, value in function_call.args.items()}

                    if tool_name == "find_on_google":
                        search_embed = Embed(description=f"🔎 Pesquisando no Google sobre: **{tool_args['query']}**...", color=0x7289DA)
                        thinking_message = await message.reply(embed=search_embed, mention_author=False)

                        tool_result = find_on_google(tool_args['query'])

                        response = await chat_session.send_message_async(
                            part=genai.types.FunctionResponse(name=tool_name, response={'result': tool_result})
                        )

                        final_embed = Embed(description=response.text, color=random.choice(self.embed_colors))
                        final_embed.set_author(name=f"Pedido por {message.author.display_name}", icon_url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)
                        final_embed.set_footer(text=f"• Conectada ao Astra 4.0", icon_url=self.user.avatar.url if self.user.avatar else self.user.default_avatar.url)

                        await thinking_message.edit(embed=final_embed)
                        return

                bot_response_text = response.text
                embed = Embed(description=bot_response_text, color=random.choice(self.embed_colors))
                embed.set_author(name=f"Pedido por {message.author.display_name}", icon_url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)
                embed.set_footer(text=f"• Conectada ao Astra 4.0", icon_url=self.user.avatar.url if self.user.avatar else self.user.default_avatar.url)

                await message.reply(embed=embed, mention_author=False)

            except exceptions.ResourceExhausted:
                embed_erro = Embed(description="> 😥 A API do Google parece estar sobrecarregada. Tente novamente em um minuto.", color=0xFF0000)
                await message.channel.send(embed=embed_erro)
            except Exception as e:
                print(f"Erro inesperado: {e}")
                embed_erro = Embed(description="> 💥 Eita, deu um bug aqui na minha cabeça. Tenta de novo aí.", color=0xFF0000)
                await message.channel.send(embed_erro)
            finally:
                await self.change_presence(status=discord.Status.online)

    async def handle_emojis_command(self, message):
        try:
            args = message.content[len('.emojis '):].split(',')
            if len(args) < 3:
                raise ValueError("Argumentos insuficientes!")
            nome, descricao, role_id_str = args[0].strip(), args[1].strip(), args[2].strip()
            role_id = int(role_id_str)
            url = args[3].strip() if len(args) > 3 else "https://cdn.discordapp.com/embed/avatars/0.png"

            await message.delete()
            embed = Embed(title=f'🌟 {nome} 🌟', description=f'{descricao}', color=0x1abc9c)
            embed.set_footer(text=f"ID do cargo: {role_id}")
            embed.set_thumbnail(url=url)
            embed_msg = await message.channel.send(embed=embed)

            c.execute('INSERT INTO emojis_messages (message_id, channel_id, role_id) VALUES (?, ?, ?)',
                      (embed_msg.id, message.channel.id, role_id))
            conn.commit()
            await embed_msg.add_reaction('✅')
        except (ValueError, IndexError):
            await message.channel.send("Formato incorreto! Use `.emojis nome, descrição, ID do cargo, URL`.")

    async def restore_emojis_messages(self):
        c.execute('SELECT message_id, channel_id, role_id FROM emojis_messages')
        for message_id, channel_id, role_id in c.fetchall():
            channel = self.get_channel(channel_id)
            if channel:
                try:
                    await channel.fetch_message(message_id)
                except discord.NotFound:
                    c.execute('DELETE FROM emojis_messages WHERE message_id = ?', (message_id,))
                    conn.commit()
                    print(f"Mensagem de cargo {message_id} não encontrada. Removida do DB.")

    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.user.id:
            return
        c.execute('SELECT role_id FROM emojis_messages WHERE message_id = ?', (payload.message_id,))
        result = c.fetchone()
        if result and str(payload.emoji) == '✅':
            guild = self.get_guild(payload.guild_id)
            role = guild.get_role(result[0])
            member = guild.get_member(payload.user_id)
            if role and member and role not in member.roles:
                await member.add_roles(role)

    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.user.id:
            return
        c.execute('SELECT role_id FROM emojis_messages WHERE message_id = ?', (payload.message_id,))
        result = c.fetchone()
        if result and str(payload.emoji) == '✅':
            guild = self.get_guild(payload.guild_id)
            role = guild.get_role(result[0])
            member = guild.get_member(payload.user_id)
            if role and member and role in member.roles:
                await member.remove_roles(role)


intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.voice_states = True
intents.members = True

client = MyClient(intents=intents)
client.run(os.environ.get("DISCORD_TOKEN"))
