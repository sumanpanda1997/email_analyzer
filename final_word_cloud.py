import csv
import matplotlib.pyplot as plt
from wordcloud import WordCloud
 
# ignore 1st line
counter=0
d = {}
# opening the CSV file
with open("./word_cloud.csv", mode ='r')as file:
   
  # reading the CSV file
  csvFile = csv.reader(file)
 
  # displaying the contents of the CSV file
  for lines in csvFile:
  #   print(lines)
        try:
            d[lines[0]] = int(lines[1])
        except:
            counter +=1


wordcloud = WordCloud()
wordcloud.generate_from_frequencies(frequencies=d)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
