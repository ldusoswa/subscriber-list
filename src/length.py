import csv
import os
import glob
from datetime import datetime

# --- Constants ---
SUB_LISTS_DIR = 'C:\\Users\\dusosl\\Downloads\\'

def find_recent_file(dir_path, prefix):
    file_list = glob.glob(f"{dir_path}/{prefix}*")
    file_list.sort(key=os.path.getmtime)
    return file_list[-1]

def perform_text_replacements(original):
    mapping = {
        'ï¼‡': '\'',
        'Ã¼': 'ü',
        'Dan Persons': 'Dogoncouch',
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
        '“': '"',
        '”': '"'
    }
    for key, value in mapping.items():
        original = original.replace(key, value)
    return original

def months_between_dates(start_date, end_date=None):
    if not start_date:
        return 0
    if end_date is None:
        end_date = datetime.utcnow()

    # Calculate full months difference between dates
    years_diff = end_date.year - start_date.year
    months_diff = end_date.month - start_date.month
    days_diff = end_date.day - start_date.day

    total_months = years_diff * 12 + months_diff
    if days_diff < 0:
        total_months -= 1
    return max(total_months, 0)

# --- Load Files ---
youtubeSubsFile = find_recent_file(SUB_LISTS_DIR, 'Your members ')
twitchSubsFile = find_recent_file(SUB_LISTS_DIR, 'subscriber-list')
patreonSubsFile = find_recent_file(SUB_LISTS_DIR, 'Members_')

all_members = []

# --- Twitch: use row[3] directly as months (whole number) ---
with open(twitchSubsFile, 'r') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row: float(row[3]), reverse=True)

    if sortedlist and sortedlist[0][0] == 'ldusoswa':
        sortedlist.pop(0)

    for row in sortedlist:
        username = perform_text_replacements(row[0])
        try:
            months = int(float(row[3]))
        except Exception:
            months = 0
        all_members.append((months, 'Twitch', username))

# --- Patreon: parse date in row[18] and calculate months difference ---
with open(patreonSubsFile, 'r') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    for row in reader:
        name = perform_text_replacements(row[0])
        months = 0
        join_date_str = row[18].strip()
        join_date = datetime.strptime(join_date_str, '%Y-%m-%d %H:%M:%S')
        months = months_between_dates(join_date)
        all_members.append((months, 'Patreon', name))

# --- YouTube: use row[4] (months with decimals), round down ---
with open(youtubeSubsFile, 'r', encoding='utf-8') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    for row in reader:
        name = perform_text_replacements(row[0])
        try:
            months = int(float(row[4]))
        except Exception:
            months = 0
        all_members.append((months, 'YouTube', name))

# --- Sort all members by months DESC ---
all_members.sort(key=lambda x: x[0], reverse=True)

# --- Print all members with months ---
print("Months as Member, Platform, Member Name")
for months, platform, member in all_members:
    print(f"{months} months - {platform} - {member} ")

# --- Export to CSV ---
output_csv = 'all_members_months.csv'
with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['MonthsAsMember', 'Platform', 'MemberName'])
    for member, platform, months in all_members:
        writer.writerow([months, platform, member])

print(f"\nCSV file created successfully: {output_csv}")
