from __future__ import division
from pprint import pprint
from scapy.all import *
import scipy

import ConfigParser

import os.path

import json

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

Config = ConfigParser.ConfigParser()

if os.path.isfile('settings.conf'):
	Config.read("settings.conf")
	total_average_percentage = float(ConfigSectionMap("Percentages")['total_average_percentage'])
	total_average_good_bigram_percentage = float(ConfigSectionMap("Percentages")['total_average_good_bigram_percentage'])
	total_bigrams_settings = float(ConfigSectionMap("Values")['total_bigrams_settings'])
else:
	cfgfile = open("settings.conf",'w')
	Config.add_section('Percentages')
	Config.add_section('Values')
	Config.set('Percentages','total_average_percentage', 0)
	Config.write(cfgfile)
	cfgfile.close()

def train_data():

    if os.path.isfile('database.json'):

	with open('database.json', 'r') as f:
	    try:
	        bigram_list = json.load(f)
	        process_data(bigram_list, total_bigrams_settings) #Call process_data
	    # if the file is empty the ValueError will be thrown
	    except ValueError:
	        bigram_list = {}

    else:

		training_data = open('alexa_top_10k_domain.txt').read().splitlines() #Import alexa top domains 
		bigram_list = {} #Define bigram_list
		total_bigrams = 0 #Set initial total to 0
		for word in xrange(len(training_data)): #Run through each word in the training list
			print "Processing domain:", word #Print word number in list
			for  bigram_position in xrange(len(training_data[word]) - 1): #Run through each bigram in word
				total_bigrams = total_bigrams + 1 #Increment bigram total
				if training_data[word][bigram_position:bigram_position + 2] in bigram_list: #Check if bigram already exists in dictionary
					bigram_list[training_data[word][bigram_position:bigram_position + 2]] = bigram_list[training_data[word][bigram_position:bigram_position + 2]] + 1 #Increment dictionary value by 1
				else:
					bigram_list[training_data[word][bigram_position:bigram_position + 2]] = 1 #Add bigram to list and set value to 1

		pprint(bigram_list) #Print bigram list
		with open('database.json', 'w') as f:
			json.dump(bigram_list, f)

		process_data(bigram_list, total_bigrams) #Call process_data

def checkList(percentage, total_average_percentage):
    for i in range(len(percentage) - 1):
        if percentage[i] < total_average_percentage and percentage[i+1] < total_average_percentage and percentage[i+1] < total_average_percentage:
            return True
    return False


def process_data(bigram_list, total_bigrams):

	data = open('dgapro.txt').read().splitlines()
	percentage = [] #Define percentage
	percentage_list = [] #Define average_percentage

	for word in xrange(len(data)): #Run through each word in the data
		for  bigram_position in xrange(len(data[word]) - 1): #Run through each bigram in the data
			if data[word][bigram_position:bigram_position + 2] in bigram_list: #Check if bigram is in dictionary 
				percentage.append((bigram_list[data[word][bigram_position:bigram_position + 2]] / total_bigrams) * 100) #Get bigram dictionary value and convert to percantage
			else:
				percentage.append(0) #Bigram value is 0 as it doesn't exist

		percentage_list.append(scipy.mean(percentage)) #Add percentage value to list for total average
		print data[word], "AP:", scipy.mean(percentage) #Print word and percentage list
		percentage = [] #Clear percentage list
	
	total_average_percentage = scipy.mean(percentage_list)

	good_bigrams = 0 #Define good_bigrams. Good_bigram is any bigram within the word that has a higher percentage than the average DGA bigram.
	good_bigrams_percentage_list = []

	for word in xrange(len(data)): #Run through each word in the data
		for  bigram_position in xrange(len(data[word]) - 1): #Run through each bigram in the data
			if data[word][bigram_position:bigram_position + 2] in bigram_list: #Check if bigram is in dictionary 
				percentage.append((bigram_list[data[word][bigram_position:bigram_position + 2]] / total_bigrams) * 100) #Get bigram dictionary value and convert to percantage
				if ((bigram_list[data[word][bigram_position:bigram_position + 2]] / total_bigrams) * 100) > total_average_percentage: #Check if bigram percentage is greater than the average DGA bigram percentage
					good_bigrams = good_bigrams + 1 #Increment good_bigram
			else:
				percentage.append(0) #Bigram value is 0 as it doesn't exist

		good_bigrams_percentage = ((good_bigrams / len(percentage)) * 100)
		good_bigrams_percentage_list.append(good_bigrams_percentage)


		print data[word], "AP:", scipy.mean(percentage), "GBP:", good_bigrams_percentage #Print word and percentage list
		percentage = [] #Clear percentage list
		good_bigrams = 0


	print 67 * "*"
	print "Total Average Percentage:", scipy.mean(percentage_list) #Get average percentage
	print "Total Average Good Bigram Percentage:", scipy.mean(good_bigrams_percentage_list)
	print 67 * "*"

	cfgfile = open("settings.conf",'w')
	Config.set('Percentages','total_average_percentage', scipy.mean(percentage_list))
	Config.set('Percentages','total_average_good_bigram_percentage', scipy.mean(good_bigrams_percentage_list))
	Config.write(cfgfile)
	cfgfile.close()


	good_bigrams = 0
	percentage = [] #Define percentage

