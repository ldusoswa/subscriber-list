import csv
import os
import glob

from datetime import datetime, timedelta

pitCrewCombined = []
crewChiefCombined = []
teamBossCombined = []
pitCrewYouTube = []
pitCrewYouTubeGifted = []
crewChiefYouTube = []
teamBossYouTube = []
pitCrewPatreon = []
crewChiefPatreon = []
teamBossPatreon = []
twitchSubs = []
twitchPrimeExpiryBlurb = []
totalMemberCount = 0

totalGross = float(0)
totalPlatformCosts = float(0)
totalNet = float(0)

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
def performTextReplacements(original):
    # Create a mapping of characters to replace
    mapping = {
        'ï¼‡': '\'',
        'Ã¼': 'ü',
        'Dan Persons': 'Dogoncouch',
        'coooyahh': 'FeckCancer',
        'kuyar21': 'FeckCancer',
        'adam_coolmunky': 'acreekracing_photography',
        'Phelan Pritchard Gaming': 'Phelan Pritchard',
        'astrophotography': 'Geezer3d.com',
        'damien mcmullen': 'Damo McMullen',
        ' ðŸ‡µðŸ‡¸': '',
        'Å‚': 'l',
        'Ã§': 'ç',
        'â€™': '\'',
        'Ã«': 'ë',
        '＇': '\'',
        '’': '\'',
        'é': 'é',
        'Ã©': 'é',
        'Ã§': 'ç',
        '“': '"',
        '”': '"',
    }

#     print(f'Original: {original}')

    for key, value in mapping.items():
        original = original.replace(key, value)

#     print(f'Replaced: {original}')
    return original

# TWITCH
with open(twitchSubsFile, 'r') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row:float(row[3]), reverse=True)
    if sortedlist[0][0] == 'ldusoswa':
        sortedlist.pop(0) # remove ldusoswa

    for row in sortedlist:
        twitchSubs.append(performTextReplacements(row[0]))

        if row[5] == 'prime' or row[5] == 'gift':
            date_format = "%Y-%m-%dT%H:%M:%SZ"
            currentDate = datetime.utcnow().strftime(date_format)
            subDate = row[1]

            daysLeft = 31 + (datetime.strptime(subDate, '%Y-%m-%dT%H:%M:%SZ') - datetime.strptime(currentDate, '%Y-%m-%dT%H:%M:%SZ')).days
            parsed_subscription_date = datetime.strptime(subDate, date_format)
            expiry_date = parsed_subscription_date + timedelta(days=31)
            formatted_expiry_date = expiry_date.strftime("%B %d, %Y at %I:%M %p")

            blurb = f'{performTextReplacements(row[0]).ljust(20)}\t{row[5]}\t\t{daysLeft}\t\t{formatted_expiry_date}'
            twitchPrimeExpiryBlurb.append(blurb)

# Patreon
with open(patroenSubsFile, 'r') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row:float(row[8]), reverse=True)
    # print(sortedlist)

    for row in sortedlist:
            # print(row[10] + ' - ' + row[0])
            if row[10] == "Crew Chief":
                crewChiefCombined.append(performTextReplacements(row[0]))
                crewChiefPatreon.append(performTextReplacements(row[0]))
            elif row[10] == "Team Boss":
                teamBossCombined.append(performTextReplacements(row[0]))
                teamBossPatreon.append(performTextReplacements(row[0]))
            elif row[10] == "Pit Crew" or row[10] == "":
                pitCrewCombined.append(performTextReplacements(row[0]))
                pitCrewPatreon.append(performTextReplacements(row[0]))

# YouTube
with open(youtubeSubsFile, 'r', encoding='utf-8') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row:float(row[4]), reverse=True)

    for row in sortedlist:
        if row[2] == "Pit Crew":
            if float(row[4]) > 3:
                pitCrewCombined.append(performTextReplacements(row[0]))
                pitCrewYouTube.append(performTextReplacements(row[0]))
            else:
                pitCrewYouTubeGifted.append(performTextReplacements(row[0]))
        elif row[2] == "Crew Chief":
            crewChiefCombined.append(performTextReplacements(row[0]))
            crewChiefYouTube.append(performTextReplacements(row[0]))
        elif row[2] == "Team Boss":
            teamBossCombined.append(performTextReplacements(row[0]))
            teamBossYouTube.append(performTextReplacements(row[0]))

# output the complete list of names
# print(f'\n#### All Members ####')
# for member in teamBossCombined:
#     print(member)
#
# for member in crewChiefCombined:
#     print(member)
# #
print('\n')

for member in pitCrewCombined:
    print(member)
#
# for member in twitchSubs:
#     print(member)

totalMemberCount = len(pitCrewCombined) + len(pitCrewYouTubeGifted) + len(crewChiefCombined) + len(teamBossCombined) + len(twitchSubs)

