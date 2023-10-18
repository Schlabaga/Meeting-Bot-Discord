import discord
from discord import app_commands
from discord.ui import Select, View
from discord.ext import commands
from pymongo import ReturnDocument
import asyncio, datetime as dt, random
from classes import InscriptionModal, InscriptionView, NoProfileView, DateView, AccueilView
from config import TOKEN, villeListe, funReponseDict, likesGifs, EmbedColor, dbuser, dbbot,dbserver, GUILD

bot = commands.Bot(command_prefix="!", intents= discord.Intents.all())

#HEURE FR

heure = dt.datetime.utcnow()+dt.timedelta(hours=1)

#INITIALISATION DE L'EMBED NOPROFIL  

async def SuppMsg(msg, scds= 1):
  await asyncio.sleep(scds)
  await msg.delete()

#TACHES A FAIRE CHAQUE HEURE (SYNCHRO VILLES PROFILS + SUPPRESSION DES SALONS DE DATE AYANT UNE DATE SUPERIEURE A 1 SEMAINE) 

async def defaultServerUpdate(guildID):
    dbserver.server.update_one({"serverID":guildID.id}, {"$set":{
                                                                "servername":guildID.name,
                                                                "rolebienvenue":None,
                                                                "salonbienvenue":None,
                                                                "salonnotifs":None,
                                                                "salonselfie":None,
                                                                "salondate":None,
                                                                "quoifeur":False,
                                                                
                                                                "villesync":True,
                                                                "salonlogbot":None,
                                                                "salonchat":None,
                                                                "saloninscription":None,
                                                                "categoriedate":None,
                                                                "faceverification": False,
                                                                }},upsert=True)
    

async def tasksOneHour():

    botServers = bot.guilds
    nbrServeurs = 0
    guild = bot.get_guild(GUILD)

    for i in botServers:

        nbrServeurs +=1
    
    if nbrServeurs == 1:
        guild = botServers[0]

    if nbrServeurs >1:

        if GUILD != None:

            try:
                guild = bot.get_guild(GUILD)

            except:
                print("Je n'arrive pas à accéder au serveur entré dans /config")
                return
            
        else:
            print("Merci de définir le serveur principal dans /config")
            
    datas = dbserver.server.find_one({"serverID":guild.id})

    while True:

        if datas:

            try:

                categorieVille = datas["categorievilles"]
                categorieDate = bot.get_channel(datas["categoriedate"])

                if categorieDate != None:

                    salonsDate = categorieDate.channels

                    for salon in salonsDate:

                        print(salon.created_at)

                        if dt.datetime.fromtimestamp(salon.created_at.timestamp()) < dt.datetime.now() - dt.timedelta(weeks=1): #SI LE SALON EST PLUS VIEUX QUE 1 SEMAINES, LE SUPPRIMER
                            
                            await salon.delete()
                            
                            # ENVOYER UN MSG AUX FLIRTERS

                        else:

                            pass

                if categorieVille and datas["villesync"]==True:

                    category = bot.get_channel(categorieVille)

                    for channel in category.channels:

                        villeATrouver = channel.topic
                        userVilles = dbuser.user.find_one({"villeName":villeATrouver})
                        
                        if userVilles:

                            if "public" in userVilles:

                                envoyer = True

                                if "posted" in userVilles:
                                    
                                    if userVilles["posted"] !=None and not userVilles["posted"] < dt.datetime.now() - dt.timedelta(weeks=4):

                                        envoyer = False
                                else:

                                    dbuser.user.update_one({"userID": userVilles["userID"]}, 
                                                    
                                    {"$set":{"posted": dt.datetime.now()}}, True)


                                if userVilles["public"] == True and envoyer == True:

                                    user = guild.get_member(userVilles["userID"])
                            
                                    embed = discord.Embed(title=userVilles["prenom"])
                                    
                                    embed.set_footer(text=f"{guild.name}",icon_url=guild.icon)
                                    embed.add_field(name="Prénom",value= userVilles["prenom"])
                                    embed.add_field(name="Sexe",value= userVilles["sexe"])
                                    embed.add_field(name="Age",value=userVilles["age"])
                                    embed.add_field(name="Ville",value=userVilles["villeName"])
                                    embed.add_field(name="Insta",value=userVilles["insta"])
                                    embed.set_footer(text=guild.name,icon_url=guild.icon)

                                    if userVilles["selfie"]:
                                        embed.set_image(url=userVilles["selfie"])

                                    embed.set_thumbnail(url=user.avatar)

                                    msg = await channel.send(embed=embed)
                                    await msg.add_reaction("💖")

                                    dbuser.user.update_one({"userID": user.id}, 
                                                    
                                    {"$set":{"posted": dt.datetime.now()}}, True)

                else:

                    print("Catégorie invalide ou synchronisation désactivée")
                    pass

                            
            except KeyError as e:
                print(str(e))
                print("Certains salons n'ont pas encore été définis dans la database.²")


        else:
            await defaultServerUpdate(guildID=guild)          

                        
        await asyncio.sleep(3600)
    


"""async def syncGuilds(bot):

    for guild in bot.guilds:
        print(guild)
        
        if not dbbot.serverlist.find({"listservers":{"$in":[guild.id]}}):

            dbserver.serverwelcome.update_one({"serverID":guild.id},{"$set":{
                                                                    "servername":guild.name,
                                                                    "rolebienvenue":None,
                                                                    "salonbienvenue":None,
                                                                    "salonnotifs":None,
                                                                    "salonselfie":None,
                                                                    "salondate":None,
                                                                    "quoifeur":False,
                                                                    
                                                                    "villesync":True,
                                                                    "salonlogbot":None,
                                                                    "salonchat":None,
                                                                    "saloninscription":None,
                                                                    "categoriedate":None,
                                                                    "faceverification": False,
                                                                    }},upsert=True)
            
            dbbot.serverlist.update_one({"servers":"servers"},{'$push': {'listservers':guild.id }}, upsert = True)


"""

