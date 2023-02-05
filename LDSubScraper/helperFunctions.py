import os
import glob

def find_recent_file(dir, prefix):
    # Get the list of all files in the directory
    file_list = glob.glob(dir + "/" + prefix + "*")

    # Sort the list of files by modification time
    if file_list:
        file_list.sort(key=os.path.getmtime)

        # Return the most recent file
        return file_list[-1]

    return None

def performTextReplacements(original, replacementMap):
    for key, value in replacementMap.items():
        original = original.replace(key, value)

    return original

def mergeTiersAcrossPlatforms(allMembers):
    merged_dict = {}
    for key, value in allMembers.items():
        for k, v in value.items():
            if k in merged_dict:
                merged_dict[k].extend(v)
            else:
                merged_dict[k] = v

    return merged_dict

