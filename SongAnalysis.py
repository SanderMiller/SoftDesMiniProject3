import wikipedia
import requests
from bs4 import BeautifulSoup
import time
import numpy as np
from pandas import *
from  more_itertools import unique_everseen
import math
import matplotlib.pyplot as plt
from os.path import exists
import sys
from pickle import dump, load

#If the file of pickeled data doesn't Exist
existance = exists('SongData.txt')
if existance == False:
    albumandsongs = []
    album_links= []
    song_links = []
    html = requests.get('https://en.wikipedia.org/wiki/List_of_Billboard_Year-End_number-one_singles_and_albums')
    b = BeautifulSoup(html.text, 'lxml')

    #Scrape the Wikipedia Table for the Billboard #1 Hit Singles and Album Wikipedia Links for every year 1946-2018
    for i in b.find_all(name='table', class_='wikitable'):
        for j in i.find_all(name='tr'):
            for k in j.find_all(name = 'td'):
                for link in j.find_all( href=True):
                    albumandsongs.append(link['href'])

                #Create a list of Billboard #1 Hit Album Wikipedia Links (They're in italics)
                for k in j.find_all(name = 'i'):
                    for link in k.find_all( href=True):
                        album_links.append(link['href'])
   
   # Delete any duplicate entries from the album and song link list
    albumandsongs = list(unique_everseen(albumandsongs))

    #Remove any album and reference links from 
    song_links = [i for i in albumandsongs if i not in album_links ]
    song_links = [ x for x in song_links if "#"  not in x ]


    '''
    Unfortunately the table contained links to both song and artist wikipedia pages. It was difficult differentiating between them. I tried following each link and searching for 
    information such as birthdate to identify and remove artist links, but that greatly increased runtime. Instead I opted to hard code in the song links I wanted.
    '''
    song_links = song_links[0:16:2]+song_links[18:26:2]+song_links[27:36:2]+\
    song_links[36:47:2]+song_links[47:52:2]+song_links[52:59:2]+song_links[61:66:2]+song_links[66:71:2]+\
    song_links[73:74]+song_links[76:80:3]+song_links[76:77]+song_links[80:82]+song_links[83:86:2]+song_links[85:86]+song_links[87:96:2]+\
    song_links[99:104:2]+song_links[105:112:2]+song_links[114:122:3]+song_links[122:130:3]+\
    song_links[130:133:2]+song_links[134:142:3]+song_links[142:144]+song_links[145:152:3]+song_links[153:156:2]+\
    song_links[158:164:3]+song_links[163:166:2]+song_links[170:173:2]+song_links[175:179:2]+song_links[178:181:2]+\
    song_links[183:186:2]+song_links[188:193:4]+song_links[195:204:3]+song_links[203:206:2]+song_links[206:208]+\
    song_links[210:213:2]+song_links[215:222:3]+song_links[223:229:3]+song_links[230:239:3]+song_links[238:240]+\
    song_links[241:243]+song_links[245:246]+song_links[245:248:2]+song_links[250:257:3]+song_links[257:271:3]+song_links[271:275:3]+\
    song_links[276:282:2]+song_links[283:294:3]+song_links[294:296]+song_links[298:301:2]+song_links[303:310:2]+\
    song_links[309:310]+song_links[310:315:2]+song_links[317:321:3]+song_links[324:329:3]+song_links[328:333:3]+\
    song_links[335:349:3]+song_links[347:348]+song_links[350:352]+song_links[354:360:3]+song_links[359:363:2]+\
    song_links[364:370:3]+song_links[369:373:2]+song_links[372:376:3]+song_links[377:383:2]+song_links[382:384]+\
    song_links[387:390:2]+song_links[390:392]+song_links[393:396:2]+song_links[398:400]+song_links[401:405:3]+\
    song_links[406:408]+song_links[410:412]+song_links[414:419:3]+song_links[419:423:2]+song_links[424:426]+\
    song_links[427:430:2]+song_links[432:435:2]+song_links[437:442:2]+song_links[441:442]+song_links[445:448:2]+\
    song_links[447:448]+song_links[450:453:2]+song_links[455:460:4]+song_links[461:465:2]+song_links[467:470:2]+\
    song_links[472:474]+song_links[475:476]+song_links[475:476]+song_links[476:477]

    #A few entries had missing or incorrect links, they are added/fixed here
    song_links.insert(8, '/wiki/Bouquet_of_Roses_(song)')
    song_links.insert(37, '/wiki/What_Am_I_Living_For')
    song_links.insert(55, '/wiki/My_Guy')
    song_links.insert(82, '/wiki/Let%27s_Get_It_On_(song)')


    #Broke the master list of links into lists based on genre
    popSongs = song_links[::3]
    soulSongs = song_links[1::3]
    countrySongs = song_links[2::3]

    #Used pandas library to scrape the wiki cite for the table and create a data frame to store all the information, indexed by genre and year
    hitsList= pandas.read_html('https://en.wikipedia.org/wiki/List_of_Billboard_Year-End_number-one_singles_and_albums', header=0, index_col=0)
    hitsList = hitsList[0]
    hitsList = hitsList.drop(['Single'])

    #Renamed dataframe columns
    hitsList.rename(
        columns={
            "R&B/Soul/Hip-hop": "Pop Length",
            "Country": "R&B/Soul/Hip-hop",
            "Unnamed: 4": "R&B/Soul/Hip-hop Length",
            "Unnamed: 5": "Country",
            "Unnamed: 6": "Country Length"
        },
        inplace=True)

    genres = ['Pop', 'R&B/Soul/Hip-hop', 'Country']
    linkList = [popSongs, soulSongs, countrySongs]
    points = []
    average = []

    #Go through each genre and pull the corresponding list of links
    for i in range(len(genres)):
        genre = genres[i]
        links = linkList[i]
        
        #iterate through each year from 1946 to 2018
        for j in range(len(hitsList[genre])):
            time.sleep(1) #delay between wikipedia requests
            #Remove stray character in Dataframe song name entries 
            s1 = hitsList.loc[str(1946+j),genre]
            firstDelPos1=s1.find("[") # get the position of [
            secondDelPos1=s1.find("]") # get the position of ]
            stringAfterReplace1 = s1.replace(s1[firstDelPos1:secondDelPos1+1], " ") # replace the string between two delimiters
            hitsList.loc[str(1946+j),genre] = stringAfterReplace1

            #create the url to access the wiki page for each song
            url = 'https://en.wikipedia.org' + links[j]
            
            #Search the song wiki page to see if they contain a table
            try:
                SongInfo = pandas.read_html(url, header=0, index_col=0)
                for i in range(len(SongInfo)):
                    #Select table with Length listed
                    if 'Length' in SongInfo[i].index:
                        SongInfo = SongInfo[i]
                        #Set Length equal to listed length
                        Length = SongInfo.loc['Length', 'Unnamed: 1']
                        break
    
                    #If no length is listed song length is 'NA'
                    else:
                        Length = 'NA'
                        Lengthsecs = 'NA'

                #Hard coded one exception that came up
                if Length == 'approx. 3 minutes':
                    Length = '3:00'

                #Cut length off to first 4 characters listed (X:XX)
                if len(Length)>=4:
                    Length = Length[0:4]

                #For listed lengths converted to total seconds
                if len(Length) == 4:
                    mins = int(Length[0])
                    secs = int(Length[2:4])
                    Lengthsecs = (60*mins) +secs

                    #Added year and song length in seconds to the list points
                    points.extend([1946+j, Lengthsecs])

            #Run exception if there is no table on the song's wiki page
            except ValueError:
                #Set length to 'NA'
                Length = 'NA'
                Lengthsecs = 'NA'          
        
            
            #Add the song lengths in seconds to the Dataframe
            hitsList.at[str(1946+j), genre + ' Length'] = Lengthsecs

    #Create new column for dataframe, arbitrarily set to the 'Country' entries, will be overwritten later
    hitsList["Average Length"] = hitsList['Country']
    
    #For each year find the average of the top hits from all three genres
    for k in range(len(hitsList[genre])):
        #Create a list of the Lengths of each top hit
        lengths = [hitsList.at[str(1946+k), 'Pop Length'], hitsList.at[str(1946+k), 'R&B/Soul/Hip-hop Length'], hitsList.at[str(1946+k), 'Country Length']]
        #Get rid of any non integer lengths ('NA')
        lengths = [ a for a in lengths if type(a) == int ]
       
        #If all three songs have an integer length add them up and divide by 3
        if len(lengths)>2:
            #add the averages to the dataframe
            hitsList.loc[str(1946+k), 'Average Lengths'] = sum(lengths)/len(lengths)

            #add the year and average to the points list
            points.extend([1946+k, sum(lengths)/len(lengths)])

    print(hitsList)

    #Pickel the Song length data
    f = open('SongData.txt', 'wb')
    dump(points, f)
    f.close()

    #Assign the data to the appropriate genre/average
    popPoints = points[0:136]
    soulPoints = points[136:264]
    countryPoints = points[264:388]
    average = points[388::]

#If the file with the pickeled data exists access it
else:
    f = open('SongData.txt', 'rb')
    points = load(f)  
    f.close()

    #Assign the data to the appropriate genre/average 
    popPoints = points[0:136]
    soulPoints = points[136:264]
    countryPoints = points[264:388]
    average = points[388::]
   
    
#Plot the Results
plt.plot(average[::2], average[1::2], color = 'red')
plt.scatter(average[::2], average[1::2], color = 'red', label = 'Average')
plt.scatter(popPoints[::2], popPoints[1::2], color = 'blue', label = 'Pop')
plt.scatter(soulPoints[::2], soulPoints[1::2], color = 'green', label = 'R&B/Soul/Hip-hop')
plt.scatter(countryPoints[::2], countryPoints[1::2], color = 'yellow', label = 'Country')
plt.title('Song Length of Billboard Year-End Number One Singles ')
plt.xlabel('Time (Years)')
plt.ylabel('Song Length (Seconds)')
plt.legend()

plt.show()