class Bot(commands.Bot):

    def __init__(self):

        intents = discord.Intents.all()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('+'), intents=intents)

    async def setup_hook(self) -> None:
        self.add_view(AccueilView())
        self.add_view(InscriptionView())
        self.add_view(DateView())


    async def on_ready(self):

        # dbbot.botfiles.update_one({"botID":bot.user.id},{"$set":{"botname":bot.user.name}}, upsert=True)

        print("--------------------------------------------")
        print(f"{bot.user.name} est prêt à être utilisé!")
        print("--------------------------------------------")
        
        try:
            #SYNCRHONISATION DES COMMANDES SLASH / CONTEXT MENU
            # await syncGuilds(bot)
            synced= await bot.tree.sync()

            print(f"Synchronisé {len(synced)} commande(s)")
            print("--------------------------------------------")


        except Exception as e:
            print(e)
  
        await bot.loop.create_task(tasksOneHour())
        
bot = Bot()



@bot.event
async def on_guild_join(guild): #INITIALISATION DE LA DATABASE DU SERVEUR REJOINT 

    n =0

    for serveur in bot.guilds:
        n+= 1
    
    if n > 1:
        await guild.leave() #BOT PAS ENCORE AU POINT POUR ETRE DANS PLUS D'1 SERV (PROBLEMES DE DB)

    if not dbserver.server.find_one({"serverID":guild.id}):
        UserDataBase = dbserver.server.update_one({"serverID":guild.id},{"$set":{
                                                                          "servername":guild.name,
                                                                          "rolebienvenue":None,
                                                                          "salonbienvenue":None,
                                                                          "salonnotifs":None,
                                                                          "salonselfie":None,
                                                                          "salondate":None,
                                                                          "quoifeur":False,
                                                                          
                                                                          "villesync":True,
                                                                          "categorievilles":None,
                                                                          "salonlogbot":None,
                                                                          "salonchat":None,
                                                                          "saloninscription":None,
                                                                          "categoriedate":None,
                                                                          "faceverification": False,
                                                                        }},upsert=True)

    print(f"J'ai rejoint le serveur {guild.name}!")


@bot.event
async def on_member_join(member:discord.Member):
    
    guild = member.guild
    
    ServerDataBase = dbserver.server.find_one({"serverID":guild.id})
    if "saloninscription" in ServerDataBase :
        if ServerDataBase["saloninscription"] !=None:
            channel=bot.get_channel(ServerDataBase["saloninscription"])
            msg = await channel.send(member.mention)
            await SuppMsg(msg)


    if not dbuser.user.find_one({"userID":member.id}):
        UserDataBase = dbuser.user.update_one({"userID":member.id},{"$set":{
                                                                        "userName":member.name,"public":False,
                                                                        "profile":False,
                                                                        "age":None,
                                                                        "insta":None,
                                                                        "prenom":None,
                                                                        "presentation":None,
                                                                        "sexe":None,
                                                                        "date":[None,None],
                                                                        "likeurs":None,
                                                                        "selfie":None,
                                                                        "date_creation": str(member.created_at.date())
                                                                        }},upsert=True)



@bot.event
async def on_member_remove(member: discord.Member):
    
    guild = member.guild
    serverDataBase = dbserver.server.find_one({"serverID":guild.id})

    if "salonlogbot" in serverDataBase:

        if serverDataBase["salonlogbot"] !=None:

            try:

                salonLogs = await guild.get_channel(serverDataBase["salonlogbot"])
                await salonLogs.send(f"{member.mention} a quitté le serveur ({member.id}).")

            except:

                print("Salon logs invalide")



@bot.event
async def on_message(message): #EVENEMENT POUR CATCH TOUS LES MESSAGES

    if not message.author.bot:

        dict = dbserver.server.find_one({"serverID":message.guild.id})
        channelSelfie = bot.get_channel(dict["salonselfie"])

        if dict:

            if dict["quoifeur"] ==True: #FONCTION POUR REPONDRE QUOIFEUR ETC

                for keys in funReponseDict.keys():

                    if type(keys) != tuple:

                        if message.content.lower().endswith(keys):
                            
                            item =random.choice(funReponseDict.get(keys))

                            await message.reply(item)

                    elif len(keys) >1: 

                        for i in keys:
                            
                            if message.content.lower().endswith(i):
                                
                                item =random.choice(funReponseDict.get(keys))

                                await message.reply(item)

        if message.channel == channelSelfie: #STOQUER LES PHOTO ENVOYES DANS LE SALON SELFIE DANS LA DATABASE

            if message.attachments:

                await message.add_reaction("💖")

                attachment = message.attachments[0]

                dbuser.user.update_one({"userID": message.author.id}, 
                                    
                {"$set":{"selfie": attachment.url}}, True)

            else:
                if message.author.id != bot.user.id:
                    
                    msg = await channelSelfie.send(f'{message.author.mention}, tu ne peux envoyer que des images ici, désolé!')
                    await message.delete()
                    await SuppMsg(msg,2)
                    

UserNoProfileEmbed = discord.Embed(title =f"Qui es-tu?", description="Oh, oh... un inconnu au bataillon? Tu n'as pas de profil, vas vite t'inscrire dans le \
                                   salon <#1072554218721919007> ou appuie sur le bouton ci-dessous!")

UserNoProfileEmbed.timestamp = heure
CibleNoProfileEmbed = discord.Embed(title =f"Qui est-ce?", description=f"Oh, oh... cet utilisateur n'a pas de profil! Vas vite lui dire d'en créer un dans le salon <#1072554218721919007>!")
CibleNoProfileEmbed.timestamp = heure



#SETUP LES FONCTIONNALITES PREMIERES DU SERVEUR



@bot.tree.command(name="configbienvenue", description="Installe les prérequis du bot (bienvenue)")
@app_commands.checks.has_permissions(administrator=True)
async def setupbienvenue(i: discord.Interaction, salonbienvenue: discord.TextChannel, rolebienvenue:discord.Role, salongeneral: discord.TextChannel):

    guild= i.guild  
    desc = ""

    serverConfig = dbserver.server.find_one_and_update({"serverID": guild.id }, {"$set":{"salonbienvenue": salonbienvenue.id, "rolebienvenue": rolebienvenue.id,
                                                                                "salonchat":salongeneral.id}},return_document=ReturnDocument.AFTER, upsert=True)  

    for cle in serverConfig.keys():
        
        valeur = serverConfig[cle]
        desc = f"{desc}\n・`{cle}`:{valeur}"

    embed= discord.Embed(title="Données modifiées:", description=desc)
    embed.set_footer(text=guild.name, icon_url=guild.icon)

    await i.response.send_message(embed=embed, ephemeral=True)



