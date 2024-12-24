def get_latest_file(pathos, typo):

    iterrer = pathlib.Path(pathos)
    fillos = list(iterrer.rglob(f"*.{typo}"))

    listo = []
    for fillo in fillos:
        datto = datefinder.find_dates(str(fillo))

        for match in datto:
            # print(match)
            listo.append((match, str(fillo)))
        # print(str(fillo))
    
    listo.sort(reverse=True)
    print(listo)
    return listo[0]
