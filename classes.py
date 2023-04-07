import discord, datetime as dt
from discord import app_commands, ui
from discord.ui import View, Select
from discord.ext import commands
from config import EmbedColor, dbuser, dbbot, dbserver

bot = commands.Bot(command_prefix="!", intents= discord.Intents.all())

#CE FICHIER CONTIENT CHACUN DES PANELS QUI SONT CREES A PARTIR DE LA LIBRAIRIE discord.ui (View, Select)

class InscriptionModal(ui.Modal, title= "Inscription"):

    prenom = ui.TextInput(label='Ton prénom', style=discord.TextStyle.short, placeholder="Ne donne jamais ton nom de famille!", max_length= 30)
    sexe = ui.TextInput(label='Ton sexe', style=discord.TextStyle.short, placeholder="M/F", max_length=1)
    age = ui.TextInput(label='Ton age', style=discord.TextStyle.short, max_length=2, placeholder= "14-30 ans", )
    presentation = ui.TextInput(label='Courte présentation (passions, sports, hobby)', style=discord.TextStyle.long,min_length=45 ,max_length=150, placeholder="Passions / sports / hobbies")
    #situation = ui.TextInput(label='Situation amoureuse', style=discord.TextStyle.short, placeholder= "Célibataire/en couple" ,max_length=10)
    instagram = ui.TextInput(label='Ton instagram', style=discord.TextStyle.short, placeholder= "Facultatif", required=False ,max_length=30)


    async def on_submit(self, interaction: discord.Interaction):
    
        guild= interaction.guild
        utilisateur = interaction.user

        embedResponse=discord.Embed(title=f'Profil de {utilisateur.name}',
        color=EmbedColor)

        embedResponse.set_footer(text=guild.name,icon_url=guild.icon)
        embedResponse.add_field(name='Prénom',value=self.prenom)
        embedResponse.add_field(name="Sexe",value=self.sexe)
        embedResponse.add_field(name="Age",value=self.age)
        embedResponse.add_field(name="Description",value=self.presentation)
        embedResponse.add_field(name="Instagram",value=self.instagram)
        embedResponse.set_thumbnail(url=interaction.user.avatar)

        await interaction.response.send_message(embed=embedResponse, ephemeral=True)


        update = False

        if dbuser.user.find_one({'userID':utilisateur.id}):
            update= True

        dbuser.user.update_one({'userID': utilisateur.id},
            
            {
            "$set":
            {
            "userName": str(utilisateur.name),
            "prenom": str(self.prenom),
            "sexe": str(self.sexe),
            "age":str(self.age),
            "presentation":str(self.presentation),
            "insta":str(self.instagram),
            #"situation": str(self.situation),
            "profile" :True,
            "public" : False
            }
            }, True
        )          
        
        serverDatas = dbserver.server.find_one({"serverID":guild.id})
        logChannel  = guild.get_channel(serverDatas["salonlogbot"])

        if update == False and logChannel != None:
            
            await logChannel.send(f"{utilisateur.mention} s'est inscrit!", embed= embedResponse)   
            #await utilisateur.add_roles(discord.Object(id=1038932615912235109))
        
        if update == True and logChannel != None:
            await logChannel.send(f"{utilisateur.mention} a mis a jour son profil!", embed= embedResponse)   
            

#BOUTON

