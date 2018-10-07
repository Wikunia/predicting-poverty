# convert gps data locations to csv file
import csv

country = "malawi"

with open('../data/output/LSMS/'+country+'/candidate_download_locs.txt') as f:
    content = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
content = [x.strip() for x in content] 


csv_file = open(country+'.csv', mode='w')
img_file = open('../data/output/LSMS/'+country+'/downloaded_locs.txt', mode='w')
csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
img_writer = csv.writer(img_file, delimiter=' ', quotechar='"', quoting=csv.QUOTE_MINIMAL)
csv_writer.writerow(['name','latitude','longitude'])

c = 1
for line in content:
    parts = line.split(' ')
    csv_writer.writerow([country+"_"+str(c),parts[0],parts[1]])
    img_writer.writerow([country+"_"+str(c)+'.png']+parts)
    c += 1
csv_file.close()