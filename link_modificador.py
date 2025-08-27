import discord
import re

# --- CONFIGURAÇÕES ---
LINK_FIXES_MAP = {
    "instagram.com": "ddinstagram.com",
    "tiktok.com": "vxtiktok.com",      # <-- ALTERADO AQUI!
    "x.com": "fixupx.com",
    "twitter.com": "fixupx.com",
}

DOMAINS_TO_SEARCH = [
    "instagram.com", "www.instagram.com",
    "tiktok.com", "www.tiktok.com", "vm.tiktok.com",
    "x.com",
    "twitter.com", "mobile.twitter.com", "www.twitter.com"
]

URL_REGEX = re.compile(
    f"https?://({'|'.join(re.escape(domain) for domain in DOMAINS_TO_SEARCH)})/[^\\s]+",
    re.IGNORECASE
)

# --- FUNÇÃO PRINCIPAL ---
async def link_m(client, message):
    if message.author.bot:
        return

    found_links = URL_REGEX.finditer(message.content)
    fixed_links = []

    for match in found_links:
        original_link = match.group(0)
        matched_domain_part = match.group(1)
        for base_domain, fix_domain in LINK_FIXES_MAP.items():
            if base_domain in matched_domain_part:
                fixed_link = original_link.replace(matched_domain_part, fix_domain, 1)
                fixed_links.append(fixed_link)
                break

    if not fixed_links:
        return

    # --- LÓGICA DO NINJA CAMUFLADO (WEBHOOK) ---
    try:
        # 1. Procura por um webhook que o bot possa usar
        target_webhook = None
        webhooks = await message.channel.webhooks()
        for wh in webhooks:
            # Reutiliza um webhook criado anteriormente por ele
            if wh.name == "Corretor de Links Ninja":
                target_webhook = wh
                break

        # 2. Se não encontrar, cria um novo (só na primeira vez)
        if not target_webhook:
            target_webhook = await message.channel.create_webhook(
                name="Corretor de Links Ninja",
                reason="Para correção automática e transparente de links"
            )

        # 3. Junta os links e envia usando o disfarce
        links_text = "\n".join(fixed_links)
        await target_webhook.send(
            content=links_text,
            username=message.author.display_name,
            avatar_url=message.author.display_avatar.url # Pega o avatar do usuário
        )

        # 4. Apaga a mensagem original
        await message.delete()

    except discord.Forbidden:
        # Se o bot não tiver permissão, avisa no console e no chat
        print(f"ERRO: O bot não tem permissão de 'Gerenciar Webhooks' ou 'Gerenciar Mensagens' no canal {message.channel.name}.")
        try:
            await message.channel.send(
                f"⚠️ **Atenção!** Eu preciso das permissões de `Gerenciar Mensagens` e `Gerenciar Webhooks` para funcionar.",
                delete_after=20
            )
        except discord.Forbidden:
            pass # Não consegue nem enviar a mensagem de erro
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")