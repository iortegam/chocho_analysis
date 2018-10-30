#----------------------------------------------------------------------------------------
# Name:
#        setInput.py
#
# Purpose:
#        This is the input file for pltSet.py
#
#----------------------------------------------------------------------------------------
import datetime as dt

#----------------------
# Importan Inputs
#----------------------
#groups     = ['BIR', 'BRE', 'BOU', 'HEI', 'MAI', 'MOH']#, 'IAP']                    #Group ID identifier
groups     = ['BOU']
vaplt      = [50.0, 51.0, 50.8, 50.8, 51.0, 50.8]#, 51.0]                          #standard viewing angle (defined by each group)

#----------------------
# Importan Inputs for plots
#----------------------
versions   =  ['V2']#, 'V1', 'V3', 'V4']                                     #Name of retrieval version to process (v1,v2,v3, or v4)
easplt      = [1,2,3,5,10]                                                  #EAs for plots
eaplt       = 3                                                           #SIngle EA
group4mean  = ['BRE', 'BOU']


#----------------------
#Choose pls to display
#----------------------

pltdoiEx      = True     #CORRELATION PLOT OF DIFFERENT SETTINGS FOR THE SAME GROUP
pltvcorr      = False     #CORRELATION PLOT OF DIFFERENT SETTINGS FOR THE SAME GROUP
pltsig        = False    #BAR PLOT SHOWING % OF DATA BELOW DL AND ABOVE MAX RMS IF FLAGS ARE TRUE
pltts         = False     #PLOT COMPLETE TIME SERIES USING THE FIRST VERSION
plttsdoih     = False     #PLOT TIME SERIES FOR DAYS OF INTEREST (HOURLY MEAN)
pltraw        = False      #PLOT RAW DATA USING the single eaplt input; DATES AND WHAT TO PLOT IS HARDCODED

#----------------------
# Date range to process
#----------------------
doi_cs      = [dt.date(2013,06,17), dt.date(2013,06,18)]                    #days of interest with clear sky
doi_os      = [dt.date(2013,06,12), dt.date(2013,06,16)]                    #days of interest with overcast sky
doi_bs      = [dt.date(2013,06,20), dt.date(2013,06,21)]                    #days of interest with broken clouds sky

#----------------------
#Flag to save Figures in PDF
#----------------------
saveFlg    = False   
#----------------------
#filtering: Flags
#----------------------
fltrFlg    = True                   # Flag to filter the data
szaFlg     = True                   # Flag to filter based on min and max SZA
ofFlg      = True
rmsFlg     = True                   # Flag to filter based on max RMS
LDFlg      = True                   # Flag to filter profiles based on limit of detection
VAFlg      = True
#----------------------
# Values for filtering
#----------------------
maxRMS     = 0.001     	                 # Max Fit RMS to filter data. Data is filtered according to <= maxrms
minSZA     = 0.0                   # Min SZA for filtering
maxSZA     = 90.0                   # Max SZA for filtering
maxOff     = 5.0

#----------------------
# Directories
#---------------------- 
dataDir = '/home/ivan/chocho/data/'

#----------------------
# PDF: Figure name
#----------------------
pltFile  = '/home/ivan/chocho/fig/plttest.pdf'
       