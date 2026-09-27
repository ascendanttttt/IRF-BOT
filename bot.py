import asyncio
import sys
import random

# Forzar el selector de red clásico en Windows para evitar errores de red
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print(f"¡Conectado como {client.user}!")

# --- COMANDOS DE ADMINISTRADOR GENERALES ---

@client.command(name="decir")
@commands.has_permissions(administrator=True)
async def decir(ctx, *, texto: str):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    await ctx.send(texto)

@client.command(name="foto")
@commands.has_permissions(administrator=True)
async def foto(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    
    if ctx.message.attachments:
        try:
            archivo = await ctx.message.attachments[0].to_file()
            await ctx.send(file=archivo)
        except Exception:
            pass

@client.command(name="prediccion")
@commands.has_permissions(administrator=True)
async def prediccion(ctx, *, enfrentamiento: str):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    
    goles1 = random.randint(1, 10)
    goles2 = random.randint(1, 10)
    
    await ctx.send(f"🔮 **SIMULACIÓN DE PARTIDO** 🔮\n\n{enfrentamiento}\n\n⚽ **Resultado final:** {goles1} - {goles2}")

@client.command(name="lock")
@commands.has_permissions(administrator=True)
async def lock(ctx):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    
    role_everyone = ctx.guild.default_role
    
    try:
        await ctx.channel.set_permissions(role_everyone, send_messages=False)
        await ctx.send("🔒 **Canal bloqueado.**", delete_after=4)
    except Exception as e:
        await ctx.send("❌ Hubo un error al intentar bloquear el canal.", delete_after=5)


# --- SISTEMA DE MODERACIÓN Y WARNS ---

@client.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, razon: str = "No especificada"):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    
    try:
        await member.kick(reason=razon)
        await ctx.send(f"👢 **{member.mention}** ha sido expulsado del servidor. Razón: *{razon}*", delete_after=6)
    except Exception:
        await ctx.send(f"❌ No se pudo expulsar a {member.mention}.", delete_after=5)

@client.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, razon: str = "No especificada"):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    
    try:
        await member.ban(reason=razon)
        await ctx.send(f"🔨 **{member.name}** ha sido baneado del servidor. Razón: *{razon}*", delete_after=6)
    except Exception:
        await ctx.send(f"❌ No se pudo banear a {member.mention}.", delete_after=5)

@client.command(name="warn")
@commands.has_permissions(manage_roles=True)
async def warn(ctx, member: discord.Member, *, razon: str = "No especificada"):
    try:
        await ctx.message.delete()
    except Exception:
        pass

    # Buscamos los roles de Warn del 1 al 5 en el servidor
    roles_warn = {
        1: discord.utils.get(ctx.guild.roles, name="Warn 1"),
        2: discord.utils.get(ctx.guild.roles, name="Warn 2"),
        3: discord.utils.get(ctx.guild.roles, name="Warn 3"),
        4: discord.utils.get(ctx.guild.roles, name="Warn 4"),
        5: discord.utils.get(ctx.guild.roles, name="Warn 5"),
    }

    # Verificamos que los roles existan creados en el servidor
    if not all(roles_warn.values()):
        await ctx.send("❌ Faltan roles por crear. Asegúrate de tener exactamente los roles: `Warn 1`, `Warn 2`, `Warn 3`, `Warn 4` y `Warn 5`.", delete_after=7)
        return

    # Determinamos qué warn actual tiene el usuario para subirlo al siguiente nivel
    nivel_actual = 0
    for nivel, rol in roles_warn.items():
        if rol in member.roles:
            nivel_actual = nivel
            break

    nuevo_nivel = nivel_actual + 1

    if nuevo_nivel > 5:
        await ctx.send(f"⚠️ **{member.mention}** ya tiene 5 warns acumulados. ¡Deberías aplicarle una sanción mayor (Kick/Ban)!", delete_after=6)
        return

    try:
        # Si tenía un warn anterior, se lo sacamos
        if nivel_actual > 0:
            await member.remove_roles(roles_warn[nivel_actual])
        
        # Le asignamos el nuevo rol de warn
        await member.add_roles(roles_warn[nuevo_nivel])
        
        await ctx.send(f"⚠️ **{member.mention}** ha recibido una advertencia (**Warn {nuevo_nivel}/5**). Razón: *{razon}*", delete_after=6)
    except Exception:
        await ctx.send("❌ Hubo un error al intentar asignar el rol de warn. Revisa los permisos del bot.", delete_after=5)


# --- MANEJO DE ERRORES GENERALES ---

@decir.error
@foto.error
@prediccion.error
@lock.error
@kick.error
@ban.error
@warn.error
async def permisos_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ No tienes los permisos necesarios para usar este comando.", delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Faltan datos (ejemplo de uso: `!warn @usuario [razón]`).", delete_after=5)
# Arrancar el bot

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="bienvenida")
    if channel:
        mensaje = (
            f"¡Bienvenido/a {member.mention} a la **IRF │ International Roblox Federation │ S1**! ⚽🎉 "
            f"Qué bueno tenerte por acá. ¡Pasala bien y busca un equipo!"
        )
        
        # Logo de la liga por enlace directo que ya subiste
        logo_url = "https://media.discordapp.net/attachments/1553427240556040202/1553872946395746325/IRF.png"
        
        # Envía el mensaje de texto junto con el enlace de la imagen para que Discord muestre la miniatura
        await channel.send(f"{mensaje}\n{logo_url}")

bot.run(os.getenv("DISCORD_TOKEN"))