@bot.tree.command(name="configinteractions", description="Installe les prérequis du bot (interactions)")
@app_commands.checks.has_permissions(administrator=True)
async def configinteractions(i: discord.Interaction, salonselfie:discord.TextChannel,
                            salondate: discord.TextChannel, salonnotifs: discord.TextChannel, saloninscription: discord.TextChannel, 
                            categorievilles: discord.CategoryChannel, categoriedate:discord.CategoryChannel):

    guild= i.guild
    desc = ""

    serverConfig = dbserver.server.find_one_and_update({"serverID": guild.id }, {"$set":{
                                                                                 "salonselfie":salonselfie.id, "salondate":salondate.id,"salonnotifs":salonnotifs.id,
                                                                                   "saloninscription":saloninscription.id, "categorievilles":categorievilles.id,
                                                                                   "categoriedate": categoriedate.id}}, 
                                                                                   upsert=True, return_document=ReturnDocument.AFTER)  

    for cle in serverConfig.keys():
        
        valeur = serverConfig[cle]
        
        desc = f"{desc}\n・`{cle}`:{valeur}"

    embed= discord.Embed(title="Données modifiées:", description=desc)
    embed.set_footer(text=guild.name, icon_url=guild.icon)

    await i.response.send_message(embed=embed, ephemeral=True)



@bot.tree.command(name="configbot", description="Installe les prérequis du bot (bot)")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(funreponses =[
    discord.app_commands.Choice(name="Activer les réponses fun (quoifeur etc)", value=True),
    discord.app_commands.Choice(name="Désactiver les réponses auto fun", value= False)
])
@app_commands.choices(villesync =[
    discord.app_commands.Choice(name="Activer la synchronisation des profils dans les salons villes", value=True),
    discord.app_commands.Choice(name="Désactiver la synchronisation des profils dans les salons villes", value= False)
])
async def configbot(i: discord.Interaction, salonlogbot: discord.TextChannel, funreponses: discord.app_commands.Choice[int],villesync:discord.app_commands.Choice[int] ):

    guild= i.guild
    desc=""
    

    serverConfig = dbserver.server.find_one_and_update({"serverID": guild.id }, {"$set":{"quoifeur": funreponses.value,
                                                                                "salonlogbot":salonlogbot.id, 
                                                                                "villesync":villesync.value}}, upsert=True, return_document=ReturnDocument.AFTER)  


    for cle in serverConfig.keys():
        
        valeur = serverConfig[cle]
        
        desc = f"{desc}\n・`{cle}`:{valeur}"

    embed= discord.Embed(title="Données modifiées:", description=desc)
    embed.set_footer(text=guild.name, icon_url=guild.icon)

    await i.response.send_message(embed=embed, ephemeral=True)



#FAIRE APPARAITRE FORMULAIRE INSCRIPTION

@bot.tree.command(name="inscription", description="Permet d'enregistrer ton profil pour commencer ton aventure!")
async def inscription(interaction:discord.Interaction):

    await interaction.response.send_modal(InscriptionModal())
    


#PANEL D'INSCRIPTION

@bot.tree.command(name="setinscription", description="Envoie le message d'inscription")
@app_commands.checks.has_permissions(administrator=True)
async def setinscription(interaction: discord.Interaction, channel: discord.TextChannel):

    guild = interaction.guild

    infosEmbed = discord.Embed(title= "Inscris-toi!", color= EmbedColor, description="Pour pouvoir trouver des personnes qui te **correspondent** et enregistrer ton **profil**, \
                               Meebot a besoin d'informations (non sensibles), t'as juste à **remplir le formulaire** ci-dessous!")
    infosEmbed.set_footer(text=guild.name,icon_url=guild.icon)
    infosEmbed.set_image(url="https://media.giphy.com/media/HGfVgWlpaA9uj4U5uf/giphy.gif")

    await channel.send(embed=infosEmbed , view= InscriptionView())
    await interaction.response.send_message("Le message d'inscription a bién été défini!",ephemeral=True)


#PANEL DE DATES

@bot.tree.command(name="setdate", description="Envoie le panel des date")
@app_commands.checks.has_permissions(administrator=True)
async def setdate(interaction: discord.Interaction, channel: discord.TextChannel =None):

    if not channel:
        channel = interaction.channel

    guild = interaction.guild

    infosEmbed = discord.Embed(title= "Tu veux date quelqu'un?", color= EmbedColor, description="Tout ce que t'as à faire, c'est sélectionner un utilisateur ci-dessous!")
    infosEmbed.set_footer(text=guild.name,icon_url=guild.icon)
    infosEmbed.set_image(url="https://media.giphy.com/media/Rl2C91kYPgq4IHj8GN/giphy.gif")

    await channel.send(embed=infosEmbed , view= DateView())
    await interaction.response.send_message("Le message d'inscription a bien été défini!",ephemeral=True)


#ACTIVER / DESACTIVER ROLE BIENVENUE AUTO 


#SYNCHRONISATION ET ENVOI DES PROFILS DE CHACUN AYANT **SPECIFIE UNE VILLE** ET UN PROFIL **PUBLIC**, ANNEXE DE LA FONCTION "tasksOneHour()"

@bot.tree.command(name="villesync", description="synchronise les villes des utilisateurs")
@app_commands.checks.has_permissions(administrator=True)
async def syncVillesCmd(i: discord.Interaction , category: discord.CategoryChannel):
    
    guild = i.guild

    database = dbserver.server.find_one({"serverID":guild.id})
    category = guild.get_channel(database["categorievilles"])
    
    await i.response.defer()
    await i.followup.send(f"Les profils sont en cours d'envoi... <#{category.id}>", ephemeral=True)

    for channel in category.channels:

        villeATrouver = channel.topic
        userVille = dbuser.user.find({"villeName":villeATrouver})

        for userDoc in userVille:

            if "public" in userDoc:

                envoyer = True

                if "posted" in userDoc:
                    
                    if userDoc["posted"] !=None and not userDoc["posted"] < dt.datetime.now() - dt.timedelta(weeks=4):

                        envoyer = False

                else:

                    dbuser.user.update_one({"userID": userDoc["userID"]}, 
                                    
                    {"$set":{"posted": dt.datetime.now()}}, True)


                if userDoc["public"] == True and envoyer ==True:

                    user = guild.get_member(userDoc["userID"])
            
                    embed = discord.Embed(title=userDoc["prenom"])
                    
                    embed.set_footer(text=f"{guild.name}",icon_url=guild.icon)
                    embed.add_field(name="Pseudo",value= user.mention)
                    embed.add_field(name="Sexe",value= userDoc["sexe"])
                    embed.add_field(name="Age",value=userDoc["age"])
                    embed.add_field(name="Présentation",value=userDoc["presentation"])
                    embed.add_field(name="Ville",value=userDoc["villeName"])
                    embed.add_field(name="Insta",value=userDoc["insta"])
                    embed.set_footer(text=guild.name,icon_url=guild.icon)

                    if userDoc["selfie"]:
                        embed.set_image(url=userDoc["selfie"])

                    embed.set_thumbnail(url=user.avatar)

                    msg = await channel.send(embed=embed)
                    await msg.add_reaction("💖")

                    dbuser.user.update_one({"userID": user.id}, 
                                    
                    {"$set":{"posted": dt.datetime.now()}}, True)


    await i.followup.send('Importation terminée!', ephemeral=True)



