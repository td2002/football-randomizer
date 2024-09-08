import comp_tiers as ct
import pprint

file = open("comps_data.txt", "r")
file_out = open("comps_final.txt", "w+")

data = file.readlines()

formatted = []
for s in data:
    tmp = [str.strip(x) for x in s.split("§§§")]
    
    formatted.append( [tmp[1], tmp[2], tmp[0], tmp[3], tmp[4]] )

tiers = []
for x in formatted:
    tiers.append(x[2])

#print(list(set(tiers)))
formatted = sorted(formatted, key=lambda x : (x[0], ct.Tiers_dict[x[1]], x[2]))
#pprint.pprint()

for l in formatted:
    file_out.write(f'{l[0]}§§§{l[1]}§§§{l[2]}§§§{l[3]}§§§{l[4]}\n')

file.close()
file_out.close()