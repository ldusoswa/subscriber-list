import csv
import patreon
youtubeSubs = 'C:\\Users\\dusosl\\Downloads\\Your members 30 Dec 2022, 16_00 Laurence Dusoswa.csv'
twitchSubs = 'C:\\Users\\dusosl\\Downloads\\subscriber-list (32).csv'
patroenSubs = 'C:\\Users\\dusosl\\Downloads\\Members_3825076.csv'

pitPass = []
pitCrew = []
crewChief = []
teamBoss = []

# TWITCH
# Open the CSV file and text file
print("\n#### TWITCH SUBS ####")
with open(twitchSubs, 'r') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row: row[4], reverse=True)

    for row in sortedlist:
        value = row[0]
        if value == "coooyahh":
            value = "FeckCancer"
        print(value)

# Patreon
# Open the CSV file and text file
print("\n#### PATREON & YOUTUBE SUBS ####")
with open(patroenSubs, 'r') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row:float(row[6]), reverse=True)
    # TODO Dan Persons should be Dogoncouch

    for row in sortedlist:
            if row[9] == "Pit Pass":
                pitPass.append(row[0])
            elif row[9] == "Pit Crew":
                pitCrew.append(row[0])
            elif row[9] == "Crew Chief":
                crewChief.append(row[0])
            elif row[9] == "Team Boss":
                teamBoss.append(row[0])

with open(youtubeSubs, 'r') as csv_file:
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
    print("\n#### Patreon & YouTube - Team Boss ####")
    for member in teamBoss:
        print(member)
        
    print("\n#### Patreon & YouTube - Crew Chief ####")
    for member in crewChief:
        print(member)
        
    print("\n#### Patreon & YouTube - Pit Crew ####")
    for member in pitCrew:
        print(member)
        
    print("\n#### Patreon & YouTube - Pit Pass ####")
    for member in pitPass:
        print(member)

