import discord
import re

LINK_FIXES_MAP = {
    "instagram.com": "kkinstagram.com",
    "tiktok.com": "vxtiktok.com",
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

    try:
        target_webhook = None
        webhooks = await message.channel.webhooks()
        for wh in webhooks:
            if wh.name == "Corretor de Links Ninja":
                target_webhook = wh
                break

        if not target_webhook:
            target_webhook = await message.channel.create_webhook(
                name="Corretor de Links Ninja",
                reason="Para correção automática e transparente de links"
            )

        links_text = "\n".join(fixed_links)
        await target_webhook.send(
            content=links_text,
            username=message.author.display_name,
            avatar_url=message.author.display_avatar.url
        )

        await message.delete()

    except discord.Forbidden:
        print(f"ERRO: Permissões insuficientes no canal {message.channel.name}.")
        try:
            await message.channel.send(
                "⚠️ **Atenção!** Eu preciso das permissões de `Gerenciar Mensagens` e `Gerenciar Webhooks` para funcionar.",
                delete_after=20
            )
        except discord.Forbidden:
            pass
    except Exception as e:
        print(f"Erro inesperado: {e}")
