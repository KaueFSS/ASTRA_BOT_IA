import discord
from datetime import datetime
import random

TEXT_CHANNEL_ID = 756707561255731290

JOIN_COLOR = 0x2ECC71
LEAVE_COLOR = 0xE74C3C

TITULOS_ENTRADA = [
    "⚠️ ALERTA DE PERTURBAÇÃO",
    "✨ UMA LENDA (NEGATIVA) APARECE",
    "📞 CHAMADA INTERROMPIDA",
    "👾 INVASÃO DETECTADA",
    "🤡 O CIRCO CHEGOU",
]

TITULOS_SAIDA = [
    "🕊️ A PAZ REINA NOVAMENTE",
    "💨 VIROU FUMAÇA",
    "✅ MISSÃO CUMPRIDA: IRRITAR A TODOS",
    "👋 ATÉ NUNCA MAIS",
    "🔇 O SILÊNCIO É DE OURO",
]

ZOACOES_ENTRADA = [
    "Entrou na call como se fosse o dono da verdade... mas é só o dono do microfone ruim.",
    "Apareceu! Achei que tinha caído na fenda do sofá.",
    "O eco da sala acaba de ganhar um concorrente.",
    "Se preparem para opiniões que ninguém pediu.",
    "Conexão estabelecida. Infelizmente.",
    "Olha só, a fonte oficial de ruído branco chegou.",
    "A call estava boa demais pra ser verdade.",
]

ZOACOES_SAIDA = [
    "Saiu e levou junto a minha dor de cabeça. Obrigado.",
    "Finalmente! A qualidade do áudio do servidor aumentou em 200%.",
    "Foi tarde, mas pelo menos foi.",
    "A cota de falar besteira por hoje foi atingida.",
    "O universo está em equilíbrio novamente.",
    "Deixou um vácuo... de silêncio abençoado.",
    "Desconectou. O servidor respira aliviado.",
]

RODAPES_ALEATORIOS = [
    "Este bot não se responsabiliza por danos auditivos.",
    "Patrocinado pelo caos.",
    "Qualidade garantida (ou não).",
    "As opiniões expressas aqui não refletem as nossas.",
    "Erro 404: Bom senso não encontrado.",
]

usuarios_hoje = {}
horas_de_entrada = {}


def emoji_personalizado(name: str) -> str:
    base = sum(ord(c) for c in name)
    emojis = ["👻", "🤡", "👽", "🤖", "👾", "👺", "👹", "💀", "🐌", "🦆"]
    return emojis[base % len(emojis)]


async def chamada(client, member, before, after):
    text_channel = client.get_channel(TEXT_CHANNEL_ID)
    if not text_channel:
        print(f"ERRO: Canal de texto com ID {TEXT_CHANNEL_ID} não encontrado.")
        return

    display_name = member.display_name
    is_joining = before.channel is None and after.channel is not None
    is_leaving = before.channel is not None and after.channel is None

    if not is_joining and not is_leaving:
        return

    voice_channel = after.channel or before.channel

    if is_joining:
        if member.id not in usuarios_hoje:
            usuarios_hoje[member.id] = len(usuarios_hoje) + 1
        horas_de_entrada[member.id] = datetime.now()

        titulo_aleatorio = random.choice(TITULOS_ENTRADA)
        frase_aleatoria = random.choice(ZOACOES_ENTRADA)
        rodape_aleatorio = random.choice(RODAPES_ALEATORIOS)
        emoji = emoji_personalizado(member.name)
        posicao = usuarios_hoje[member.id]

        embed = discord.Embed(
            title=f"{emoji} {titulo_aleatorio}: {display_name.upper()}",
            description=f"_{frase_aleatoria}_",
            color=JOIN_COLOR
        )

        if member.display_avatar:
            embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="📍 Canal", value=voice_channel.mention, inline=True)
        timestamp = f"<t:{int(datetime.now().timestamp())}:F>"
        embed.add_field(name="⏰ Horário", value=timestamp, inline=True)
        embed.add_field(name="🏆 Ranking do Dia", value=f"**#{posicao}** a perturbar a paz.", inline=False)
        embed.set_footer(text=rodape_aleatorio)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="Juntar-se ao hospício",
            url=f"https://discordapp.com/channels/{member.guild.id}/{voice_channel.id}",
            style=discord.ButtonStyle.link,
            emoji="🚪"
        ))

        await text_channel.send(embed=embed, view=view)

    elif is_leaving:
        entrada = horas_de_entrada.pop(member.id, None)
        duracao_str = ""
        if entrada:
            tempo_total = datetime.now() - entrada
            minutos, segundos = divmod(int(tempo_total.total_seconds()), 60)
            duracao_str = f"**{minutos}m {segundos}s**"

        titulo_aleatorio = random.choice(TITULOS_SAIDA)
        frase_aleatoria = random.choice(ZOACOES_SAIDA)
        rodape_aleatorio = random.choice(RODAPES_ALEATORIOS)
        emoji = emoji_personalizado(member.name)

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
