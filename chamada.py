import discord
from datetime import datetime
import random

# --- CONFIGURAÇÕES ---
# Coloque o ID do canal de texto onde as mensagens devem ser enviadas
TEXT_CHANNEL_ID = 756707561255731290 
JOIN_COLOR = 0x2ECC71  # Verde mais vibrante
LEAVE_COLOR = 0xE74C3C # Vermelho mais suave

# --- LISTAS PARA ALEATORIEDADE ---

# Títulos quando alguém entra
TITULOS_ENTRADA = [
    "⚠️ ALERTA DE PERTURBAÇÃO",
    "✨ UMA LENDA (NEGATIVA) APARECE",
    "📞 CHAMADA INTERROMPIDA",
    "👾 INVASÃO DETECTADA",
    "🤡 O CIRCO CHEGOU",
]

# Títulos quando alguém sai
TITULOS_SAIDA = [
    "🕊️ A PAZ REINA NOVAMENTE",
    "💨 VIROU FUMAÇA",
    "✅ MISSÃO CUMPRIDA: IRRITAR A TODOS",
    "👋 ATÉ NUNCA MAIS",
    "🔇 O SILÊNCIO É DE OURO",
]

# Frases de zuação para entrada
ZOACOES_ENTRADA = [
    "Entrou na call como se fosse o dono da verdade... mas é só o dono do microfone ruim.",
    "Apareceu! Achei que tinha caído na fenda do sofá.",
    "O eco da sala acaba de ganhar um concorrente.",
    "Se preparem para opiniões que ninguém pediu.",
    "Conexão estabelecida. Infelizmente.",
    "Olha só, a fonte oficial de ruído branco chegou.",
    "A call estava boa demais pra ser verdade.",
]

# Frases de zuação para saída
ZOACOES_SAIDA = [
    "Saiu e levou junto a minha dor de cabeça. Obrigado.",
    "Finalmente! A qualidade do áudio do servidor aumentou em 200%.",
    "Foi tarde, mas pelo menos foi.",
    "A cota de falar besteira por hoje foi atingida.",
    "O universo está em equilíbrio novamente.",
    "Deixou um vácuo... de silêncio abençoado.",
    "Desconectou. O servidor respira aliviado.",
]

# Rodapés aleatórios para dar um charme
RODAPES_ALEATORIOS = [
    "Este bot não se responsabiliza por danos auditivos.",
    "Patrocinado pelo caos.",
    "Qualidade garantida (ou não).",
    "As opiniões expressas aqui não refletem as nossas.",
    "Erro 404: Bom senso não encontrado.",
]

# Dicionários para rastreamento (mantidos como no original)
usuarios_hoje = {}
horas_de_entrada = {}

def emoji_personalizado(name: str) -> str:
    """Gera um emoji 'ofensivo' com base no nome do usuário."""
    base = sum(ord(c) for c in name)
    # Lista de emojis renovada e mais criativa
    emojis = ["👻", "🤡", "👽", "🤖", "👾", "👺", "👹", "💀", "🐌", "🦆"]
    return emojis[base % len(emojis)]

async def chamada(client, member, before, after):
    """Função principal que lida com eventos de entrada e saída de canais de voz."""
    text_channel = client.get_channel(TEXT_CHANNEL_ID)
    if not text_channel:
        print(f"ERRO: Canal de texto com ID {TEXT_CHANNEL_ID} não encontrado.")
        return

    display_name = member.display_name
    is_joining = before.channel is None and after.channel is not None
    is_leaving = before.channel is not None and after.channel is None
    
    # Ignorar eventos que não são de entrada ou saída (ex: mutar, desmutar)
    if not is_joining and not is_leaving:
        return

    voice_channel = after.channel or before.channel
    
    # --- LÓGICA DE ENTRADA ---
    if is_joining:
        if member.id not in usuarios_hoje:
            usuarios_hoje[member.id] = len(usuarios_hoje) + 1
        horas_de_entrada[member.id] = datetime.now()

        # Seleciona os elementos aleatórios
        titulo_aleatorio = random.choice(TITULOS_ENTRADA)
        frase_aleatoria = random.choice(ZOACOES_ENTRADA)
        rodape_aleatorio = random.choice(RODAPES_ALEATORIOS)
        emoji = emoji_personalizado(member.name)
        posicao = usuarios_hoje[member.id]
        
        # Cria o Embed
        embed = discord.Embed(
            title=f"{emoji} {titulo_aleatorio}: {display_name.upper()}",
            description=f"_{frase_aleatoria}_",
            color=JOIN_COLOR
        )
        
        # Usa a thumbnail para um visual mais limpo
        if member.display_avatar:
            embed.set_thumbnail(url=member.display_avatar.url)

        # Campos com mais informações e emojis
        embed.add_field(name="📍 Canal", value=voice_channel.mention, inline=True)
        # Timestamp dinâmico do Discord!
        timestamp = f"<t:{int(datetime.now().timestamp())}:F>"
        embed.add_field(name="⏰ Horário", value=timestamp, inline=True)
        embed.add_field(name="🏆 Ranking do Dia", value=f"**#{posicao}** a perturbar a paz.", inline=False)

        embed.set_footer(text=rodape_aleatorio)
        
        # Botão para entrar na call
        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="Juntar-se ao hospício",
            url=f"https://discordapp.com/channels/{member.guild.id}/{voice_channel.id}",
            style=discord.ButtonStyle.link,
            emoji="🚪"
        ))

        await text_channel.send(embed=embed, view=view)

    # --- LÓGICA DE SAÍDA ---
    elif is_leaving:
        entrada = horas_de_entrada.pop(member.id, None)
        duracao_str = ""
        if entrada:
            tempo_total = datetime.now() - entrada
            minutos, segundos = divmod(int(tempo_total.total_seconds()), 60)
            duracao_str = f"**{minutos}m {segundos}s**"

        # Seleciona os elementos aleatórios
        titulo_aleatorio = random.choice(TITULOS_SAIDA)
        frase_aleatoria = random.choice(ZOACOES_SAIDA)
        rodape_aleatorio = random.choice(RODAPES_ALEATORIOS)
        emoji = emoji_personalizado(member.name)

        # Cria o Embed
        embed = discord.Embed(
            title=f"{emoji} {titulo_aleatorio}: {display_name.upper()}",
            description=f"_{frase_aleatoria}_",
            color=LEAVE_COLOR
        )
        
        if member.display_avatar:
            embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="📤 Canal", value=voice_channel.mention, inline=True)
        if duracao_str:
            embed.add_field(name="⏱️ Tempo de Tortura", value=duracao_str, inline=True)

        embed.set_footer(text=rodape_aleatorio)
        
        await text_channel.send(embed=embed)