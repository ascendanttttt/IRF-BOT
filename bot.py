import asyncio
import sys
import random
import os

# Forzar el selector de red clásico en Windows para evitar errores de red
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- MINI SERVIDOR WEB (Para mantener activo el puerto en Render) ---
app = Flask('')

@app.route('/')
def home():
    return "¡El bot de la IRF está activo y online 24/7!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- CONFIGURACIÓN DEL BOT ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Obligatorio para detectar cuando entran miembros
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

    roles_warn = {
        1: discord.utils.get(ctx.guild.roles, name="Warn 1"),
        2: discord.utils.get(ctx.guild.roles, name="Warn 2"),
        3: discord.utils.get(ctx.guild.roles, name="Warn 3"),
        4: discord.utils.get(ctx.guild.roles, name="Warn 4"),
        5: discord.utils.get(ctx.guild.roles, name="Warn 5"),
    }

    if not all(roles_warn.values()):
        await ctx.send("❌ Faltan roles por crear. Asegúrate de tener exactamente los roles: `Warn 1`, `Warn 2`, `Warn 3`, `Warn 4` y `Warn 5`.", delete_after=7)
        return

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
        if nivel_actual > 0:
            await member.remove_roles(roles_warn[nivel_actual])
        
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


# --- EVENTO DE BIENVENIDA ---

@client.event
async def on_member_join(member):
    if member.bot:
        return
        
    channel = member.guild.get_channel(1553140453216620746)
    if channel:
        mensaje = (
            f"¡Bienvenido/a {member.mention} a la **IRF │ International Roblox Federation │ S1**! ⚽🎉 "
            f"Qué bueno tenerte por acá. ¡Pasala bien y busca un equipo!"
        )
        
        logo_url = "https://media.discordapp.net/attachments/1553427240556040202/1553872946395746325/IRF.png"
        
        await channel.send(f"{mensaje}\n{logo_url}")


# --- ARRANCAR SERVIDOR WEB Y BOT ---

if __name__ == "__main__":
    keep_alive()
    client.run(os.getenv("DISCORD_TOKEN"))
