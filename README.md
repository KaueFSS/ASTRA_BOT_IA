<div align="center">

# 🌌 Astra Bot

**Bot de Discord com IA generativa, feito pra uso pessoal com os amigos.**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2?style=flat-square&logo=discord&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-4285F4?style=flat-square&logo=google&logoColor=white)

</div>

---

## Sobre o projeto

A Astra nasceu de um tempo que fiquei brincando com a API do Gemini e resolvi integrar num bot pro Discord. O que começou como um teste virou algo que ficou rodando nos servidores com os amigos por um bom tempo, ganhando features conforme a necessidade ia aparecendo.

Estou disponibilizando o código publicamente pra quem quiser usar, adaptar ou só dar uma olhada em como as coisas foram montadas. Fique à vontade.

---

## Funcionalidades

**IA Conversacional**
Mencione o bot pelo nome ou via `@` e ele responde usando o Gemini 2.0 Flash. Mantém histórico da conversa e consegue analisar imagens enviadas no chat.

**Corretor de Links**
Detecta links de Instagram, TikTok, Twitter/X e substitui automaticamente por versões que embeds funcionam corretamente no Discord. Tudo feito via webhook pra parecer que foi o próprio usuário quem enviou.

**Notificações de Voz**
Quando alguém entra ou sai de um canal de voz, o bot manda uma mensagem bem-humorada num canal de texto configurado, com tempo de permanência e ranking do dia.

**Cargos por Reação**
Sistema de auto-roles: cria uma mensagem embed e quem reagir com ✅ recebe (ou perde) o cargo configurado.

**Rate Limiting Duplo**
Para não estourar os limites da API do Gemini, tem um sistema com duas camadas: uma pra controlar rajadas rápidas (RPM) e outra pra uso sustentado ao longo da hora. Use `!bateria` pra ver o status atual.

---

## Como rodar

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/astra-bot.git
cd astra-bot
```

**2. Instale as dependências**
```bash
pip install -r requirements.txt
```

**3. Configure as variáveis de ambiente**

Copie o `.env.example` e preencha com suas credenciais:
```bash
cp .env.example .env
```

```env
DISCORD_TOKEN=seu_token_aqui
GEMINI_API_KEY=sua_chave_gemini_aqui
```

**4. Ajuste as configurações**

Em `chamada.py`, mude o `TEXT_CHANNEL_ID` pro ID do canal de texto onde as notificações de voz devem aparecer.

Em `astra.py`, o ID do owner (linha do comando `.emojis`) está fixo — troque pelo seu.

**5. Rode**
```bash
python astra.py
```

---

## Permissões necessárias no Discord

O bot precisa das seguintes permissões no servidor:

- Ler mensagens / Ver canais
- Enviar mensagens
- Gerenciar mensagens
- Gerenciar webhooks
- Adicionar reações
- Ver membros do servidor
- Gerenciar cargos (abaixo do cargo do bot na hierarquia)
- Conectar / Ver canais de voz

---

## Estrutura

```
astra-bot/
├── astra.py              # Arquivo principal, lógica do bot e IA
├── chamada.py            # Notificações de entrada/saída em calls
├── link_modificador.py   # Correção automática de links
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Stack

- [discord.py](https://discordpy.readthedocs.io/) — wrapper da API do Discord
- [Google Gemini](https://ai.google.dev/) — modelo de linguagem
- [Pillow](https://pillow.readthedocs.io/) — processamento de imagens
- SQLite — armazenamento dos cargos por reação

---

<div align="center">
  <sub>Feito por <a href="https://github.com/KyraString">Kaue Fernandes</a></sub>
</div>
