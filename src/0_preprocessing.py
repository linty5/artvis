from utils import get_current_dir

inputpath = get_current_dir().parent / "data" / "artvis_dump.csv"
outputpath = get_current_dir().parent / "data" / "artvis_cleaned.csv"


total = 0
invalid = 0

with open(inputpath, "r") as i:
    with open(outputpath, "w") as o:
        # turn header to utf-8
        header = "".join([c for c in i.readline() if ord(c) < 128])
        header = header.replace("\n", "")
        o.write(header + "\n")

        numcols = header.count(",") + 1
        for index, line in enumerate(i):
            # drop "\N"
            line = line.replace(",\\N", ",null")

            linearr = line.split(",")
            for i, _ in enumerate(linearr):
                linearr[i] = linearr[i].strip()

                # fix num of quotation marks
                if '"' in linearr[i]:
                    linearr[i] = linearr[i].replace('"', "")
                if "," in linearr[i]:
                    linearr[i] = '"' + linearr[i] + '"'

            # over 10k lines use unquoted delimiters.
            # they can only fixed manually, so we have to drop them.
            debug = True
            if len(linearr) != numcols:
                if debug:
                    print(f"invalid in line {index}: expected {numcols} but got {len(linearr)}")
                    tmpheader = header.split(",")
                    tmpline = linearr
                    while len(tmpheader) < len(tmpline):
                        tmpheader.append("null")
                    while len(tmpline) < len(tmpheader):
                        tmpline.append("null")
                    assert len(tmpheader) == len(tmpline)
                    for i, (a, b) in enumerate(zip(tmpheader, tmpline)):
                        print(f"{i:2d}: {a} -> {b}")
                    print("\n")
                invalid += 1
                continue

            """
             0 a.id
             1 a.firstname
             2 a.lastname
             3 a.gender
             4 a.birthdate
             5 a.deathdate
             6 a.birthplace
             7 a.deathplace
             8 a.nationality
             9 e.id
            10 e.title
            11 e.venue
            12 e.startdate
            13 e.type
            14 e.paintings
            15 e.country
            16 e.city
            17 e.latitude
            18 e.longitude
            """

            # validate format
            # - a.id is a positive integer
            # - a.gender must be "M" or "F"
            # - e.type must be "group" or "solo" or "auction"
            # - e.paintings must be a positive integer
            if not linearr[0].isnumeric():
                linearr[0] = "null"
            if linearr[3] not in ["M", "F"]:
                linearr[3] = "null"
            if linearr[13] not in ["group", "solo", "auction"]:
                linearr[13] = "null"
            if not linearr[14].isnumeric():
                linearr[14] = "null"

            # geolocation
            # - e.latitude and e.longitude must point to a valid location
            try:
                if float(linearr[17]):
                    pass
                if (float(linearr[17]) < -90) or (90 < float(linearr[17])):
                    raise ValueError
            except ValueError:
                linearr[17] = "null"
            try:
                if float(linearr[18]):
                    pass
                if (float(linearr[18]) < -180) or (180 < float(linearr[18])):
                    raise ValueError
            except ValueError:
                linearr[18] = "null"

            # validate date range
            # a.birthdate must be a date with format "YYYY-MM-DD" and range 1400-2024
            # a.deathdate must be a date with format "YYYY-MM-DD" and range 1500-2024
            # the life span must be less than 150 years
            # e.startdate must be a year with format "YYYY" and range 1900-2000
            try:
                birthdate = linearr[4].split("-")
                if len(birthdate) != 3:
                    raise ValueError
                if not (1400 <= int(birthdate[0]) <= 2024):
                    raise ValueError
                if not (1 <= int(birthdate[1]) <= 12):
                    raise ValueError
                if not (1 <= int(birthdate[2]) <= 31):
                    raise ValueError
            except ValueError:
                linearr[4] = "null"
            try:
                deathdate = linearr[5].split("-")
                if len(deathdate) != 3:
                    raise ValueError
                if not (1500 <= int(deathdate[0]) <= 2024):
                    raise ValueError
                if not (1 <= int(deathdate[1]) <= 12):
                    raise ValueError
                if not (1 <= int(deathdate[2]) <= 31):
                    raise ValueError
            except ValueError:
                linearr[5] = "null"
            try:
                birthdate = linearr[4].split("-")
                deathdate = linearr[5].split("-")
                if birthdate[0] == "null" or deathdate[0] == "null":
                    raise ValueError
                if int(deathdate[0]) - int(birthdate[0]) > 150:
                    raise ValueError
            except ValueError:
                linearr[4] = "null"
                linearr[5] = "null"
            try:
                startdate = linearr[12]
                if len(startdate) != 4:
                    raise ValueError
                if not (1900 <= int(startdate) <= 2000):
                    raise ValueError
            except ValueError:
                linearr[12] = "null"

            o.write(",".join(linearr) + "\n")
            total += 1

print(f"total: {total}, invalid: {invalid}")