class DateButtons(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=60)


    @discord.ui.button(label="Accepter", style= discord.ButtonStyle.green,emoji= "✔️")
    async def boutonaccepter(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(title="Bravo!", description=f"Ton date a été accepté par {interaction.user}, félicitations!")
        
        await interaction.message.delete()
        await interaction.response.send_message(embed=embed)


    @discord.ui.button(label="Refuser", style= discord.ButtonStyle.red,emoji= "❌")
    async def boutonrefuser(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild

        embed = discord.Embed(title="Oups, desolé... :/", description=f"Malheuresement, ton date a été refusé par {interaction.user}, t'inquiète pas, la prochaine fois sera la bonne!")
        embed.set_footer(icon_url=guild.icon, text=guild.name)
        
        await interaction.message.delete()
        await interaction.response.send_message(embed=embed)


"""class ConfigView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.cooldown = commands.CooldownMapping.from_cooldown(3,60, commands.BucketType.member)


    @discord.ui.select( 
            
        placeholder = "Que souhaites-tu configurer?",
        min_values = 1, 
        max_values = 1,
        custom_id= "persistent_view:select",
        options = [ 
            discord.SelectOption(
                label="Interactions de bienvenue",
                description="Définis les salons/ roles de bienvenue",
                value="bienvenue",
                emoji="🗺️",
            ),
            discord.SelectOption(
                label="Interactions de relation",
                description="Définis les salons/ roles d'interaction",
                value="relations",
                emoji="📁"
            ),
            discord.SelectOption(
                label="Fonctionnalités du bot",
                description="Configure les fonctionnalités du bot",
                value="configbot",
                emoji="📣"
            ),
           discord.SelectOption(
                label="Poster mon selfie",
                description="A moi les minettes!",
                value="selfie",
                emoji="😎"
           )
        ]
    )


    async def select_callback(self, interaction: discord.Interaction, choix: discord.ui.Select) -> None:

        bucket = self.cooldown.get_bucket(interaction.message)
        retry = bucket.update_rate_limit()

        if retry:
            await interaction.response.send_message(f"Tu es en **cooldown**, rééssaye dans `{round(retry,1)} secondes`", ephemeral=True)
            return

        else:
            
            choice = choix.values[0]
            
            if choice == "bienvenue":

                salonBienvenue = discord.ui.select(cls= discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Choisis le salon de bienvenue") 
                salonInscription = discord.ui.select(cls= discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Dans quel salon les membres vont-ils s'inscrire?")
                salonChatGeneral = discord.ui.select(cls= discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Quel est le salon général?")
                roleBienvenue = discord.ui.select(cls= discord.ui.RoleSelect,  placeholder="Choisis le role de bienvenue")

                autoRoleChoice = discord.ui.select(
                    min_values = 1, 
                    max_values = 1,options=[
                                discord.SelectOption(
                                    label="Oui",
                                    description="Ajoute auto un role aux nvx membres",
                                    value="yesrole",
                                    emoji="✔️",
                                ),
                                discord.SelectOption(
                                    label="Non",
                                    description="N'ajoute aucun role aux nvx membres",
                                    value="norole",
                                    emoji="❌"
                                )],
                                
                                placeholder="Veux-tu assigner un role aux nouveaux membres?")

                await interaction.response.send_message(view=FavouriteGameSelect())

            if choice == "relations":

                salonDates = discord.ui.select(cls= discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Choisis le salon des dates") 
                salonNotifs = discord.ui.select(cls= discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Choisis le salon des notifs")
                salonSelfies = discord.ui.select(cls= discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Choisis le salon des selfies")
                categorieVille = discord.ui.select(
                    
                    min_values = 1, 
                    max_values = 1,options=[
                                discord.SelectOption(
                                    label="Oui",
                                    description="Crée une catégorie avec les 50 1eres villes FR",
                                    value="yesvilles",
                                    emoji="✔️",
                                ),
                                discord.SelectOption(
                                    label="Non",
                                    description="Certaines fonctionnalités seront désactivées (villesync)",
                                    value="novilles",
                                    emoji="❌"
                                )],
                                
                                placeholder="Veux-tu configurer la catégorie villes?")



            if choice == "configbot":

                salonLogBot = discord.ui.select(cls= discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Choisis le salon où apparaîtront les logs du bot")
                quoiFeur = discord.ui.select(

                    min_values = 1, 
                    max_values = 1,options=[
                                discord.SelectOption(
                                    label="Oui",
                                    description="Active les réponses auto",
                                    value="yesauto",
                                    emoji="✔️",
                                ),
                                discord.SelectOption(
                                    label="Non",
                                    description="Désactive les réponses auto (par défaut)",
                                    value="noauto",
                                    emoji="❌"
                                )],
                                
                                placeholder="Veux-tu activer les réponses auto? (quoifeur etc)")
"""    



class DateView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.cooldown = commands.CooldownMapping.from_cooldown(3,60, commands.BucketType.member)


    @discord.ui.select(
        cls=discord.ui.UserSelect,
        max_values=1,
        custom_id="persistent_view:userSelect",
        placeholder='Sélectionne / recherche un utilisateur',
    )


    async def user_select(self, interaction: discord.Interaction, cibleListe: discord.ui.UserSelect) -> None:
        bucket = self.cooldown.get_bucket(interaction.message)
        retry = bucket.update_rate_limit()

        if retry:
            await interaction.response.send_message(f"Tu es en **cooldown**, rééssaye dans `{round(retry,1)} secondes`", ephemeral=True)
            return

        else:

            cible = cibleListe.values[0]

            select = Select(options=[
            discord.SelectOption(label="Accepter", emoji="✔️", description="Accepte le date (si t en couple tu romps)"),
            discord.SelectOption(label="Refuser", emoji= "❌", description="Refuse le date")
            ], placeholder="Attention, tu ne peux faire ça qu'une fois tous les 7j") 
            
            guild = interaction.guild

            serverDict = dbserver.server.find_one({"serverID":guild.id})
            salonNotifs = guild.get_channel(serverDict["salonnotifs"])
            categorieDate = guild.get_channel(serverDict["categoriedate"])

            async def select_callback(interaction: discord.Interaction):

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

                                            await salonNotifs.send(content=cible.mention, embed = propositionEmbed,view=selectView)
                                            await interaction.response.send_message(f"Le date a bien été envoyé! <#{salonNotifs.id}>", ephemeral=True)
                                        
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




class NoProfileView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=180)
        self.cooldown = commands.CooldownMapping.from_cooldown(3,60, commands.BucketType.member)

    @discord.ui.button(label="S'inscrire", style= discord.ButtonStyle.green,emoji= "📁")
    async def boutoninscription(self, interaction: discord.Interaction, button: discord.ui.Button):

        bucket = self.cooldown.get_bucket(interaction.message)
        retry = bucket.update_rate_limit()

        if retry:
            await interaction.response.send_message(f"Tu es en **cooldown**, rééssaye dans `{round(retry,1)} secondes`", ephemeral=True)
        else:
            
            await interaction.response.send_modal(InscriptionModal(timeout=180) )




class InscriptionView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.cooldown = commands.CooldownMapping.from_cooldown(3,60, commands.BucketType.member)

    @discord.ui.button(label="S'inscrire", style= discord.ButtonStyle.green, custom_id= "persistent_view:green",emoji= "📁")
    async def boutoninscription(self, interaction: discord.Interaction, button: discord.ui.Button):

        bucket = self.cooldown.get_bucket(interaction.message)
        retry = bucket.update_rate_limit()

        if retry:
            await interaction.response.send_message(f"Tu es en **cooldown**, rééssaye dans `{round(retry,1)} secondes`", ephemeral=True)
        else:
            await interaction.response.send_modal(InscriptionModal() )
        
    
    @discord.ui.button(label="Effacer mon profil", style= discord.ButtonStyle.gray, custom_id= "persistent_view:red",emoji= "⚠️")
    async def boutonsupp(self, interaction: discord.Interaction, button: discord.ui.Button):
        utilisateur = interaction.user

        bucket = self.cooldown.get_bucket(interaction.message)
        retry = bucket.update_rate_limit()

        if retry:
            await interaction.response.send_message(f"Tu es en **cooldown**, rééssaye dans `{round(retry,1)} secondes`", ephemeral=True)

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
            else:
                await interaction.response.send_message(f'Tu n\'as pas de profil!', ephemeral=True)



#FORMULAIRE


class AccueilView(View):

    def __init__(self):
        super().__init__(timeout=None)
        self.cooldown = commands.CooldownMapping.from_cooldown(6,60, commands.BucketType.member)
    
    @discord.ui.select( 
        placeholder = "Que veux-tu faire?",
        min_values = 1, 
        max_values = 1,
        custom_id= "persistent_view:select",
        options = [ 
            discord.SelectOption(
                label="Je veux visiter!",
                description="Fais moi visiter!",
                value="visite",
                emoji="🗺️",
                default=True
            ),
            discord.SelectOption(
                label="Je veux créer mon profil!",
                description="Te permet d'accéder aux fonctionnalités du serveur!",
                value="profil",
                emoji="📁"
            ),
            discord.SelectOption(
                label="Je veux discuter!",
                description="C'est où, le chat?",
                value="chat",
                emoji="📣"
            ),
           discord.SelectOption(
                label="Poster mon selfie",
                description="A moi les minettes!",
                value="selfie",
                emoji="😎"
           )
        ]
    )

    async def select(self, interaction: discord.Interaction, select: discord.ui.Select) -> None:

        bucket = self.cooldown.get_bucket(interaction.message)
        retry = bucket.update_rate_limit()

        guild = interaction.guild

        if retry:
            await interaction.response.send_message(f"Tu es en **cooldown**, rééssaye dans `{round(retry,1)} secondes`", ephemeral=True)
   
        else:
            if select.values[0] == "profil":
                await interaction.response.send_modal(InscriptionModal())

            serverDB = dbserver.server.find_one({"serverID":guild.id})

            salonGeneral = serverDB["salonchat"] 
            salonSelfie = serverDB["salonselfie"]
            salonDate = serverDB["salondate"]

            titre= ""
            description = ""

            heure = dt.datetime.utcnow()+dt.timedelta(hours=1)

            if select.values[0] == "visite":
                titre = "Par ici la visite!"
                description = f"<#{salonGeneral}>: Par ici, tu pourras discuter et te faire de nouveaux amis!\n<#{salonSelfie}>:\
                Ici, tu vas voir la tête de tout le monde\n<#{salonDate}>: Là, tu pourras voir qui date qui"


            if select.values[0] == "chat":
                titre = "Tu veux discuter? C'est par là!"
                description = f"Le chat général: <#{salonGeneral}>, pour discuter et te faire de nouvelles rencontres!"

        
            if select.values[0] == "selfie":
                titre = "Besoin de flex?"
                description = f"Le salon selfie: <#{salonSelfie}>, pour potentiellement rencontrer ton/ta nouveau(elle) partenaire!"


            embedChat = discord.Embed(title=titre, description=description)
            embedChat.set_footer(text=guild.name,icon_url=guild.icon)
            #embedChat.set_image(url="")
            embedChat.timestamp= heure

            if select.values[0] != "profil":
                await interaction.response.send_message(embed=embedChat, ephemeral=True)
        
