import csv
import os
import glob
from datetime import datetime, timedelta

# --- Constants ---
SUB_LISTS_DIR = 'C:\\Users\\dusosl\\Downloads\\'

# --- Globals ---
pitCrewCombined, crewChiefCombined, teamBossCombined = [], [], []
twitchCombined, pitCrewYouTube, pitCrewYouTubeGifted = [], [], []
crewChiefYouTube, teamBossYouTube = [], []
pitCrewPatreon, crewChiefPatreon, teamBossPatreon = [], [], []
pitCrewTwitchTier1, pitCrewTwitchTier1Gifted = [], []
newGiftedCombined, twitchPrimeExpiryBlurb = [], []
totalMemberCount = 0
totalGross, totalPlatformCosts, totalNet = 0.0, 0.0, 0.0


# --- Helpers ---
def find_recent_file(dir_path, prefix):
    file_list = glob.glob(f"{dir_path}/{prefix}*")
    file_list.sort(key=os.path.getmtime)
    return file_list[-1]


def perform_text_replacements(original):
    mapping = {
        'ï¼‡': '\'', 'Ã¼': 'ü', 'Dan Persons': 'Dogoncouch',
        'coooyahh': 'FeckCancer', 'kuyar21': 'FeckCancer',
        'adam_coolmunky': 'acreekracing_photography',
        'Phelan Pritchard Gaming': 'Phelan Pritchard',
        'astrophotography': 'Geezer3d.com',
        'damien mcmullen': 'Damo McMullen',
        ' ðŸ‡µðŸ‡¸': '', 'Å‚': 'l', 'Ã§': 'ç', 'â€™': '\'',
        'Ã«': 'ë', '＇': '\'', '’': '\'', 'é': 'é',
        'Ã©': 'é', '“': '"', '”': '"'
    }
    for key, value in mapping.items():
        original = original.replace(key, value)
    return original


def format_for_photoshop_text(members, padding):
    if not members:
        return 'None at this time'
    return ' '.join(member.ljust(padding) for member in members)


def calculate_and_output_totals(platform, tier_name, members, price_per_month):
    global totalGross, totalPlatformCosts, totalNet

    monthly_gross = len(members) * price_per_month

    if platform == 'YouTube':
        fees = monthly_gross * 0.30
    elif platform == 'Twitch':
        fees = monthly_gross * 0.50
    elif platform == 'Patreon':
        fees = (monthly_gross * 0.05 + len(members) * 0.10) if price_per_month < 3 else (monthly_gross * 0.029 + len(members) * 0.30)
    else:
        fees = 0

    monthly_net = monthly_gross - fees
    totalGross += monthly_gross
    totalPlatformCosts += fees
    totalNet += monthly_net

    if members:
        print(f'{platform} - {tier_name}\t{len(members)}\t€{price_per_month}\t€{monthly_gross:.2f}\t\t€{fees:.2f}\t\t€{monthly_net:.2f}')


# --- Load Files ---
youtubeSubsFile = find_recent_file(SUB_LISTS_DIR, 'Your members ')
twitchSubsFile = find_recent_file(SUB_LISTS_DIR, 'subscriber-list')
patreonSubsFile = find_recent_file(SUB_LISTS_DIR, 'Members_')

# --- Twitch ---
with open(twitchSubsFile, 'r') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row: float(row[3]), reverse=True)

    if sortedlist[0][0] == 'ldusoswa':
        sortedlist.pop(0)

    for row in sortedlist:
        username = perform_text_replacements(row[0])
        sub_type = row[5]

        if sub_type == 'gift':
            pitCrewTwitchTier1Gifted.append(username)
        else:
            pitCrewTwitchTier1.append(username)

        if sub_type in ['prime', 'gift']:
            sub_date = datetime.strptime(row[1], "%Y-%m-%dT%H:%M:%SZ")
            expiry_date = sub_date + timedelta(days=31)
            current_date = datetime.utcnow()
            days_left = 31 + (sub_date - current_date).days
            expiry_str = expiry_date.strftime("%B %d, %Y at %I:%M %p")
            blurb = f'{username.ljust(20)}\t{sub_type}\t\t{days_left}\t\t{expiry_str}'
            twitchPrimeExpiryBlurb.append(blurb)

