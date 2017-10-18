import os
import sys
import numpy as np
import matplotlib.pyplot as mpl

#------INPUT FUNCTIONS------
def getInput():
    ''' Collects and returns the following information from the user:

        1. filt[list] - A list of format [Product Code, StationID, Year, Month, Day, Measurement, Length, Quality]
            It only makes sense to filter based on Product Code, StationID, Month, and Quality
            All other entries filled with 'None' by default
        2. mode(str) - High or Low. Whether the Measurement sought should be a high value or low value
        3. frequency(int) - describes how rare the event should be
        4. aggI(int) - the aggregation column that should be used when manipulating the data
        5. filename(str) - path to the file to open containing the data to be processed
        6. option
     '''

    # Get filename from User
    while True:
        response0 = input("Please enter the FULL path to the file to process: ").rstrip()
        if not os.path.isfile(response0):
            print("Invalid path. Please check and try again")
        else:
            filename = response0
            break

    # Get Product Code info from User
    while True:
        response1 = input("Do you want rainfall or temperature data? (Enter 'Rainfall' or 'Temperature'):")
        if response1.lower() == 'rainfall' or response1.lower() == 'rain':
            code = 'IDCJAC0009'
            break
        elif response1.lower() == 'temperature' or response1.lower() == 'temp':
            code = 'IDCJAC0010'
            break
        else:
            print("There are only two options: Rainfall or Temperature")

    # Get Station Number from User
    while True:
        response2 = input("Which location do you want the data to come from? (Enter 'Sydney', 'Canberra', 'Queanbeyan' or 'All')")
        if response2.lower() == 'sydney' or response2.lower() == 'syd':
            station = 66062
            break
        elif response2.lower() == 'canberra' or response2.lower() == 'can':
            station = 70247
            break
        elif response2.lower() == 'queanbeyan' or response2.lower() == 'q':
            station = 70072
            break
        elif response2.lower() == 'all' or response2.lower() == 'any':
            station = None
            break
        else:
            print("Please enter 'Sydney', 'Canberra', 'Queanbeyan' or 'All'")


    # New - Get date filters and aggregation method

    print()
    print("**********")
    print("How should the data be aggregated? The options are to: ")
    print()

    if code == 'IDCJAC0009':
        print(" 1) - total the rainfall for each month to produce a monthly timeseries, ")
        print(" 2) - total the rainfall for a specific month, to produce a yearly timeseries, ")
        print(" 3) - total the rainfall for each year to produce a yearly timeseries")
        print(" 4) - Don't aggregate the data. I want a daily timeseries")
        print()

    elif code == 'IDCJAC0010':
        print(" 1) - Find the average temperature for each month to produce a monthly timeseries, ")
        print(" 2) - Find the average temperature for a specific month, to produce a yearly timeseries, ")
        print(" 3) - Find the average for each year to produce a yearly timeseries")
        print(" 4) - Don't aggregate the data. I want a daily timeseries")
        print()

    while True:
        monthfilt = None    #if not set below, should be blank which is None
        response10 = input("Please select which method you wish to use to aggregate the data (Enter '1', '2, '3', or '4'):")
        if int(response10) == 1:
            aggI = 3
            option = 1
            break
        elif int(response10) == 2:
            aggI = 2
            option = 2
            months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
            while True:
                r = input("Which month do you wish to filter by?").lower()
                try:
                    if r in months:
                        monthfilt = months.index(r)+1
                        break
                    else:
                        monthfilt = int(r)
                        break
                except ValueError:
                    print("Please enter a month name (eg. September) or an integer")
            break
        elif int(response10) == 3:
            aggI = 2
            option = 3
            break
        elif int(response10) == 4:
            aggI = 4
            option = 4
            break
        else:
            print("Please enter an integer between 1 and 4")



    #Get Frequency from User
    while True:
        response3 = input("How rare an event are you interested in? (Eg. 1 in 20, enter '20')")
        try:
            if 0 < int(response3) < 2000:
                frequency = int(response3)
                break
            else:
                print("Please enter a value between 0 and 2000")
        except ValueError:
            print("Please enter an integer value between 0 and 2000")


    #Get Mode from User
    while True:
        response4 = input("And should this 1 in " + str(frequency) +" event be a high or a low? (Enter 'High' or 'Low')")
        if response4.lower() == 'high' or response4.lower() == 'h':
            mode = 'high'
            break
        elif response4.lower() == 'low' or response4.lower() == 'l':
            mode = 'low'
            break
        else:
            print("Enter either 'high' or 'low'")

    #Get Quality from User
    while True:
        response5 = input("Do you require that the quality of the data be assured? (Enter 'Yes' or 'No')")
        if response5.lower() == 'yes':
            quality = 'Y'
            break
        elif response5.lower() == 'no':
            quality = None
            break
        else:
            print("Please enter either 'yes' or 'no'")

    #filt = [code, station, None, months, None, None, None, quality]
    filt = [code, station, None, monthfilt, None, None, None, quality]
    return filt, mode, frequency, aggI, filename, option