# TODO print out youtube description blurb
print(f'\nTeam Boss (€19.99/mo)\t\t{", ".join(teamBossCombined)}')
print(f'Crew Chief (€9.99/mo)\t\t{", ".join(crewChiefCombined)}')
print(f'Pit Crew (€4.99/mo)\t\t{", ".join(pitCrewCombined)}')
print(f'TWITCH (€4.99/mo)\t\t{", ".join(twitchSubs)}')

# Create the csv for photoshop to import
def formatForPhotoshopText(membersArray, padding):
    photoshopText = ''
    for index, member in enumerate(membersArray):
            photoshopText = f'{photoshopText} {member.ljust(padding)}'

    return photoshopText

data = [
    ['teamBoss', 'crewChief', 'pitCrew', 'pitCrewYouTubeGifted', 'twitchSubs'],
    [
        formatForPhotoshopText(teamBossCombined, 45),
        formatForPhotoshopText(crewChiefCombined, 30),
        formatForPhotoshopText(pitCrewCombined, 30),
        formatForPhotoshopText(pitCrewYouTubeGifted, 24),
        formatForPhotoshopText(twitchSubs, 30)
    ]
]
psdName = 'levels.csv'

with open(psdName, 'w', newline='', encoding='utf-8-sig') as csv_file:
    writer = csv.writer(csv_file)
    for row in data:
        writer.writerow(row)

    print(f'\nCSV file created successfully for Photoshop import: {psdName}')

def calculateAndOutputTotals(platform, tierName, members, pricePerMonth):
    # Calculate totals for this tier
    monthlyGross = len(members)*pricePerMonth
    # calculate the platform costs
    if platform == 'YouTube':
        monthlyPlatformFees = monthlyGross*30/100
    elif platform == 'Twitch':
        monthlyPlatformFees = monthlyGross*50/100
    elif platform == 'Patreon':
        if pricePerMonth < 3:
            monthlyPlatformFees = monthlyGross*5/100 + len(members)*0.10
        else:
            monthlyPlatformFees = monthlyGross*2.9/100 + len(members)*0.30
    else:
        monthlyPlatformFees = 0
    monthlyNet = monthlyGross - monthlyPlatformFees

    # Update running totals
    global totalGross
    global totalPlatformCosts
    global totalNet
    totalGross += monthlyGross
    totalPlatformCosts += monthlyPlatformFees
    totalNet += monthlyNet

    # spit out the data
    if len(members) > 0:
        print(f'{platform} - {tierName}\t{len(members)}\t€{pricePerMonth}\t€{"{:.2f}".format(monthlyGross)}\t\t€{"{:.2f}".format(monthlyPlatformFees)}\t\t€{"{:.2f}".format(monthlyNet)}')

# Do earnings projections
print(f'\n############################# MONTHLY EARNINGS REPORT #####################################')
print(f'level\t\t\tmembers\trate\tgross income\tplatform costs\ttotal (before tax)')
print(f'_____________________\t______\t______\t______________\t______________\t__________________')
calculateAndOutputTotals('YouTube', 'Team Boss', teamBossYouTube, 19.99)
calculateAndOutputTotals('YouTube', 'Crew Chief', crewChiefYouTube, 9.99)
calculateAndOutputTotals('YouTube', 'Pit Crew', pitCrewYouTube, 4.99)
calculateAndOutputTotals('YouTube', 'Gifted/New', pitCrewYouTubeGifted, 4.99)
calculateAndOutputTotals('Twitch', 'Subscriptions', twitchSubs, 4.99)
calculateAndOutputTotals('Patreon', 'Team Boss', teamBossPatreon, 19.99)
calculateAndOutputTotals('Patreon', 'Crew Chief', crewChiefPatreon, 9.99)
calculateAndOutputTotals('Patreon', 'Pit Crew', pitCrewPatreon, 4.99)

print('===========================================================================================')
print(f'TOTAL\t\t\t{totalMemberCount}\t\t€{"{:.2f}".format(totalGross)}\t\t€{"{:.2f}".format(totalPlatformCosts)}\t\t€{"{:.2f}".format(totalNet)}')
print(f'###########################################################################################')

# print(f'\n\n############################# TWITCH PRIME EXPIRING SOON #####################################')
# print(f'member\t\t\tsub type\tdays left\t\texpiry date')
# print(f'_____________________\t__________\t__________\t___________________________')
# for blurb in twitchPrimeExpiryBlurb:
#     print(blurb)
# print(f'\nTwitch prime subs do not auto-renew. If you\'d like to renew your prime sub, the easiest way \nto remember to renew it is by setting a monthly reminder for the expiry date beside your name')
# print('##############################################################################################')
