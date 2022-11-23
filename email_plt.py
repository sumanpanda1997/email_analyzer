from matplotlib import pyplot as plt
import numpy as np
import csv

from wordcloud import WordCloud

import os
import shutil

def create_output_dir():
    if os.path.exists("assets"):
        shutil.rmtree('assets')
    os.makedirs("assets")

def pie_chart():
    counter = 0
    with open('./output/prediction_count.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        label=[]
        value=[]
        for row in reader:
            try:
                value.append(int(row[1]))
                label.append(row[0])
            except:
                counter += 1
    #print(label,value)
    prediction_count_array=np.array(value)
    plt.pie(prediction_count_array, labels=label)
    plt.savefig("./assets/pie_chart.png")
    plt.close()


def word_cloud(): 
    # ignore 1st line
    counter=0
    d = {}
    # opening the CSV file
    with open("./output/word_cloud.csv", mode ='r')as file:
        # reading the CSV file
        csvFile = csv.reader(file)
        # displaying the contents of the CSV file
        for lines in csvFile:
                try:
                    d[lines[0]] = int(lines[1])
                except:
                    counter +=1


    wordcloud = WordCloud()
    wordcloud.generate_from_frequencies(frequencies=d)
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig("./assets/word_cloud.png")
    plt.close()


def histogram():
    max = 0
    with open('./output/duration.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        value=[]
        counter = 0
        for row in reader:
            try:
                if int(row[1]) > max:
                    max=int(row[1])
                value.append(int(row[1]))
            except:
                counter +=1

    # Creating dataset
    email_count_array = np.array(value)
    # Creating histogram
    fig, ax = plt.subplots(figsize =(10, 7))
    ax.hist(email_count_array, bins=max+1, rwidth=0.6)

    plt.gca().set(title='Frequency Histogram', ylabel='Frequency')
    # Show plot
    plt.savefig("./assets/histogram.png")
    plt.close()

def driver():
    create_output_dir()
    histogram()
    word_cloud()
    pie_chart()