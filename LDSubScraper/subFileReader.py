import csv
from helperFunctions import performTextReplacements
from config import TWITCH, YOUTUBE, PATREON, MY_TWITCH_NAME, TEXT_REPLACEMENT_MAP, TWITCH_TIER_REPLACEMENTS_MAP

def get_twitch_tiers_and_subs(twitchSubsFile, allMembers):
    allMembers[TWITCH] = {}
    with open(twitchSubsFile, 'r') as csv_file:
        next(csv_file)
        reader = csv.reader(csv_file)

        # order the list by how long they've been a member
        sortedlist = sorted(reader, key=lambda row: row[1], reverse=False)

        # remove myself from the list
        if sortedlist[0][0] == MY_TWITCH_NAME:
            sortedlist.pop(0)

        # determine unique tiers from the csv
        tiers = set([row[2] for row in sortedlist])
        # add each tier to the allMembers dictionary
        for tier in tiers:
            allMembers[TWITCH][performTextReplacements(tier, TWITCH_TIER_REPLACEMENTS_MAP)] = []

        # populate the subs dictionary
        for row in sortedlist:
            allMembers[TWITCH][performTextReplacements(row[2], TWITCH_TIER_REPLACEMENTS_MAP)].append(performTextReplacements(row[0], TEXT_REPLACEMENT_MAP))

def get_youtube_tiers_and_subs(youTubeSubsFile, allMembers):
    allMembers[YOUTUBE] = {}
    with open(youTubeSubsFile, 'r') as csv_file:
        next(csv_file)
        reader = csv.reader(csv_file)
        # order the list by how long they've been a member
        sortedlist = sorted(reader, key=lambda row:float(row[4]), reverse=True)

        # determine unique tiers from the csv
        tiers = set([row[2] for row in sortedlist])
        # add each tier to the allMembers dictionary
        for tier in tiers:
            allMembers[YOUTUBE][tier] = []

        # populate the members dictionary
        for row in sortedlist:
            allMembers[YOUTUBE][row[2]].append(performTextReplacements(row[0], TEXT_REPLACEMENT_MAP))


def get_patreon_tiers_and_subs(patreonSubsFile, allMembers):
    allMembers[PATREON] = {}
    with open(patreonSubsFile, 'r') as csv_file:
        next(csv_file)
        reader = csv.reader(csv_file)
        # order the list by how long they've been a member
        sortedlist = sorted(reader, key=lambda row:float(row[6]), reverse=True)

        # determine unique tiers from the csv
        tiers = set([row[9] for row in sortedlist])
        # add each tier to the allMembers dictionary
        for tier in tiers:
            allMembers[PATREON][tier] = []

        # populate the members dictionary
        for row in sortedlist:
            allMembers[PATREON][row[9]].append(performTextReplacements(row[0], TEXT_REPLACEMENT_MAP))

