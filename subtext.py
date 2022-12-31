import csv
import patreon
import os
import glob

pitPass = []
pitCrew = []
crewChief = []
teamBoss = []
twitchSubs = []

subListsDir = 'C:\\Users\\dusosl\\Downloads\\'

def find_recent_file(dir, prefix):
  # Get the list of all files in the directory
  file_list = glob.glob(dir + "/" + prefix + "*")

  # Sort the list of files by modification time
  file_list.sort(key=os.path.getmtime)

  # Return the most recent file
  return file_list[-1]

youtubeSubsFile = find_recent_file(subListsDir, 'Your members ')
twitchSubsFile = find_recent_file(subListsDir, 'subscriber-list')
patroenSubsFile = find_recent_file(subListsDir, 'Members_')

# quick and dirty replace of poor imports or name change requests
def prettyPrint(original):
    new = original
    new = new.replace('ï¼‡', '\'')
    new = new.replace('Ã¼', 'ü')
    new = new.replace('Dan Persons', 'Dogoncouch')
    new = new.replace('coooyahh', 'FeckCancer')
    print(new)

# TWITCH
with open(twitchSubsFile, 'r') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    twitchSubs = sorted(reader, key=lambda row: row[4], reverse=True)
    if twitchSubs[0][0] == 'ldusoswa':
        twitchSubs.pop(0) # remove ldusoswa

# Patreon
with open(patroenSubsFile, 'r') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row:float(row[6]), reverse=True)

    for row in sortedlist:
            if row[9] == "Pit Pass":
                pitPass.append(row[0])
            elif row[9] == "Pit Crew":
                pitCrew.append(row[0])
            elif row[9] == "Crew Chief":
                crewChief.append(row[0])
            elif row[9] == "Team Boss":
                teamBoss.append(row[0])

# YouTube
with open(youtubeSubsFile, 'r') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row:float(row[4]), reverse=True)

    for row in sortedlist:
        if row[2] == "Pit Pass":
            pitPass.append(row[0])
        elif row[2] == "Pit Crew":
            pitCrew.append(row[0])
        elif row[2] == "Crew Chief":
            crewChief.append(row[0])
        elif row[2] == "Team Boss":
            teamBoss.append(row[0])
            

# output the results
print(f'\n#### Patreon & YouTube - Team Boss ({len(teamBoss)}) ####')
for member in teamBoss:
    prettyPrint(member)

print(f'\n#### Patreon & YouTube - Crew Chief ({len(crewChief)}) ####')
for member in crewChief:
    prettyPrint(member)

print(f'\n#### Patreon & YouTube - Pit Crew ({len(pitCrew)}) ####')
for member in pitCrew:
    prettyPrint(member)

print(f'\n#### TWITCH SUBS - Pit Crew ({len(twitchSubs)}) ####')
for row in twitchSubs:
    prettyPrint(row[0])

print(f'\n#### Patreon & YouTube - Pit Pass ({len(pitPass)}) ####')
for member in pitPass:
    prettyPrint(member)

print(f'\nTotal paid contributors: {len(pitPass) + len(pitCrew) + len(crewChief) + len(teamBoss) + len(twitchSubs) }')

# TODO print out youtube description blurb
