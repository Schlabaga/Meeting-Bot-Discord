import pymongo
from discord.ext import commands
import discord
import os
from dotenv import load_dotenv

load_dotenv()


MONGO_CLIENT_KEY = os.getenv('MONGO_CLIENT_KEY')
TOKEN = os.getenv('TOKEN')

bot = commands.Bot(command_prefix="!", intents= discord.Intents.all())


client = pymongo.MongoClient(MONGO_CLIENT_KEY)
dbuser = client.userconfig
dbbot = client.botconfig
dbserver = client.serverconfig

EmbedColor= 16711822 #POSSIBILITE DE CHANGER LA COULEUR DES EMBEDS (CODE HEXADECIMAL / https://gist.github.com/thomasbnt/b6f455e2c7d743b796917fa3c205f812)

GUILD = 993849107678515230 #METTRE ICI L'ID DU SERVEUR
categorieDate = 0 #METTRE ICI LA CATEGORIE OU APPARAITRONT LES DATES


#POSSIBILITE DE REMPLACER DES VILLES

villeListe = ["Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Montpellier", "Strasbourg", "Bordeaux", "Lille", \
              "Rennes", "Reims", "Toulon", "Saint-Etienne", "Le Havre", "Grenoble", "Dijon", "Angers", "Saint-Denis", "Villeurbanne",\
                  "Nimes", "Clermont-Ferrand", "Aix-en-Provence", "Le Mans", "Brest", "Tours", "Amiens", "Limoges", "Annecy", "Boulogne-Billancourt", \
                    "Perpignan", "Metz", "Besancon", "Orleans", "Saint-Denis", "Rouen", "Montreuil", "Argenteuil", "Mulhouse", "Caen", "Nancy", "Saint-Paul", \
                        "Roubaix", "Tourcoing", "Nanterre", "Vitry-sur-Seine", "Creteil", "Avignon", "Poitiers", "Aubervilliers"]

#POSSIBILITE D'AJOUTER DES REPONSES SOUS LA FORME {(tuple de provocateurs):[liste de réponses]}

funReponseDict = {("quoi","koi","koa", "quoi?"):['feur',"drilatère","driceps","shi","coubeh"], ("oui","ui"):["ghour","stiti","sky","fi","kend"], 
                ("non","nn"):["bril"],("ouais","oe","oue"):["stern","jden"],("hein","hn?","hein?"):["deux", "2","dien","stagram","doux","posteur"],
                ("comment","comment?"):["dent","taire","tateur"], ("ta mère","mère","mere"):["cedes"],("allo","allo?"):["pital"],("coucou","cc"):["niette"],
                ("ok","okay"):["sur glace"],("tg"):['v'],("re","reuh"):["nard","quin"],("yo"):['plait'], ("qui","qui?"):["rikou","ri","wi"],
                ("nan"):["cy"], ("mais"):["son","juin"],("ah","aaaah"):["b","vion","beille","vocat","poil","rabe"], ("rouge"):["gorge"],("dit"):["recteur","rigeable"]}

#POSSIBILITE D'AJOUTER DES GIFS QUI APPARAITRONT LORSQU'UNE IMAGE SERA LIKEE

likesGifs = ["https://media.tenor.com/jhsdIveYcGAAAAAC/big-snoopa-borzoi.gif","https://media.giphy.com/media/WpllTN0WCLq7vXhuTY/giphy.gif",
                  "https://i.pinimg.com/originals/35/a1/d7/35a1d707e4be7cf2b1d0f8dba00003cc.gif","https://media.tenor.com/Ao1ftp1W0WAAAAAd/discord-notification.gif",
                    "https://marketpedia.ca/wp-content/uploads/2021/10/gif-01-brent-rambo-b25.gif", "https://images.wondershare.com/filmora/article-images/what-is-gif.gif",
                      "https://i.gifer.com/Bkl6.gif", "https://media.tenor.com/4lKRNDUHBzcAAAAC/harry-potter.gif", "https://media.tenor.com/Y8jWfoPKmMoAAAAC/elon-musk-dance.gif"]