#SETUP LES 20 TAGS DISPOS DU FORUM DU SERVEUR (20 PREMIERES VILLES)

@bot.tree.command(name="setuptags", description="Setup les tags d'un forum")
@app_commands.checks.has_permissions(administrator=True)
async def setuptags(interaction:discord.Interaction, forum :discord.ForumChannel):

    listeTags = []

    for tag in villeListe[0:20]:
        listeTags.append(discord.ForumTag(name=tag.capitalize(),emoji=None))
        
    await forum.edit(available_tags=listeTags)
    
    await interaction.response.send_message("Les tags ont bien été ajouté au forum", ephemeral=True)



#COMMANDE SETUP CATEGORIE VILLES (50)

@bot.tree.command(name="setup", description="Setup les villes")
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction:discord.Interaction, rolemembre:discord.Role):

    guild = interaction.guild

    categorie = await guild.create_category_channel(name="VILLES")

    dbserver.server.update_one({"serverID":guild.id}, {"$set":{"categorievilles":categorie.id}}, upsert=True)

    await categorie.set_permissions(rolemembre,read_messages=True,send_messages=False, read_message_history =True)
    await categorie.set_permissions(guild.default_role, view_channel=False, read_messages=False, connect=False, send_messages=False)

    await interaction.response.send_message(f"Chargement... <#{categorie.id}>", ephemeral=True)

    for channel in villeListe:
        salon = await guild.create_text_channel(name=f'🔰・{channel}', category=categorie, topic= channel.lower())
        await salon.edit(sync_permissions=True) 


#COMMANDE SUPPR CATEGORIE ET SON CONTENU

@bot.tree.command(name="deletecategory", description="Supprime une catégorie et ses salons")
@app_commands.checks.has_permissions(administrator=True)
async def suppr(i: discord.Interaction, categorie: discord.CategoryChannel):

    await i.response.send_message("Chargement... Les salons de la catégorie `{}` vont être supprimés".format(categorie.name), ephemeral=True)

    for channel in categorie.channels:
        await channel.delete()
        await asyncio.sleep(0.20)
    await categorie.delete()



#COMMANDE A SETUP


"""
db.user.update_many(
        {},
        {"$set":
            {
                "posted": None
            }
        },upsert=True)

"""




@bot.tree.command(name="updatedb", description="Met à jour la db en cas de crash du bot")
@app_commands.checks.has_permissions(administrator=True)
async def updatedb(interaction: discord.Interaction):

  guild = interaction.guild
  memberDefaultDict= {}


  for user in guild.members:

    if not user.bot:

        memberDefaultDict ={"selfie":None, "smashs":None, "public":False, "age":None, "insta":None, "prenom": None,\
        "presentation":None, "profile":False, "sexe":None, "userName":user.name, "public": False, "villeName":None, "villeID":None, "posted":None, "date":[None,None]}

        userDatas = dbuser.user.find_one({"userID":user.id})

        if userDatas:

            for localKey in memberDefaultDict:

                if localKey in userDatas:

                    pass

                else:

                    dbuser.user.update_one({"userID":user.id}, {"$set":{localKey:memberDefaultDict.get(localKey)}}, upsert=True)

        else:

            dbuser.user.update_one({"selfie":None, "smashs":None, "public":False, "age":None, "insta":None, "prenom": None,\
        "presentation":None, "profile":False, "sexe":None, "userName":user.name, "public": False, "villeName":None, "villeID":None, "posted":None, "date":[None,None]})


  for serveur in bot.guilds:

    serverDefaultDict = {
        "servername":serveur.name,
        "rolebienvenue":None,
        "salonbienvenue":None,
        "salonnotifs":None,
        "salonselfie":None,
        "salondate":None,
        "quoifeur":False,
        
        "villesync":True,
        "categorievilles":None,
        "salonlogbot":None,
        "salonchat":None,
        "saloninscription":None,
        "categoriedate":None,
        "faceverification": False,
    }
    
    serverDatas = dbserver.server.find_one({"serverID":serveur.id})

    if serverDatas:

      for defaultKey in serverDefaultDict:

        if defaultKey in serverDatas:

          pass
          
        else:

          dbserver.server.update_one({"serverID":serveur.id}, {"$set":{defaultKey:serverDefaultDict.get(defaultKey)}}, upsert=True)

    else:

      dbserver.server.update_one({"serverID":serveur.id}, {"$set":{
        "servername":serveur.name,
        "rolebienvenue":None,
        "salonbienvenue":None,
        "salonnotifs":None,
        "salonselfie":None,
        "salondate":None,
        "quoifeur":False,
        "villesync":True,
        "categorievilles":None,
        "salonlogbot":None,
        "salonchat":None,
        "saloninscription":None,
        "categoriedate":None,
        "faceverification": False,
    }
        }, upsert=True)

  await interaction.response.send_message("Les différentes db ont été mises à jour", ephemeral=True)






#DATE UN UTILISATEUR

