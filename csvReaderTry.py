import csv
import numpy as np
import matplotlib.pyplot as plt

def getRSSI(name,antennaNum):
	column=[]
	with open(name,'r') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			if row[1]==antennaNum:
				column.append(float(row[3]))
		return column, len(column)

		
def getPhase(name,antennaNum):
	column=[]
	with open(name,'r') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			if row[1]==antennaNum:
				column.append(float(row[5]))
		return column
		

def getT(num):
	T=[]
	for i in range(0,num):
		T.append(i)
	return T
	
name = input("FileName:")
	
while(name!="1"):
	RSSI_1,num_1=getRSSI(name,"1");
	T_1=getT(num_1)

	RSSI_2,num_2=getRSSI(name,"2");
	T_2=getT(num_2)

	RSSI_3,num_3=getRSSI(name,"3");
	T_3=getT(num_3)

	RSSI_4,num_4=getRSSI(name,"4");
	T_4=getT(num_4)

	Phase_1=getPhase(name,"1");
	Phase_2=getPhase(name,"2");
	Phase_3=getPhase(name,"3");
	Phase_4=getPhase(name,"4");


	fig, (ax1, ax2) = plt.subplots(2, 1)
	plt.title(name, y=2.5)
	fig.subplots_adjust(hspace=0.5)
	ax1.plot(T_1, Phase_1, label='Antenna One')
	ax1.plot(T_2, Phase_2, label='Antenna Two')
	ax1.plot(T_3, Phase_3, label='Antenna Three')
	ax1.plot(T_4, Phase_4, label='Antenna Four')
	ax1.legend(loc = 7)
	ax1.set_xlim(0, max(num_1,num_2,num_3,num_4))
	ax1.set_xlabel('time')
	ax1.set_ylabel('Phase')
	ax1.grid(True)

	ax2.plot(T_1, RSSI_1, label='Antenna One')
	ax2.plot(T_2, RSSI_2, label='Antenna Two')
	ax2.plot(T_3, RSSI_3, label='Antenna Three')
	ax2.plot(T_4, RSSI_4, label='Antenna Four')
	ax2.legend(loc = 7)
	ax2.set_xlim(0, max(num_1,num_2,num_3,num_4))
	ax2.set_xlabel('time')
	ax2.set_ylabel('RSSI')
	ax2.grid(True)

	plt.savefig(name+".png")
	plt.show()
	print("You can input number 1 to stop")
	name = input("FileName:")