# --- Patreon ---
with open(patreonSubsFile, 'r') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row: float(row[8]), reverse=True)

    for row in sortedlist:
        name = perform_text_replacements(row[0])
        tier = row[10]
        if tier == "Crew Chief":
            crewChiefPatreon.append(name)
        elif tier == "Team Boss":
            teamBossPatreon.append(name)
        else:
            pitCrewPatreon.append(name)

# --- YouTube ---
with open(youtubeSubsFile, 'r', encoding='utf-8') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row: float(row[4]), reverse=True)

    for row in sortedlist:
        name = perform_text_replacements(row[0])
        tier = row[2]
        amount = float(row[4])

        if tier == "Pit Crew":
            (pitCrewYouTube if amount > 3 else pitCrewYouTubeGifted).append(name)
        elif tier == "Crew Chief":
            crewChiefYouTube.append(name)
        elif tier == "Team Boss":
            teamBossYouTube.append(name)

# --- Combine Lists ---
teamBossCombined = teamBossPatreon + teamBossYouTube
crewChiefCombined = crewChiefPatreon + crewChiefYouTube
pitCrewCombined = pitCrewPatreon + pitCrewYouTube
twitchCombined = pitCrewTwitchTier1
newGiftedCombined = pitCrewYouTubeGifted + pitCrewTwitchTier1Gifted
totalMemberCount = len(teamBossCombined + crewChiefCombined + pitCrewCombined + twitchCombined + newGiftedCombined)

# --- Output Lists ---
print(f'\nTeam Boss\t{", ".join(teamBossCombined)}')
print(f'Crew Chief\t{", ".join(crewChiefCombined)}')
print(f'Pit Crew\t{", ".join(pitCrewCombined)}')
print(f'TWITCH\t\t{", ".join(twitchCombined)}')

# --- Write CSV for Photoshop ---
data = [
    ['teamBoss', 'crewChief', 'pitCrew', 'twitchSubs', 'newGifted'],
    [
        format_for_photoshop_text(teamBossCombined, 45),
        format_for_photoshop_text(crewChiefCombined, 30),
        format_for_photoshop_text(pitCrewCombined, 30),
        format_for_photoshop_text(pitCrewTwitchTier1, 30),
        format_for_photoshop_text(newGiftedCombined, 24)
    ]
]

psd_file = 'levels.csv'
with open(psd_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerows(data)

print(f'\nCSV file created successfully for Photoshop import: {psd_file}')

# --- Output Earnings ---
print(f'\n############################# MONTHLY EARNINGS REPORT #####################################')
print(f'level\t\t\tmembers\trate\tgross income\tplatform costs\ttotal (before tax)')
print(f'_____________________\t______\t______\t______________\t______________\t__________________')

calculate_and_output_totals('YouTube', 'Team Boss', teamBossYouTube, 19.99)
calculate_and_output_totals('YouTube', 'Crew Chief', crewChiefYouTube, 9.99)
calculate_and_output_totals('YouTube', 'Pit Crew', pitCrewYouTube, 4.99)
calculate_and_output_totals('YouTube', 'Gifted', pitCrewYouTubeGifted, 4.99)
calculate_and_output_totals('Twitch', 'Tier 1 member', pitCrewTwitchTier1, 4.99)
calculate_and_output_totals('Twitch', 'Gifted sub', pitCrewTwitchTier1Gifted, 4.99)
calculate_and_output_totals('Patreon', 'Team Boss', teamBossPatreon, 19.99)
calculate_and_output_totals('Patreon', 'Crew Chief', crewChiefPatreon, 9.99)
calculate_and_output_totals('Patreon', 'Pit Crew', pitCrewPatreon, 4.99)

print('===========================================================================================')
print(f'TOTAL\t\t\t{totalMemberCount}\t\t€{totalGross:.2f}\t\t€{totalPlatformCosts:.2f}\t\t€{totalNet:.2f}')
print(f'###########################################################################################')

# Uncomment below to show Twitch Prime expiry data
# print(f'\n\n############################# TWITCH PRIME EXPIRING SOON #####################################')
# print(f'member\t\t\tsub type\tdays left\t\texpiry date')
# print(f'_____________________\t__________\t__________\t___________________________')
# for blurb in twitchPrimeExpiryBlurb:
#     print(blurb)
# print(f'\nTwitch prime subs do not auto-renew. If you\'d like to renew your prime sub, set a reminder for the expiry date beside your name.')
# print('##############################################################################################')

print(f'newGifted: {newGiftedCombined}')
