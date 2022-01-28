import json, os
from config import CONFIG

def firstChange():
    for table, infos in CONFIG.DataSources.items():
        if ('time' not in infos["data_structure"] if "data_structure" in infos else True):
            continue
        infos["data_structure"].update({
            "time_" + column: [specs[0]] + infos["data_structure"]["time"][1:]
            for column, specs in infos["data_structure"].items()
            if column!='time'})
        print(infos["data_structure"].pop('time', None))
        infos["index"] = "time"

    with open(os.path.join(CONFIG.DataDirectory, "data_sources.json"), "w") as file:
        json.dump(CONFIG.DataSources, file, indent=2)


def secondChange():
    for table, infos in CONFIG.DataSources.items():
        extension = infos["filename"].split('.')
        if len(extension)>1:
            infos["format"] = extension[-1]
    
    with open(os.path.join(CONFIG.DataDirectory, "data_sources.json"), "w") as file:
        json.dump(CONFIG.DataSources, file, indent=2)


if __name__ == '__main__':
    # firstChange()
    secondChange()