@bot.tree.context_menu(name='Date')
@app_commands.checks.cooldown(3, 45.0, key=lambda i: (i.guild_id, i.user.id))
async def date(interaction: discord.Interaction, cible: discord.User):

    #SETUP PANEL DE CHOIX

    select = Select(options=[
    discord.SelectOption(label="Accepter", emoji="✔️", description="Accepte le date (si t en couple tu romps)"),
    discord.SelectOption(label="Refuser", emoji= "❌", description="Refuse le date")
    ], placeholder="Attention, tu ne peux faire ça qu'une fois tous les 7j") 
    
    guild = interaction.guild

    serverDict = dbserver.server.find_one({"serverID":guild.id})
    salonNotifs = guild.get_channel(serverDict["salonnotifs"])
    categorieDate = guild.get_channel(serverDict["categoriedate"])

    async def select_callback(interaction):

        if interaction.user == cible:

            if select.values[0] == "Accepter":

                await interaction.message.delete()

                embedOK = discord.Embed(title="Date accepté!", description=f"Bravo! {cible.mention} et {user.mention} sont maintenant en flirt!")
                #embedOK.set_footer(icon_url=guild.icon, text=guild.name)

                await interaction.response.send_message(embed = embedOK)

                userDict = dbuser.user.find_one({"userID":user.id})
                cibleDict =dbuser.user.find_one({"userID":cible.id})
                dateField = cibleDict["date"]

                if dateField[0] != None:

                    idCocu = dateField[0]
                    userCocu = guild.get_member(idCocu)
                    dbuser.user.update_one({"userID":idCocu}, {"$set":{"date":[None,None]}})
                    await salonNotifs.send(f"{userCocu.mention}, ton flirt avec `{cible.mention}` prend fin :(")
            
                dateField = userDict["date"]

                if dateField[0] != None:

                    idCocu = dateField[0]
                    userCocu = guild.get_member(idCocu)
                    dbuser.user.update_one({"userID":idCocu}, {"$set":{"date":[None,None]}})
                    await salonNotifs.send(f"{userCocu.mention}, ton flirt avec `{user.name}` prend fin :(")
   
                dateChannel =  await guild.create_text_channel(name=f"💞・{cible.name} et {user.name}",topic= f"{user.id}+{cible.id}", category=categorieDate)
                
                await dateChannel.set_permissions(guild.default_role,read_messages = False, view_channel= False)
                await dateChannel.set_permissions(user,read_messages = True, view_channel= True,send_messages = True, read_message_history = True)
                await dateChannel.set_permissions(cible,read_messages = True, view_channel= True, send_messages = True , read_message_history = True)

                dbuser.user.update_one({'userID': user.id},       
                    {
                    "$set":
                    {
                        "date": (cible.id,dt.datetime.utcnow()+dt.timedelta(hours=1))
                    }
                    }, True)

                dbuser.user.update_one({'userID': cible.id},       
                    {
                    "$set":
                    {
                        "date": (user.id,dt.datetime.utcnow()+dt.timedelta(hours=1))
                    }
                    }, True)
                

                await salonNotifs.send(f'{user} a date {cible}')
                await dateChannel.send(f'{user.mention} {cible.mention}')


            else:
                await interaction.message.delete()
                embedRefuser = discord.Embed(title="Oups, desolé... :/", description=f"Malheureusement, ton date a été refusé par {interaction.user}, t'inquiète pas, la prochaine fois sera la bonne!")
                embedRefuser.set_footer(icon_url=guild.icon, text=guild.name)  
                await interaction.response.send_message(embed = embedRefuser, ephemeral = True)

        elif interaction.user == user:
            await interaction.response.send_message(f"{user.mention} t'es arrogant ou en manque d'affection? Tu voulais vraiment accepter ton propre date?", ephemeral = True)

        else:
            await interaction.response.send_message(f"{interaction.user.mention}Quel culot! Tu voulais vraiment accepter un date qui ne t'étais pas adressé?",ephemeral = True)
    

    select.callback = select_callback
    selectView = View(timeout=180)
    selectView.clear_items
    selectView.add_item(select)

    user = interaction.user

    def updateUser(userID):

        dbuser.user.update_one({"userID":userID}, {"$set":{"date":[None,None]}})


    if not cible.bot:

        if interaction.user != cible:

            userInfos = dbuser.user.find_one({'userID': user.id})
            cibleInfos = dbuser.user.find_one({"userID" : cible.id})

            if userInfos:

                if cibleInfos:

                    if "date" in userInfos:

                        if "date" in cibleInfos:

                            dateBool = True
                            dictUser = userInfos["date"]
                            dictCible = cibleInfos["date"]

                            if (not dictUser[1] or dictUser[1] == None or (dictUser[0] != cible.id and dictUser[1] < dt.datetime.now() - dt.timedelta(days=7))) and \
                                (not dictCible[1] or dictCible[1] == None or (dictUser[0] != cible.id and dictCible[1] < dt.datetime.now() - dt.timedelta(days=7))):
                                    
                                    
                                    propositionEmbed = discord.Embed(title="Quelle bonne nouvelle!", description=f"Hey, {cible.mention}, un date vous est proposé par {user.mention}, acceptez-vous?")
                                    propositionEmbed.set_footer(text = guild.name, icon_url= guild.icon)

                                    await interaction.response.send_message(content=cible.mention,embed = propositionEmbed,view=selectView)
                                
                            else:
                                
                                if dictUser[0] == cible.id:
                                    await interaction.response.send_message(f"Tu es déjà en flirt avec {cible.mention}", ephemeral=True)

                                elif dictUser[1] != None and dictUser[1] > dt.datetime.now() - dt.timedelta(days=7):
                                    temps = dt.datetime.now()- dt.timedelta(days=7)
                                    tempsDef = dictUser[1] - temps

                                    tempsEmbedUser = discord.Embed(title="Pas si vite!", description=f"Quelles sont ces manières? Tu dois attendre 7j après \
                                                               ton précédent date pour en refaire un! Il te reste `{tempsDef}` à attendre") 
                                    
                                    tempsEmbedUser.set_footer(text = guild.name, icon_url= guild.icon)
                                                                      
                                    await interaction.response.send_message(embed = tempsEmbedUser, ephemeral=True)

                                elif dictCible[0] == user.id:
                                    await interaction.response.send_message(f"Tu es déjà en flirt avec {cible.mention}", ephemeral=True)
                   
                                elif dictCible != None and dictCible[1] > dt.datetime.now() - dt.timedelta(days=7):
                                    temps = dt.datetime.now()- dt.timedelta(days=7)
                                    tempsDef = dictCible[1] - temps

                                    tempsEmbed = discord.Embed(title="Pas si vite!", description=f"La personne que tu demandes en date doit attendre `{tempsDef}` pour date quelqu'un") 
                                    tempsEmbed.set_footer(text = guild.name, icon_url= guild.icon)

                                    await interaction.response.send_message(embed = tempsEmbed, ephemeral=True)
                        else:
                            await interaction.response.send_message("Erreur de database, rééssayez dans quelques instants", ephemeral=True)
                            updateUser(userID=cible.id)
                    else:
                        await interaction.response.send_message("Erreur de database rééssayez dans quelques instants", ephemeral=True)
                        updateUser(userID=user.id)
                else:
                    await interaction.response.send_message(f"Oh, oh... l'heureux(se) élu(e) {cible.mention} n'a pas configuré son profil... Vas vite lui dire d'en faire un!", ephemeral=True)
            else:
                await interaction.response.send_message(f"Tu comptes aller à un date tout nu? Crée d'abord un profil!", ephemeral=True, view= NoProfileView())
        else:
            await interaction.response.send_message(f"Quelle arrogance! Tu comptais te date toi-même??", ephemeral=True)
    else:
        await interaction.response.send_message(f'Tu ne peux pas date un bot! Les pauvres ne peuvent pas éprouver l\'amour', ephemeral=True)