def openData(path):
    """
    Opens a .csv files that contains rainfall/temperature
    data from BOM
    Returns a list of lists in the form
    [
    Product code: determines the type of data (str),
    Station number (int),
    Year of observation (int),
    Month of observation (int),
    Day of observation (int),
    Observation data: max temp in degrees C or
        rainfall in mm. Depends on the product
        code (float),
    Number of days over which the data was
        recorded (int),
    Quality assurance: Y or N if checked (str)
    ]
    """

    assert os.path.isfile(path), "The input file does not exist"

    data = []
    f = open(path, "r")
    lines = f.readlines()
    f.close()
    for i in range(1, len(lines)):  #skip first line
        line = lines[i]
        count=0
        newrow = []
        for column in line.split(","):
            column = column.rstrip()    #removes any newlines
            if count==0 or count==7:
                #these are strings
                newrow.append(column)
            elif column=="":
                #blank int
                newrow.append(None)
            elif count==5:
                #the observation is a float
                newrow.append(float(column))
            else:
                newrow.append(int(column))
            count+=1
        data.append(newrow)
    return data

#------CALCULATION FUNCTIONS------
def calcThresholdA(X, F, mode):
    '''
    Accepts a dictionary X, an integer F and mode which is either 'high' or 'low'
    For mode == 'high'
    Calculates the smallest value in a sequence such that every value
    greater than or equal to this number
    only appears in the sequence X on average every F position.
    For mode == 'low'
    Calculates the the largest value in a sequence such that every value smaller than
    or equal to this number appears on average every F position
    '''
    index1 = 0
    minimum = 1e9
    threshold = []
    value_list = list(X.values())
    if type(F) != int:  #F is not an integer
        raise ValueError("F is must be an an integer")
    if mode != 'high' and mode != 'low': #invalid mode is entered
        raise ValueError("mode must be either 'high' or 'low'")
    
    if mode == 'high':
        for index in range(len(value_list)):  #Replace missing data with exceptionally low values
            if value_list[index] == None:
                value_list[index] = -1000
        while index1 < len(value_list):
            aboveXindex = [index for index in range(len(value_list)) if value_list[index] >= value_list[index1]]
            for index in range(len(aboveXindex)-1):
                difference = abs(aboveXindex[index+1]-aboveXindex[index])
                if difference < minimum:
                    minimum = difference
            if minimum >= F:  #checks if the smallest difference is at least F
                threshold.append(value_list[index1])
            minimum = 1e9
            index1 += 1
    if mode == 'low':   #Works the same as when mode = high, except the inequalities are reversed
        for index in range(len(value_list)):
            if value_list[index] == None:
                value_list[index] = 1000
        while index1 < len(value_list):
            belowXindex = [index for index in range(len(value_list)) if value_list[index] <= value_list[index1]]
            for index in range(len(belowXindex)-1):
                difference = abs(belowXindex[index+1]-belowXindex[index])
                if difference < minimum:
                    minimum = difference
            if minimum >= F:
                threshold.append(value_list[index1])
            minimum = 1e9
            index1 += 1
    if len(threshold) != 0:
        if mode == 'high':          #Returns smallest threshold for mode == 'high'
            threshold_value = min(threshold)
            key = [value for value in X if X[value] == threshold_value]
            return threshold_value, key
        if mode == 'low':           #Returns largest threhold for mode == 'low'
            threshold_value = max(threshold)
            key = [value for value in X if X[value] == threshold_value]
            return threshold_value, key
    print ('No values in the sequence, satisfy this condition')

def calcThresholdB(X, F, mode):
    '''
    Accepts a dictionary X, an integer F and mode which is either 'high' or 'low'
    For mode == 'high'
    Calculates the smallest value in a sequence such that the number of value
    greater than it is less than n/F where n is the length of X
    For mode == 'low'
    Calculates the the largest value in a sequence such that number of values
    smaller than it is less than or equal to n/F where n is the length of X
    '''
    #Albert - mabye state what this function returns in the docstring
    assert type(X) == dict, "X must be a dictionary"
    value_list = list(X.values())
    if type(F) != int:  #F is not an integer
        raise ValueError("F is must be an an integer")
    if mode != 'high' and mode != 'low': #invalid mode is entered
        raise ValueError("mode must be either 'high' or 'low'")
    values = [value for value in value_list if value != None] #Removes None values
    values.sort()

    #Make sure that the list "X" does not only contain None values
    assert values!=[], "There is no useable data for this aggregation"

    quantile = len(values)//F
    if mode == 'high':
        threshold = values[-quantile]
        key = [value for value in X if X[value] == threshold]
        return threshold, key
    if mode == 'low':
        threshold = values[quantile-1]
        key = [value for value in X if X[value] == threshold]
        return threshold, key

