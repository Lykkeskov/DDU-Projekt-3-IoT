#tal af hvor stor emails er
size = [120, 1000, 90, 133, 124, 122, 99]

MB = []
KB = []

#sortere efter størrelse
for item in size:
    if item < 1000:
       KB.append(item) 
    else:
        MB.append(item)

#find CO2 udput 
CO2 = (0.3 * len(KB)) + (50 * len(MB))
print(CO2)