@date.error
async def on_public_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown) :
        await interaction.response.send_message(f"La commande est en cooldown, merci de rééssayer dans `{round(error.retry_after) } secondes`", ephemeral=True)



@bot.tree.command(name="accueilsetup", description="Envoie le message d'accueil")
@app_commands.checks.has_permissions(administrator=True)
async def accueilsetup(interaction: discord.Interaction, channel : discord.TextChannel = None):

    guild = interaction.guild

    embed = discord.Embed(title="Visite guidée", description="Choisis dans le menu de sélection ci-dessous ce que tu comptes faire dans le serveur!")
    embed.set_image(url="https://cdn.discordapp.com/attachments/726746146961096774/1079354028519071764/Composition_1_5.gif")
    embed.set_footer(icon_url=guild.icon, tw=guild.name)

    if channel:
        await channel.send(embed = embed, view=AccueilView())
        await interaction.response.send_message(f"L'embed de visite guidée a bien été envoyé dans <#{channel.id}>", ephemeral=True)

    else:
        await interaction.response.send_message(embed = embed, view=AccueilView())



#COMMANDE POUR SUPPRIMER SON PROFIL, CLEAR LES INFOS SENSIBLES

@bot.tree.command(name="clearprofile", description="Supprime toutes tes informations")
async def clearprofile(interaction: discord.Interaction, cible:discord.Member):

    utilisateur = interaction.user

    if cible:
        if utilisateur.guild_permissions.administrator:

            if dbuser.user.find_one({"userID":utilisateur.id}):

                dbuser.user.update_one({"userID": cible.id},
                {"$set":{
                "profile":False,
                "insta":None,
                "sexe":None,
                "presentation":None,
                "age":None,
                "prenom":None,
                "selfie":None
                }},True)

                await interaction.response.send_message(f'Le profil de {cible.mention} a bien été supprimé!', ephemeral=True)

        else:
            await interaction.response.send_message(f"Désolé, tu n'as pas les permissions pour utiliser cette commande.", ephemeral=True)
             
    else:
        if dbuser.user.find_one({"userID":utilisateur.id}):

            dbuser.user.update_one({"userID": utilisateur.id},
                {"$set":{
                "profile":False,
                "insta":None,
                "sexe":None,
                "presentation":None,
                "age":None,
                "prenom":None,
                "selfie":None
                }},True)
            
            await interaction.response.send_message(f'Ton profil a bien été supprimé!', ephemeral=True)

    #db.user.delete_one({"userID":utilisateur.id}) POUR SUPPRIMER L'UTILISATEUR 



#ACTIVE / DESACTIVE LES REPONSES AUTO #FUN

@bot.tree.command(name="setquoifeur", description="Active / désactive les réponses automtiques (quoi/feur etc)")
@app_commands.checks.has_permissions(administrator=True)
async def quoifeur(interaction: discord.Interaction):

    serverDict= dbserver.server.find_one({"serverID":interaction.guild.id})

    if serverDict:
        if "quoifeur" in serverDict:

            quoifeurAutorisation = serverDict["quoifeur"]

        else: 
            
            quoifeurAutorisation = True

        dbserver.server.update_one({"serverID": interaction.guild.id}, 
        {"$set":{"quoifeur": not quoifeurAutorisation}}, True)

        if quoifeurAutorisation == False:
            await interaction.response.send_message("Les réponses automatiques sont maintenant `activées`",ephemeral=True)
        
        if quoifeurAutorisation == True:
            await interaction.response.send_message("Les réponses automatiques sont maintenant `désactivées`", ephemeral=True)

    else:
        await interaction.response.send_message("Erreur de base de données!", ephemeral=True)


#COMMANDE QUI SWITCH ENTRE PROFIL PUBLIC/PRIVE

@bot.tree.command(name="confidentialite", description="Rend ton profil public/ privé")
@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
async def confidentialite(interaction: discord.Interaction):

    utilisateur= interaction.user
    userDict= dbuser.user.find_one({"userID":utilisateur.id})

    if userDict:
        if "public" in userDict:

            publicAutorisation = userDict["public"]

        else: 
            
            publicAutorisation = True

        dbuser.user.update_one({"userID": utilisateur.id}, 
        {"$set":{"public": not publicAutorisation}})

        if publicAutorisation == False:
            await interaction.response.send_message("Ton profil est maintenant `public`",ephemeral=True)
        
        if publicAutorisation == True:
            await interaction.response.send_message("Ton profil est maintenant `privé`", ephemeral=True)

    else:
        UserNoProfileEmbed.set_footer(icon_url= interaction.guild.icon, text=interaction.guild.name)
        await interaction.response.send_message(embed=UserNoProfileEmbed, ephemeral=True, view=NoProfileView())


@confidentialite.error
async def on_public_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown) :
        await interaction.response.send_message(f"La commande est en cooldown, merci de rééssayer dans `{round(error.retry_after) } secondes`", ephemeral=True)


#COMMANDE QUI MET A JOUR LA SITUATION DE QQUN (CELIB/EN COUPLE)

@bot.tree.command(name="situation", description="Célibataire ou en couple?")
@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
async def situation(interaction: discord.Interaction):

    utilisateur= interaction.user
    userDict = dbuser.user.find_one({"userID":utilisateur.id})

    if userDict:
        if "situation" in userDict:
            situation = userDict["situation"]
    

        else:
            situation= False

        dbuser.user.update_one({"userID": utilisateur.id}, 
        {"$set":{"situation": not situation}}, upsert=True)

        if situation == False:
            await interaction.response.send_message("Tu es maintenant `célibataire`",ephemeral=True)
        
        if situation == True:
            await interaction.response.send_message("Tu es maintenant `en couple`", ephemeral=True)
    
    else:
        UserNoProfileEmbed.set_footer(icon_url= interaction.guild.icon, text=interaction.guild.name)
        await interaction.response.send_message(embed=UserNoProfileEmbed, ephemeral=True, view=NoProfileView())

