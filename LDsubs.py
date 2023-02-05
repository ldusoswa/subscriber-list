import sys
sys.path.append("LDSubScraper")
from LDSubScraper.LDSubScraper import getListOfMembersPerTierAsString


# print all the members
listOfMembers = getListOfMembersPerTierAsString()
print(listOfMembers)

