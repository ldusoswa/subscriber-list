import csv
youtubeSubs = 'C:\\Users\\dusosl\\Downloads\\Your members 30 Dec 2022, 16_00 Laurence Dusoswa.csv'
twitchSubs = 'C:\\Users\\dusosl\\Downloads\\subscriber-list (32).csv'
patroenSubs = 'C:\\Users\\dusosl\\Downloads\\Members_3825076.csv'

# TWITCH
# Open the CSV file and text file
print("#### TWITCH SUBS ####")
excludedTwitchNames = ["Username", "ldusoswa"]
with open(twitchSubs, 'r') as csv_file:
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row: row[4], reverse=True)

    for row in sortedlist:
        value = row[0]
        if value == "coooyahh":
            value = "FeckCancer"
        if value not in excludedTwitchNames:
            print(value)
            
print("#### YOUTUBE SUBS ####")
excludedYouTubeNames = ["Member"]
with open(youtubeSubs, 'r') as csv_file:
    next(csv_file)
    # Create a CSV reader object
    reader = csv.reader(csv_file)
    pitPass = []
    pitCrew = []
    crewChief = []
    teamBoss = []

    # Iterate through each row in the CSV file
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
    print("#### YouTube - Team Boss ####")
    for member in teamBoss:
        print(member)
        
    print("#### YouTube - Crew Chief ####")
    for member in crewChief:
        print(member)
        
    print("#### YouTube - Pit Crew ####")
    for member in pitCrew:
        print(member)
        
    print("#### YouTube - Pit Pass ####")
    for member in pitPass:
        print(member)
        
        
# Patreon
# Open the CSV file and text file
print("#### Patreon SUBS ####")
with open(patroenSubs, 'r') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row:float(row[6]), reverse=True)
   
    for row in sortedlist:
        value = row[0]
        if value not in excludedTwitchNames:
            print(value)