import matplotlib.pyplot as plt
import numpy as np
import csv

with open('records.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)
    label=[]
    value=[]
    for row in reader:
        label.append(row[0])
        value.append(int(row[1]))
#print(label,value)


#y = np.array([35,25,25,15])
y=np.array(value)
#mylabels = ["Apples", "Bananas", "Cherry", "Dates"]
plt.pie(y, labels = label)
plt.show()
