from config import DOWNLOADS_DIR, YOUTUBE_SUBS_FILE_PREFIX, TWITCH_SUBS_FILE_PREFIX, PATREON_SUBS_FILE_PREFIX, TWITCH, YOUTUBE, PATREON
from helperFunctions import find_recent_file, mergeTiersAcrossPlatforms
from subFileReader import get_twitch_tiers_and_subs, get_youtube_tiers_and_subs, get_patreon_tiers_and_subs

allMembers = {}

# Step 1 get the recent files. This will pull from your downloads folder as defined above
youTubeSubsFile = find_recent_file(DOWNLOADS_DIR, YOUTUBE_SUBS_FILE_PREFIX)
twitchSubsFile = find_recent_file(DOWNLOADS_DIR, TWITCH_SUBS_FILE_PREFIX)
patroenSubsFile = find_recent_file(DOWNLOADS_DIR, PATREON_SUBS_FILE_PREFIX)

# the order here will have an impact on the order they appear in the combined lists
if patroenSubsFile:
    get_patreon_tiers_and_subs(patroenSubsFile, allMembers)
if youTubeSubsFile:
    get_youtube_tiers_and_subs(youTubeSubsFile, allMembers)
if twitchSubsFile:
    get_twitch_tiers_and_subs(twitchSubsFile, allMembers)

combinedMembers = mergeTiersAcrossPlatforms(allMembers)

def test():
    return 'blah'

def getAllMembers():
    return combinedMembers

def getCombinedMembers():
    return combinedMembers

def getTiers():
    return combinedMembers.keys()

def getMembersAtTier(tier):
    return combinedMembers[tier]

def getTwitchMembers():
    return allMembers[TWITCH]

def getYouTubeMembers():
    return allMembers[YOUTUBE]

def getPatreonMembers():
    return allMembers[PATREON]

def getListOfMembers():
    listOfMembers = ''
    for tier, members in combinedMembers.items():
        listOfMembers += ('\n').join(members)

    return listOfMembers

def getListOfMembersPerTierAsString():
    listOfMembers = ''
    for tier, members in combinedMembers.items():
        listOfMembers += f'\n#####{tier}#####\n'
        for member in members:
            listOfMembers += f'{member}\n'

    return listOfMembers