#------TOOLS------
def filterData(data, filt):
        """
        Returns a new list of items, but only items
        that pass the "filt" comparison test
        'filt' is a list of the same length as a 'data'
        item, and contains objects that will be compared to
        each corresponding item in each row to determine if the
        row should be added to the new list
        """

        assert len(filt)==len(data[0]), "Incorrect filter length"

        newdata = []
        for row in data:
            passed = True
            for i in range(0, len(filt)):
                #filter should be the length of each item
                a = row[i]
                b = filt[i]
                if b!=None and a!=b: #None is a blank filter
                    passed = False
                    break
            if passed==True:
                newdata.append(row)

        return newdata

def aggregateData(data, dataType, option):
    """
    Returns a dictionary of {aggregation1: valueSum1, ...}
    "aggI" is the column index to be used for aggregation
    "valI" is the column of values to be grouped/summed
    "dataType" is either "IDCJAC0009" or "IDCJAC0010"
    This function groups all values in column index "valI"
    together IF they have the same values in column index
    "aggI"
    Does not assume that aggregated data is in order
    CURRENTLY - aggregations that include a "None" value
    are given "None"

    assume no observations on leap days
    """
    #print("aggI=", aggI, "valI=", valI, "data[0]=", data[0])
    #assert 0<aggI<len(data[0]), "Impossible aggregation column number"
    #assert 0<valI<len(data[0]), "Impossible value column number"
    #assert type(data[0][valI])==int or type(data[0][valI])==float, "Can't aggregate non-integer/float values" - NOT TRUE IF FIRST OBSERVATON IS NONE
    assert dataType=="IDCJAC0009" or dataType=="IDCJAC0010", "Incorrect data type"
    assert 1<=option<=4, "Wrong option number. 'option' must be 1, 2, 3 or 4"

    #print("Start aggregateData\naggI =", aggI, "dataType =", dataType, "option =", option)

    #GROUP/AGGREGATE ALL OF THE DATA
    #Group like this: {agg: a list of "data" rows,...}
    grouped = {}
    for row in data:
        if option == 1:
            aggregation = int( str(row[2]) + str(row[3]) )  #ints compute fast
        elif option==2 or option==3:
            aggregation = row[2]
        else:# option == 4
            aggregation = int(str(row[2])+str(row[3])+str(row[4]))

        if aggregation in grouped:
            grouped[aggregation].append(row)
        else:
            grouped[aggregation] = [row]

    #CHECK IF THE AGGREGATION IS USEABLE AND SUM
    #   OPTION  #DESCRIPTION                        AGGREGATION aggI    OBS. CONDITION              REQUIRED # of OBS
    #   1       Sum months seperately               Monthly     3       Observations in same month  Same # of obs. as days in the particular month
    #   2       Sum a specific month for each year  Yearly      2       Observations in same month  Same # of obs. as days in the particular month
    #   3       Sum each year                       Yearly      2       Observations in same year   365/366 observations per group
    #   4       No aggregation, return each obs     Daliy       4       None                        None

    results = {}
    daysEachMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    #daysEachYear = depends on year
    for group in grouped:

        items = grouped[group]  #these are "data" rows

        #Get number of observation days and the sum of observations
        observationDays = 0 #no. of observation days for a group/aggregation
        observationSum = 0  #sum of observations for a group (ignores Nones)
        for item in items:
            if item[5]!=None:
                observationSum += item[5]
                if item[6]==None:   #Observation of 0 gets None here
                    observationDays += 1
                else:
                    observationDays += item[6]

        #print("Group:", group, "observationDays=", observationDays, "observationSum=", observationSum)

        #-----CHECK IF THE AGGREGATION IS USEABLE-----
        #Check that the observation condition is satisfied
        if option==1 or option==2:
            #Check all observations in this group are in the same month
            months = [x[3] for x in items]
            obsCondCheck = all([x==months[0] for x in months])
        elif option==3:
            #Option 3. Check all observations in this group are in the same year
            years = [x[2] for x in items]
            obsCondCheck = all([x==years[0] for x in years])
        else:
            #there is no condition
            obsCondCheck = True

        #Check that there are the required number of observations
        if option==1 or option==2:
            #Same # of obs as days in the specific month
            month = items[0][3] #all the same month in this case
            requiredNo = daysEachMonth[month-1]
            requiredNoCheck = observationDays==requiredNo
        elif option==3:
            ## observations=# of days in the current year
            year = items[0][2]  #all the same year in this case
            if year%4==0:
                requiredNo = 366    #leap year
            else:
                requiredNo = 365
            requiredNoCheck = observationDays==requiredNo
        else:
            #there is no condition
            requiredNoCheck = True

        #----------------------------------------------

        #print("- obsCondCheck=", obsCondCheck, "requiredNoCheck=", requiredNoCheck)

        if not (obsCondCheck and requiredNoCheck):
            results[group] = None
        else:
            if dataType == "IDCJAC0009":
                results[group] = observationSum
            else:
                results[group] = observationSum/observationDays

        """

            #Get input will only ever output aggregation indexes of 2 or 3 (y or m)
            #If 3, months will be grouped. This h
            if aggI==3: #monthly aggregation
                month = items[0][4] #get the month (all are the same)
                correctNoOfObs = daysEachMonth[month-1]
                elif aggI==2:   #yearly aggregation
                correctNoOfObs = daysEachYear
            else:
                print("I dont know what to do here...! aggI=", aggI)

                if observationDays<correctNoOfObs:
                #There are holes
                check = False
            elif observationDays>correctNoOfObs:
                print("What the hell how can there be more observations than days???")
                check = False
                #else:
                #   exactly the same no. of days as observations. Sweet!

                #Quit if already useless
                if check == False:
                    results[group] = None



                    #Add the data to the "results" dict. this
                    #will be a sum or average depending on the
                    #"dataType"
                    #if dataType == "IDCJAC0009":
                    #        results[group] = observationSum
                    #        else:
                    #results[group] = observationSum/observationDays

        """

    #Make sure that the list "X" does not only contain None values
    #This might happen if you filter for a month, and aggregate monthly
    #assert not all([x==None for x in results.values()]), "There is no useable data for this aggregation"

    return results