def check_domain(domain):

	for  bigram_position in xrange(len(domain) - 1): #Run through each bigram in the data
		if domain[bigram_position:bigram_position + 2] in bigram_list: #Check if bigram is in dictionary 
			percentage.append((bigram_list[domain[bigram_position:bigram_position + 2]] / total_bigrams_settings) * 100) #Get bigram dictionary value and convert to percantage
			if ((bigram_list[domain[bigram_position:bigram_position + 2]] / total_bigrams_settings) * 100) > total_average_percentage: #Check if bigram percentage is greater than the average DGA bigram percentage
				good_bigrams = good_bigrams + 1 #Increment good_bigram
		else:
			percentage.append(0) #Bigram value is 0 as it doesn't exist
	good_bigrams_percentage = ((good_bigrams / len(percentage)) * 100)
	print domain, percentage, "AP:", scipy.mean(percentage), "GBP:", good_bigrams_percentage #Print word and percentage list

	if total_average_percentage >= scipy.mean(percentage):
		return 1
	elif total_average_good_bigram_percentage >= good_bigrams_percentage:
		return 1
	else:
		return 0

	percentage = [] #Clear percentage list
	good_bigrams = 0

def capture_traffic(pkt):
	if IP in pkt:
		ip_src = pkt[IP].src
		ip_dst = pkt[IP].dst
		if pkt.haslayer(DNS) and pkt.getlayer(DNS).qr == 0:
			#sep = '.'
			#domain = (pkt.getlayer(DNS).qd.qname).split(sep, 1)[0]
			domain = (pkt.getlayer(DNS).qd.qname)
			if "localdomain" not in domain and len(domain) > 4:
				if check_domain(domain) == 1:
					print "Warning! Potential DGA Detected ", "(" + domain + ")"
				else:
					print "Safe domain", "(" + domain + ")"

def testing():

	data = open('dgapro.txt').read().splitlines()

	if os.path.isfile('database.json'):
		with open('database.json', 'r') as f:
		    try:
		        bigram_list = json.load(f)
		    # if the file is empty the ValueError will be thrown
		    except ValueError:
		        bigram_list = {}
	flag = 0
	total_flags = 0
	good_bigrams = 0
	percentage = [] #Define percentage

	for word in xrange(len(data)): #Run through each word in the data

		for  bigram_position in xrange(len(data[word]) - 1): #Run through each bigram in the data
			if data[word][bigram_position:bigram_position + 2] in bigram_list: #Check if bigram is in dictionary 
				percentage.append((bigram_list[data[word][bigram_position:bigram_position + 2]] / total_bigrams_settings) * 100) #Get bigram dictionary value and convert to percantage
				if ((bigram_list[data[word][bigram_position:bigram_position + 2]] / total_bigrams_settings) * 100) > total_average_percentage: #Check if bigram percentage is greater than the average DGA bigram percentage
					good_bigrams = good_bigrams + 1 #Increment good_bigram
			else:
				percentage.append(0) #Bigram value is 0 as it doesn't exist
		good_bigrams_percentage = ((good_bigrams / len(percentage)) * 100)

		total_flags = total_flags + 1

		if total_average_percentage >= scipy.mean(percentage):
			flag = flag + 1
			print data[word], "AP:", scipy.mean(percentage), "GBP:", good_bigrams_percentage, 1 #Print word and percentage list
		elif total_average_good_bigram_percentage >= good_bigrams_percentage:
			flag = flag + 1
			print data[word], "AP:", scipy.mean(percentage), "GBP:", good_bigrams_percentage, 1 #Print word and percentage list
		else:
			print data[word], "AP:", scipy.mean(percentage), "GBP:", good_bigrams_percentage, 0 #Print word and percentage list


		percentage = [] #Clear percentage list
		good_bigrams = 0

	print 67 * "*"
	print "Detection Rate:", flag / total_flags * 100
	print 67 * "*"

ans=True
while ans:
	print 30 * "-" , "MENU" , 30 * "-"
	print ("""
	1. Train Data
	2. Start Capturing DNS
	3. Testing
	4. View Config File
	5. Reset Config File
	6. Exit/Quit
	""")
	print 67 * "-"
	ans=raw_input("Select an option to proceed: ") 
	if ans=="1": 
		train_data()
	elif ans=="2":
		try:
			interface = raw_input("[*] Enter Desired Interface: ")
		except KeyboardInterrupt:
			print "[*] User Requested Shutdown..."
			print "[*] Exiting..."
			sys.exit(1)
		sniff(iface = interface,filter = "port 53", prn = capture_traffic, store = 0)
	elif ans=="3":
	  testing()
	elif ans=="4":
	  print("\n 4")
	elif ans=="5":
	  print("\n 5")
	elif ans=="6":
	  print("\nExiting...") 
	  quit()
	elif ans !="":
	  print("\n Not Valid Choice Try again") 

#Add to a raspberry device, MITM and then use pushnotification to notify of network activity
#Look at length of word 
#0's being added randomly
#Criminals can bypass by using high frequency bigrams




