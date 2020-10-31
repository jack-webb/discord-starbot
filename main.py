import sys
from typing import Optional
import discord
from peewee import DoesNotExist
import config
from model import Star, database
import logging

client = discord.Client()
logging.basicConfig(level=logging.INFO)


@client.event
async def on_ready():
    print("=====================")
    print("Discord Starbot, by Jack Webb")
    print("https://github.com/jack-webb/discord-starbot/")
    print(f"Python version {sys.version}")
    print(f"discord.py version {discord.__version__}")
    print(f"Starbot ready, logged in as {client.user}")
    print("=====================")


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    logging.debug("on_raw_reaction_add")
    if str(payload.emoji) == config.emoji:
        message = await get_message(payload.channel_id, payload.message_id)
        star, created = Star.get_or_create(
            message_id=payload.message_id,
            channel_id=payload.channel_id,
            defaults={
                'star_id': 0,
                'username': str(message.author),
                'avatar_url': str(message.author.avatar_url),
                'channel': str(message.channel),
                'jump_link': message.jump_url,
                'content': message.content,
                'attachment_url': message.attachments[0].url if 0 < len(message.attachments) else None,
                'votes': get_star_count(message),
                'timestamp': message.created_at,
            })

        if not created:
            star.votes = get_star_count(message)

        await update(star)


@client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    logging.debug("on_raw_reaction_remove")
    message = await get_message(payload.channel_id, payload.message_id)
    if str(payload.emoji) == config.emoji and message is not None:
        star = get_star(payload.message_id)

        star.votes = get_star_count(message)

        await update(star)


@client.event
async def on_raw_message_edit(payload: discord.RawMessageUpdateEvent):
    logging.debug("on_raw_message_edit")
    message = await get_message(payload.channel_id, payload.message_id)
    star = get_star(payload.message_id)
    if star is not None:
        star.is_edited = True
        star.content = message.content

        await update(star)


@client.event
async def on_raw_message_delete(payload: discord.RawMessageDeleteEvent):
    logging.debug("on_raw_message_delete")
    star = get_star(payload.message_id)
    if star is not None:
        await delete(star)


def setup_database():
    database.connect()
    database.create_tables([Star])


def get_star_count(message: discord.Message) -> int:
    if config.emoji in [str(reaction.emoji) for reaction in message.reactions]:
        return [reaction for reaction in message.reactions if reaction.emoji == config.emoji][0].count
    else:
        return 0


def get_star(message_id: int) -> Optional[Star]:
    try:
        star = Star.get(message_id=message_id)
        logging.debug(f"Found star for {message_id}")
        return star
    except DoesNotExist:
        logging.debug(f"Star for {message_id} does not exist")
        return None


async def update(star: Star):
    # Update the database
    star.save()
    # Update the message
    await handle_message(star)


async def delete(star: Star):
    # Remove the message
    message = await get_message(config.star_channel, star.star_id)
    await message.delete()
    # Remove from database
    star.delete_instance()


async def get_message(channel_id: int, message_id: int) -> discord.Message:
    channel = client.get_channel(channel_id)
    return await channel.fetch_message(message_id)


async def handle_message(star: Star):
    channel = client.get_channel(config.star_channel)

    try:
        message = await channel.fetch_message(star.star_id)
    except discord.NotFound:
        message = None

    if message is not None:  # Edit or delete
        if star.votes >= config.threshold:
            print(f"editing {message}")
            await message.edit(embed=build_embed(star))
        else:
            print(f"deleting {message}")
            await delete(star)
    elif star.votes >= config.threshold:  # Create a new one
        print(f"creating {message}")
        star_message = await channel.send(embed=build_embed(star))
        star.star_id = star_message.id
        star.save()
    else:
        print(f"do nothing {message}")


def build_embed(star: Star) -> discord.Embed:
    embed = discord.Embed(
        description=star.content,
        color=discord.Colour.from_rgb(config.colour[0], config.colour[1], config.colour[2]),
        url=star.jump_link,
    )

    if star.attachment_url:
        embed.set_image(url=star.attachment_url)

    embed.set_author(
        name=f"{star.username} in #{star.channel}",
        icon_url=star.avatar_url
    )

    embed.add_field(
        name=f"{config.emoji} {star.votes} star(s)",
        value=f"[Posted {star.timestamp.strftime('%a, %d %b %Y at %H:%M')}]({star.jump_link})"
    )

    return embed


if __name__ == '__main__':
    setup_database()
    client.run(config.token)

# todo support custom emoji by ID
# todo make better use of caching (eg payload raw data instead of refetch)