@situation.error
async def on_public_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"La commande est en cooldown, merci de rééssayer dans `{round(error.retry_after) } secondes`", ephemeral=True)



#PERMET D'AFFICHER LE PROFIL DE QQUN / DE SOI MEME + ERREUR AVEC CASSOULET, METTRE A JOUR

@bot.tree.context_menu(name='Profil')
@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
async def profile_context(interaction: discord.Interaction, cible:discord.Member):


    if cible and cible != interaction.user:
        
        user = cible
    
    else:   
        user = interaction.user

    if user.bot:
        await interaction.response.send_message("Oh,oh... on évite de stalker les bots!", ephemeral=True)
        return

    guild = interaction.guild
    stalker = False
    CibleNoProfileEmbed.set_footer(icon_url=guild.icon, text=guild.name)
    UserNoProfileEmbed.set_footer(icon_url=guild.icon, text=guild.name)


    if user != interaction.user:
        stalker = True
    
    profileDict=dbuser.user.find_one({"userID":user.id})

    if profileDict:

        if "profile" in profileDict:

            if profileDict["profile"] == True:

                titre ="titre"
                footer = "footer"

                publicAutorisation =""
                stalkerAutorise= False

                if "public" in profileDict:


                    if profileDict["public"] == True:
                        publicAutorisation = "Public" 
                    
                    if profileDict["public"] == False:
                        publicAutorisation = "Privé" 
                        
                    if stalker ==True and publicAutorisation == "Public":
                        stalkerAutorise= True
                        titre = f"Profil de {cible.name}  ({publicAutorisation})"
                        footer = f"{guild.name}・Demandé par {interaction.user}"
                    
                    if stalker == True and publicAutorisation =="Privé":
                        await interaction.response.send_message(f"Le profil de {user.mention} est privé, désolé")
                        pass

                    if  stalker == False:
                        titre = f"Mon profil ({publicAutorisation})"
                        footer = guild.name
                    
                    listeDisplay = ["prenom","sexe","age","ville","presentation","insta"]

                    description = ""

                    for item in listeDisplay:
                        try:
                            if profileDict[item] != None:
                                value =profileDict[item]
                                description = f"{description}\n・{item.capitalize()}: {value}"
                               
                        except KeyError:
                            pass
                    
                    if profileDict["date"][0] !=None:
                        userFlirt = guild.get_member(profileDict["date"][0])
                        if userFlirt:
                            description = f"{description}\n・Flirt: {userFlirt.mention}"

                    if description == "":
                        
                        await interaction.response.send_message(embed=CibleNoProfileEmbed, ephemeral=True)
                        return


                    embed = discord.Embed(title=titre, description=description)
                    embed.set_footer(text=f"{footer}",icon_url=guild.icon)

                    if "selfie" in profileDict:
                        if profileDict["selfie"] != None:
                            embed.set_image(url=profileDict["selfie"])

                    embed.set_thumbnail(url=user.avatar)

                    try:
                    
                        if stalker == False or stalkerAutorise== True:

                            await interaction.response.send_message(embed=embed, ephemeral=not stalker)
                        
                        else:
                    
                            await interaction.response.send_message("Vous n'êtes pas autorisé à consulter ce profil")
                
                    except KeyError as e:

                        print(e)
                        await interaction.response.send_message("Erreur, veuillez rééssayer!", ephemeral=True)
            else:
                if stalker:
                    
                    await interaction.response.send_message(embed=CibleNoProfileEmbed, ephemeral=True)

                else:
                    await interaction.response.send_message(embed=UserNoProfileEmbed, view=NoProfileView(), ephemeral=True)

        else: 

            dbuser.user.update_one({"userID": cible.id }, {"$set":{"public":False}}, upsert=True)
            await interaction.response.send_message("Cet utilisateur n'a pas spécifié la confidentialité de son profil. Par défaut, il est `privé`!", ephemeral=True)
                        
    else:
        if stalker:
            
            await interaction.response.send_message(embed=CibleNoProfileEmbed, ephemeral=True)

        else:
            await interaction.response.send_message("Oh, oh... un inconnu au bataillon? Tu n'as pas de profil, vas vite t'inscrire dans le\
                                                     salon <#1072554218721919007> ou en appuie sur le bouton ci-dessous!",view=NoProfileView(), ephemeral=True)

@profile_context.error
async def on_profile_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"La commande est en cooldown, merci de rééssayer dans `{round(error.retry_after) } secondes`", ephemeral=True)



#AFFICHER SON PROFIL

