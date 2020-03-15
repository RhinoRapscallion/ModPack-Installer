import json, os, pathlib, shutil
from urllib.request import Request, urlopen, urlretrieve
import tkinter as tk
from tkinter import filedialog

workingdir = os.path.dirname(os.path.realpath(__file__))
print(workingdir)
print(
    "Welcome to RhinoGaming1187's Modpack Installer\n" +
    "----------------------------------------------" 
)

minecraft = input("Full Path of Minecraft Folder (Defaults to {}\\AppData\\Roaming\\.minecraft): ".format(pathlib.Path.home()))
ram = input('Ram in GB to Allocate (Defaults to 2): ')
try:
    ram = int(ram)
except:
    print("Defaulting Ram to: 2GB")
    ram = 2

if minecraft == None or minecraft == '':
    minecraft = '{}\\AppData\\Roaming\\.minecraft'.format(pathlib.Path.home())
    print('Defaulting Path to: {}\\AppData\\Roaming\\.minecraft'.format(pathlib.Path.home()))

if not os.path.exists(os.path.join(workingdir, "manifest.json")):
    print("Manifest Doesn't Exist")
    raise(FileNotFoundError)

manifest = open(os.path.join(workingdir,"manifest.json"))
data = json.load(manifest)
manifest.close()

if not os.path.exists(os.path.join(workingdir, "overrides")):
    print("Overrides Don't Exist")
    raise(FileNotFoundError)
os.chdir(os.path.join(workingdir, "overrides"))
workingdir = os.getcwd()

if not os.path.exists(os.path.join(workingdir, "mods")):
    os.mkdir(os.path.join(workingdir, 'mods'))
#install correct version of forge
version = data['minecraft']['version']

print(
    '----------------------------------------------\n'+
    'Installing Forge for Minecraft {}...          \n'.format(version) +
    '----------------------------------------------\n'
)

forgeinstalled = False

print("version: {}".format(version))
forge = data['minecraft']['modLoaders'][0]['id'].replace("forge-", '')
print("forge-{}".format(forge))
constructor = version + '-' + forge
print("URL Constructor: {}".format(constructor))

for (root, dirs, files) in os.walk(minecraft, topdown= True):
    for i in dirs:
        if i == '{}-forge{}'.format(version, constructor):
            forgeinstalled = True
            break

if forgeinstalled:
    print("Forge for {} Already Installed...".format(version))
else:
    print(
        '----------------------------------------------\n' +
        'Starting Forge Installer Log\n' +
        '----------------------------------------------' 
    )
    downloadUrl = 'https://files.minecraftforge.net/maven/net/minecraftforge/forge/{constructor}/forge-{constructor}-installer.jar'.format(constructor= constructor)
    urlretrieve(downloadUrl, os.path.join(workingdir, 'forge-installer.jar'))
    os.system('java -jar "' + os.path.join(workingdir, 'forge-installer.jar' + '"'))

#get mods
print(
    '----------------------------------------------\n' +
    'Downloading Mods from Manifest...\n' +
    '----------------------------------------------'
)
totalmods = len(data['files'])
modnumber = 0
for i in data["files"]:
    modnumber += 1
    projectID = str(i['projectID'])
    fileID = str(i['fileID'])
    request = Request('https://addons-ecs.forgesvc.net/api/v2/addon/{addonID}/file/{fileID}/download-url'.format(addonID = projectID, fileID = fileID))
    
    response = urlopen(request).read()
    print("Downloading mod [{} of {}] from: {}".format(modnumber, totalmods, response.decode('utf-8')))
    downloadUrl = response.decode("utf-8").replace(' ', '%20')
    urlretrieve(downloadUrl, os.path.join(workingdir, "mods\\project{}-file{}.jar".format(projectID, fileID)))

#make and move minecraft folder
print(
    '----------------------------------------------\n'
    'Finalizing...\n' +
    '----------------------------------------------'
)
path = pathlib.Path(os.getcwd())
os.chdir(path.parent)

if not os.path.exists(os.path.join(minecraft, "ModPacks")):
    os.mkdir(os.path.join(minecraft, 'ModPacks'))

name = data['name']

shutil.move(os.path.join(os.getcwd(), 'overrides'), os.path.join(minecraft, 'ModPacks', name))

jsonprofile ={
    "gameDir" : os.path.join(minecraft, 'ModPacks', name),
    "javaArgs" : "-Xmx{}G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M".format(ram),
    "lastUsed" : "2020-03-14T19:46:35+0000",
    "lastVersionId" : "{}-forge{}".format(version, constructor),
    "name" : name,
    "type" : "ModPack"
}

file = open(os.path.join(minecraft, 'launcher_profiles.json'))
profilesjson = json.load(file)
file.close()

profilesjson['profiles'][name.replace(' ', '-')] = jsonprofile

with open(os.path.join(minecraft, 'launcher_profiles.json'), 'w') as file:
    json.dump(profilesjson, file, indent = 4)

print(
    '----------------------------------------------\n' +
    'Done!\n' +
    '----------------------------------------------\n'
    )