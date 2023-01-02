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
def prettify(original):
    new = original
    new = new.replace('ï¼‡', '\'')
    new = new.replace('Ã¼', 'ü')
    new = new.replace('Dan Persons', 'Dogoncouch')
    new = new.replace('coooyahh', 'FeckCancer')
    return new

# TWITCH
with open(twitchSubsFile, 'r') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row: row[4], reverse=True)
    if sortedlist[0][0] == 'ldusoswa':
        sortedlist.pop(0) # remove ldusoswa

    for row in sortedlist:
        twitchSubs.append(prettify(row[0]))

# Patreon
with open(patroenSubsFile, 'r') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row:float(row[6]), reverse=True)

    for row in sortedlist:
            if row[9] == "Pit Pass":
                pitPass.append(prettify(row[0]))
            elif row[9] == "Pit Crew":
                pitCrew.append(prettify(row[0]))
            elif row[9] == "Crew Chief":
                crewChief.append(prettify(row[0]))
            elif row[9] == "Team Boss":
                teamBoss.append(prettify(row[0]))

# YouTube
with open(youtubeSubsFile, 'r') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row:float(row[4]), reverse=True)

    for row in sortedlist:
        if row[2] == "Pit Pass":
            pitPass.append(prettify(row[0]))
        elif row[2] == "Pit Crew":
            pitCrew.append(prettify(row[0]))
        elif row[2] == "Crew Chief":
            crewChief.append(prettify(row[0]))
        elif row[2] == "Team Boss":
            teamBoss.append(prettify(row[0]))
            

# output the results
print(f'\n#### Patreon & YouTube - Team Boss ({len(teamBoss)}) ####')
for member in teamBoss:
    print(member)

print(f'\n#### Patreon & YouTube - Crew Chief ({len(crewChief)}) ####')
for member in crewChief:
    print(member)

print(f'\n#### Patreon & YouTube - Pit Crew ({len(pitCrew)}) ####')
for member in pitCrew:
    print(member)

print(f'\n#### TWITCH SUBS - Pit Crew ({len(twitchSubs)}) ####')
for member in twitchSubs:
    print(member)

print(f'\n#### Patreon & YouTube - Pit Pass ({len(pitPass)}) ####')
for member in pitPass:
    print(member)

print(f'\nTotal paid contributors: {len(pitPass) + len(pitCrew) + len(crewChief) + len(teamBoss) + len(twitchSubs) }')

# TODO print out youtube description blurb
print(f'Team Boss (€20/mo)      {", ".join(teamBoss)}')
print(f'Crew Chief (€10/mo)     {", ".join(crewChief)}')
print(f'Pit Crew (€5/mo)        {", ".join(pitCrew)}')
print(f'TWITCH Tier 1           {", ".join(twitchSubs)}')
print(f'Pit Pass (€3/mo)        {", ".join(pitPass)}')