@bot.tree.command(name="profile", description="Affiche ton profil")
@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
async def profile(interaction: discord.Interaction, cible:discord.Member =None):

    if cible and cible != interaction.user:
        
        user = cible
    
    else:   
        user = interaction.user

    if user.bot:
        await interaction.response.send_message("Tu comptais stalker un bot là??", ephemeral=True)
        return

    guild = interaction.guild
    stalker = False

    UserNoProfileEmbed.set_footer(icon_url=guild.icon, text=guild.name)
    CibleNoProfileEmbed.set_footer(icon_url=guild.icon, text=guild.name)

    

    if user != interaction.user:
        stalker = True
    
    profileDict= dbuser.user.find_one({"userID":user.id})


    if profileDict:

        if "profile" in profileDict:

            if profileDict["profile"] == True:

                titre ="titre"
                footer = "footer"

                publicAutorisation =""
                stalkerAutorise= False

                if "public" in profileDict:

                    if profileDict["public"] == True:
                        publicAutorisation = "Public" 
                    
                    if profileDict["public"] == False:
                        publicAutorisation = "Privé" 
                        
                    if stalker ==True and publicAutorisation == "Public":
                        stalkerAutorise= True
                        titre = f"Profil de {cible.name}  ({publicAutorisation})"
                        footer = f"{guild.name}・Demandé par {interaction.user}"
                    
                    if stalker == True and publicAutorisation =="Privé":
                        await interaction.response.send_message(f"Le profil de {user.mention} est privé, désolé")
                        pass

                    if  stalker == False:
                        titre = f"Mon profil ({publicAutorisation})"
                        footer = guild.name
                    
                    listeDisplay = ["prenom","sexe","age","ville","presentation","insta"]

                    description = ""

                    for item in listeDisplay:
                        try:
                            if profileDict[item] != None:
                                value =profileDict[item]
                                description = f"{description}\n・{item.capitalize()}: {value}"
                    
                        except KeyError:
                            pass
                    
                    if profileDict["date"][0] !=None:
                        userFlirt = guild.get_member(profileDict["date"][0])
                        if userFlirt:
                            description = f"{description}\n・Flirt: {userFlirt.mention}"

                    if description == "":
                        await interaction.response.send_message(embed=CibleNoProfileEmbed, ephemeral=True)
                        return


                    embed = discord.Embed(title=titre, description=description)
                    embed.set_footer(text=f"{footer}",icon_url=guild.icon)

                    if "selfie" in profileDict:
                        if profileDict["selfie"] != None:
                            embed.set_image(url=profileDict["selfie"])

                    embed.set_thumbnail(url=user.avatar)

                    try:
                    
                        if stalker == False or stalkerAutorise== True:

                            await interaction.response.send_message(embed=embed, ephemeral=not stalker)
                        
                        else:
                    
                            await interaction.response.send_message("Vous n'êtes pas autorisé à consulter ce profil")
                
                    except KeyError as e:

                        print(e)
                        await interaction.response.send_message("Erreur, veuillez rééssayer!", ephemeral=True)
            else:
                if stalker:
                    await interaction.response.send_message(CibleNoProfileEmbed, ephemeral=True)

                else:
                    await interaction.response.send_message(embed=UserNoProfileEmbed,view=NoProfileView(), ephemeral=True)

        else: 

            dbuser.user.update_one({"userID": cible.id }, {"$set":{"public":False}}, upsert=True)
            await interaction.response.send_message("Cet utilisateur n'a pas spécifié la confidentialité de son profil. Par défaut, il est `privé`!", ephemeral=True)
                        
    else:
        if stalker:
            await interaction.response.send_message(embed=CibleNoProfileEmbed, ephemeral=True)

        else:
            await interaction.response.send_message(embed=UserNoProfileEmbed,view=NoProfileView(), ephemeral=True)



@profile.error
async def on_profile_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"La commande est en cooldown, merci de rééssayer dans `{round(error.retry_after) } secondes`", ephemeral=True)


#FONCTION DE SELECTION DE SA VILLE

@bot.tree.command(name="ville", description="Met à jour ta ville")
async def ville(i:discord.Interaction, ville: discord.TextChannel):

    guild = i.guild
    database = dbserver.server.find_one({"serverID":guild.id})
    category =  guild.get_channel(database["categorievilles"])
    desc = ""

    if ville not in category.text_channels:
        desc = "Ce salon ne correspond `pas` à une ville!"

    else:

        villeName = ville.topic

        dbuser.user.update_one({"userID": i.user.id }, {"$set":{"villeName":villeName.lower()}}, upsert=True)  
        dbuser.user.update_one({"userID": i.user.id }, {"$set":{"villeID":ville.id}}, upsert=True)  
        desc = f"Ta ville est la suivante: `{villeName.capitalize()}`"

    try:
        await i.response.send_message(desc, ephemeral=True)
        
    except discord.app_commands.errors.CommandInvokeError:
        return
    

#FONCTION PR METTRE A JOUR LES LIKES DE QQUN

def update_likes(userID, likeurID):
    
    listeLikeurs = dbuser.user.find_one({"userID":userID})
  
    if listeLikeurs:

        if "likeurs" in listeLikeurs:

            likeursRender= listeLikeurs["likeurs"]

            if likeurID in likeursRender:

                return False
            
            else:

                dbuser.user.update_one({'userID': userID}, {'$push': {'likeurs': likeurID}}, upsert = True)

                return True



#CONTEXT MENU LIKE

@bot.tree.context_menu(name='Liker')
@app_commands.checks.cooldown(10, 86400.0, key=lambda i: (i.guild_id, i.user.id))
async def like(interaction: discord.Interaction, message: discord.Message):

    
    user = interaction.user
    guild = interaction.guild
    servProfil = dbserver.server.find_one({"serverID":guild.id})
    salonSelfie = servProfil["salonselfie"]
    salon = guild.get_channel(salonSelfie)
    salonNotifs = guild.get_channel(1077339834106003467)
    

    if message.attachments:

        if interaction.channel == salon:
            
            if message.author != user:

                nbLikes = dbuser.user.find_one({"userID":message.author.id})

                if nbLikes:

                    updated = update_likes(message.author.id,user.id)

                    if updated == True:

                        if "likes" in nbLikes:
                            likesRender= nbLikes["likes"]
                            dbuser.user.update_one({"userID": message.author.id}, 
                            {"$set":{"likes": likesRender+1}})   
                        

                        else:
                            dbuser.user.update_one({"userID": message.author.id}, 
                            {"$set":{"likes": 1}})
                        
                        embed = discord.Embed(title="Like", description=f'{user} a liké une photo de {message.author.mention}!', color=EmbedColor)
                        embed.set_image(url=random.choice(likesGifs))
                        embed.set_footer(text = guild.name, icon_url=guild.icon)

                        try:

                            await message.author.send("Viens vite! Ta photo a été likée <#1077339834106003467>")

                        except:

                            pass

                        await salonNotifs.send(f'{user.mention} a liké une photo de {message.author.mention}!', embed=embed)
                        await interaction.response.send_message(f"La photo a bien été likée!", ephemeral=True)

                    
                    else: 
                        
                        await interaction.response.send_message(f'Tu as déjà liké cette personne!', ephemeral=True)

            else:
                
                await interaction.response.send_message(f'Tu ne peux pas liker ta propre photo!', ephemeral=True)
                
        else:

            await interaction.response.send_message(f'Tu ne peux liker que les selfies! <#{salonSelfie}>', ephemeral=True)

    else:

        await interaction.response.send_message(f'Tu ne peux pas liker un message sans image!', ephemeral=True)


@like.error
async def on_public_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"Tu ne peux que liker 10 fois par jour. La commande est en cooldown, merci de rééssayer dans\
                                                 `{str(dt.timedelta(seconds=round(error.retry_after))) }`", ephemeral=True)


bot.run(TOKEN)