#------OUTPUT FUNCTIONS------
def outputResults(x):
    """
    Hurry up and write this Michael you slave!
    """
    pass

def displayGraph(agg_data, method_A_threshold, method_B_threshold):
    years = list(agg_data.keys())
    y = []
    for thing in list(agg_data.values()):
        if thing!=None:
            y.append(thing)
        else:
            y.append(0) #hole
    x = np.arange(0, len(y))
    mpl.bar(x + 0.25, y, 0.5, color='blue')
    mpl.plot([0, len(y) + 1], [method_A_threshold[0], method_A_threshold[0]], '--r')  # the threshold line
    mpl.plot([0, len(y) + 1], [method_B_threshold[0], method_B_threshold[0]], '--g')  # the threshold line
    mpl.xticks(x + 0.5, years, rotation=90)
    mpl.show()

#--------MAIN PROGRAM---------

#Get input file from User
filt, mode, frequency, aggI, filename, option = getInput()
#print("filt=", filt)
#print(filt, mode, frequency, aggI, filename)
code = filt[0]
#Assignment example:
#filt = ['IDCJAC0009', 70247, None, 5, None, None, None, None]
#mode = "high"
#frequency = 20
#aggI = 2
#filename = "/Users/michaelvernon/Google Drive/weather/Rainfall_Canberra_070247.csv"
#filename2 = "C:/Users/Jack/Google Drive/weather/Rainfall_Canberra_070247.csv"

#Open the data file
data = openData(filename)
print()
print("aggI is", aggI)
print()
print("filt is:", filt)
print()

#Filter the data based on user input. Quit if it filters everything
clean_data = filterData(data, filt)
if clean_data == []:
    print("There is no data that fits the parameters you provided. This program will now finish")
    sys.exit()

#Aggregate the data. Quit if useless
agg_data = aggregateData(clean_data, code, option)
print("Aggregated data:", agg_data, len(agg_data), "\n")
if all([x==None for x in agg_data.values()]):
    print("There is no data that fits the parameters you provided. This program will now finish")
    sys.exit()

#Calculate thresholds
method_A_threshold = calcThresholdA(agg_data, frequency, mode)
method_B_threshold = calcThresholdB(agg_data, frequency, mode)
print("calcThresholdA result:", method_A_threshold)
print("calcThresholdB result:", method_B_threshold)

displayGraph(agg_data, method_A_threshold, method_B_threshold)
