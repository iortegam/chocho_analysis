#----------------------------------------------------------------------------------------
# Name:
#        classgly.py
#
# Purpose:
#       This is a collection of classes and functions used for processing and ploting 
#       chocho output
#
#----------------------------------------------------------------------------------------

import datetime as dt
import time
import math
import sys
import numpy as np
import os
import csv
import itertools
from collections import OrderedDict
import os
from os import listdir
from os.path import isfile, join
import re
from scipy.integrate import simps
import matplotlib
from collections import namedtuple
# Force matplotlib to not use any Xwindows backend.
#matplotlib.use('Agg')
import matplotlib.dates as md
from matplotlib.dates import DateFormatter, MonthLocator, YearLocator
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FormatStrFormatter, MultipleLocator,AutoMinorLocator,ScalarFormatter
from matplotlib.backends.backend_pdf import PdfPages #to save multiple pages in 1 pdf...
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import matplotlib.gridspec as gridspec
import matplotlib.gridspec as gridspec

from datetime import timedelta

from sklearn import linear_model, datasets
from scipy import stats

                                            #------------------#
                                            # Define functions #
                                            #------------------#

def ckDir(dirName,logFlg=False,exitFlg=False):
    ''' '''
    if not os.path.exists( dirName ):
        print 'Input Directory %s does not exist' % (dirName)
        if logFlg: logFlg.error('Directory %s does not exist' % dirName)
        if exitFlg: sys.exit()
        return False
    else:
        return True   

def ckFile(fName,logFlg=False,exitFlg=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print 'File %s does not exist' % (fName)
        if logFlg: logFlg.error('Unable to find file: %s' % fName)
        if exitFlg: sys.exit()
        return False
    else:
        return True

def toYearFraction(dates):
    ''' Convert datetime to year and fraction of year'''

    #def sinceEpoch(date): # returns seconds since epoch
        #return time.mktime(date.timetuple())
    #s = sinceEpoch
    ep_fnc = lambda x: time.mktime(x.timetuple())


    retrnDates = np.zeros(len(dates))
    
    for i,sngDate in enumerate(dates):
        year = sngDate.year
        startOfThisYear = dt.datetime(year=year, month=1, day=1)
        startOfNextYear = dt.datetime(year=year+1, month=1, day=1)
    
        yearElapsed = ep_fnc(sngDate) - ep_fnc(startOfThisYear)
        yearDuration = ep_fnc(startOfNextYear) - ep_fnc(startOfThisYear)
        fraction = yearElapsed/yearDuration
        retrnDates[i] = sngDate.year + fraction

    return retrnDates

def doytodate(doy, ft, iyear = ''):
    ''' Convert fraction of year to date time'''

    #http://stackoverflow.com/questions/20911015/decimal-years-to-datetime-in-python
    
    
    #start = [float(iyear) + int(val)/365.0  + ft[i]/24.0/365.0 for i, val in enumerate(doy)]
    
    #for i, dd in enumerate(np.asarray(doy)):
    #    print i, int(dd)

    doy_i = [int(i) for i in np.asarray(doy)]
    #ft_i = [int(i) for i in np.asarray(ft)]

    #print doy[0]
    #print ft[0]
    #print doy_i[0]
    #print ft_i[0]


    #print np.array(doy_i[0])/365.0 + np.array(ft[0])/24.0/365.0
    #print doy[0]
    #exit() 
    start = float(iyear) + np.array(doy_i)/365.0  + np.asarray(ft)/24.0/365.0

    year = [int(i) for i in np.asarray(start)] 
    rem = np.asarray(start) - year
    
    #print start[0]
    #print year[0]
    #print rem[0]
    
    base = dt.datetime(iyear, 1, 1)

    retrnDates = [base + dt.timedelta(seconds=(base.replace(year=base.year + 1) - base).total_seconds() * i) for i in rem]
    #retrnDates = [base + dt.timedelta(days=() - base).total_seconds() * i) for i in rem]
    #retrnDates = dt.datetime(iyear, 1, doy, 0,0, fts)
    #retrnDates = dt.datetime(2013, 1, 12, 0,0, 5.1)
    #print retrnDates[0]
    

    return retrnDates

def clrplt():
    ''' Colors for plots in order for for loops'''
    
    clr = ('green', 'red', 'maroon', 'blue', 'gray', 'orange', 'cyan')
    return clr

def getgroupname(group):
    ''' Get the name of the group'''

    if group == 'BIR': groupn = 'BIRA'
    elif group == 'BRE': groupn = 'Bremen'
    elif group == 'BOU': groupn = 'Boulder'
    elif group == 'MAI': groupn = 'MPIC'
    elif group == 'MOH': groupn = 'Mohali'
    elif group == 'HEI': groupn = 'Heidelberg'
    else: groupn = group

    return groupn

def detectionlimit(rms):
    ''' Know the detection limit based on RMS'''
    
    xs = 5.0e-19  #CHOCHO
    DL = (1.0*rms)/xs

    DL = np.asarray(DL)

    return DL

def hourAvg(data, dates, idate, fdate, dateAxis=1, meanAxis=0, quad=0):
    ''' Creates daily averages of specified quantity'''

    #-----------------------------
    # Initialize output dictionary
    #-----------------------------
    outdata = {}
    dataAvg = []
    cnt     = []
    std     = []
    dtavg      = []

    #-----------------------------------------
    # Convert date time input to strictly date
    #-----------------------------------------
    dates_daily = np.asarray([dt.date(d.year,d.month,d.day) for d in dates])
    hours_daily = np.asarray([d.hour for d in dates])

    #-----------------------------
    # Ensure data is a numpy array
    #-----------------------------
    data = np.asarray(data)
    #--------------------------------------
    # Create a list of days to loop through
    #--------------------------------------
    #i_date = dt.date(2013, 06, 01)
    #f_date = dt.date(2013, 07, 10)

    i_date = idate
    f_date = fdate

    numDays = (f_date + dt.timedelta(days=1) - i_date).days
    datelist =[i_date + dt.timedelta(days=i) for i in range(0, numDays, 1)]   # Incremental day list from initial to final day

    datelist = list(set(datelist))     
    datelist.sort()
    datelist = np.asarray(datelist)    

    #-------------------------
    # Define hours
    #-------------------------
    ho = range(0, 24, 1)#(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,21,23,24)
    nho = len(ho)-1
    #-------------------------
    # Loop through unique days
    #-------------------------
    for indDay in datelist:

        for h in range(nho):

            inds = np.where( (dates_daily == indDay) & (hours_daily >= ho[h]) & (hours_daily < ho[h+1]) ) [0]                                   # Index for values to use as daily average
       
            if data.ndim == 1:                                                              # For single dimension array   
                if quad == 1: dataAvg.append( np.sqrt(np.sum(data[inds]**2)) / len(inds) )  # Find daily average (sqrt(sum(x^2))/N)
                else:         dataAvg.append( np.mean(data[inds]) )                         # Find daily average (straight mean)
                std.append(np.std(data[inds]))                                              # Find standard deviation
     
            else:                                                                           # For multi-Dimension array
                s           = [slice(None)] * data.ndim
                s[dateAxis] = inds
                tempMat     = data[s]
                if quad == 1: dataAvg.append( np.sqrt(np.sum(tempMat,axis=meanAxis) / len(inds)))
                else:         dataAvg.append( np.mean(tempMat,axis=meanAxis) )
                std.append(np.std(tempMat,axis=meanAxis))                                  # Find standard deviation
        
            cnt.append(len(inds))                                                         # Number of observations used in daily average
            dtavg.append(dt.datetime(indDay.year, indDay.month, indDay.day, ho[h], 30, 0 ) )

    cnt     = np.asarray(cnt)
    dataAvg = np.asarray(dataAvg)
    std     = np.asarray(std)
    dtavg   = np.asarray(dtavg)

    outdata['avg']         = dataAvg
    outdata['dtavg']       = dtavg
    outdata['cnt']         = cnt
    outdata['std']         = std

    return dataAvg, std, dtavg, cnt

def groupAvg(data, dates, dateAxis=1, meanAxis=0, quad=0):
    '''   '''

    #-----------------------------
    # Initialize output dictionary
    #-----------------------------
    outdata = {}
    dataAvg = []
    cnt     = []
    std     = []
    dh      = []

    #-----------------------------------------
    # Convert date time input to strictly date
    #-----------------------------------------
    dates_daily = np.asarray([dt.date(d.year,d.month,d.day) for d in dates])
    hours_daily = np.asarray([d.hour for d in dates])
    exit()
    #-----------------------------
    # Ensure data is a numpy array
    #-----------------------------
    data = np.asarray(data)

    #--------------------------------------
    # Create a list of days to loop through
    #--------------------------------------
    uniqueDays = list(set(dates_daily))          # Find a list of unique days
    uniqueDays.sort()
    uniqueDays = np.asarray(uniqueDays)    

    #-------------------------
    # Define hours
    #-------------------------
    ho = (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,21,23,24)
    nho = len(ho)-1
    #-------------------------
    # Loop through unique days
    #-------------------------
    for indDay in uniqueDays:

        for h in range(nho):

            inds = np.where( (dates_daily == indDay) & (hours_daily >= ho[h]) & (hours_daily < ho[h+1]) ) [0]                                   # Index for values to use as daily average
       
            if data.ndim == 1:                                                              # For single dimension array   
                if quad == 1: dataAvg.append( np.sqrt(np.sum(data[inds]**2)) / len(inds) )  # Find daily average (sqrt(sum(x^2))/N)
                else:         dataAvg.append( np.mean(data[inds]) )                         # Find daily average (straight mean)
                std.append(np.std(data[inds]))                                              # Find standard deviation
     
            else:                                                                           # For multi-Dimension array
                s           = [slice(None)] * data.ndim
                s[dateAxis] = inds
                tempMat     = data[s]
                if quad == 1: dataAvg.append( np.sqrt(np.sum(tempMat,axis=meanAxis) / len(inds)))
                else:         dataAvg.append( np.mean(tempMat,axis=meanAxis) )
                std.append(np.std(tempMat,axis=meanAxis))                                  # Find standard deviation
        
            cnt.append(len(inds))                                                         # Number of observations used in daily average
            dh.append(dt.datetime(indDay.year, indDay.month, indDay.day, ho[h], 30, 0 ) )

    cnt     = np.asarray(cnt)
    dataAvg = np.asarray(dataAvg)
    std     = np.asarray(std)
    dh      = np.asarray(dh)

    outdata['avg']      = dataAvg
    outdata['dt']       = dh
    outdata['cnt']      = cnt
    outdata['std']      = std

    return dataAvg, std, dh, cnt

#------------------------------------------------------------------------------------------------------------------------------    
class _DateRange(object):
    '''
    This is an extension of the datetime module.
    Adds functionality to create a list of days.
    '''
    def __init__(self,iyear,imnth,iday,fyear,fmnth,fday, incr=1):
        self.i_date   = dt.date(iyear,imnth,iday)                                                     # Initial Day
        self.f_date   = dt.date(fyear,fmnth,fday)                                                     # Final Day
        self.dateList =[self.i_date + dt.timedelta(days=i) for i in range(0, self.numDays(), incr)]   # Incremental day list from initial to final day

    def numDays(self):
        '''Counts the number of days between start date and end date'''
        return (self.f_date + dt.timedelta(days=1) - self.i_date).days

    def inRange(self,crntyear,crntmonth,crntday):
        '''Determines if a specified date is within the date ranged initialized'''
        crntdate = dt.date(crntyear,crntmonth,crntday)
        if self.i_date <= crntdate <= self.f_date:
            return True
        else:
            return False

    def nearestDate(self, year, month, day=1, daysList=False):
        ''' Finds the nearest date from a list of days based on a given year, month, and day'''
        testDate = dt.date(year, month, day)
        if not daysList:
            daysList = self.dateList
        return min( daysList, key=lambda x:abs(x-testDate) )

    def yearList(self):
        ''' Gives a list of unique years within DateRange '''
        years = [ singDate.year for singDate in self.dateList]               # Find years for all date entries
        years = list(set(years))                                             # Determine all unique years
        years.sort()
        return years

    def daysInYear(self,year):
        ''' Returns an ordered list of days from DateRange within a specified year '''
        if isinstance(year,int):
            newyears = [inYear for inYear in self.dateList if inYear.year == year]
            return newyears
        else:
            print 'Error!! Year must be type int for daysInYear'
            return False



class readoutdata(_DateRange):
    '''  Class for reading data  '''    
    
    def __init__(self, dataDir, groups, versions, vaplts, outFname='', saveFlg= False):

        #------------------------------------------------------------
        # If outFname is specified, plots will be saved to this file,
        # otherwise plots will be displayed to screen
        #------------------------------------------------------------
        if saveFlg: self.pdfsav = PdfPages(outFname)
        else:       self.pdfsav = False

        #-----------------------------------------------------------
        #Declare self
        #-----------------------------------------------------------
        self.data   = {}
        self.ver    = []
        self.group  = []

        #https://docs.python.org/2/library/stdtypes.html

        for i, group in enumerate(groups):

            self.data[group] = {}

            for v, version in enumerate(versions):
                
               
                if group == 'BOU' or group == 'BRE':
                    filename = dataDir + group+'/'+ group + '_D' + version + '_L.txt'
                else:
                    filename = dataDir +group+'/'+group + '_D' + version + '.txt'
        
                ckFile(filename, exitFlg=True)
                self.data[group][version] = { }#.setdefault(version,[]).append(version)
                self.ver.append( version)
                self.group.append( group )
                self.data[group][version].setdefault('groupname',[]).append( getgroupname(group))

            #------------------------
            # Open file and read data
            #------------------------
                with open(filename,'r') as fname:
                    try:
                        data = fname.readlines()
                    except:
                        print 'Error in reading file: %s' % filename
                        sys.exit()   
                
                #--------------------
                # Remove white spaces
                #--------------------
                data[:] = [ row.strip().split(',') for row in data ]              

                #---------------------------------
                # Determine number of observations
                #---------------------------------
                npoints =  len(data)
                #------------------
                # Update dictionary
                #------------------
                #self.data = {'doy':[]}

                self.data[group][version].setdefault('doy',[]).append( [float(row[0].split()[0]) for row in data] )
                self.data[group][version].setdefault('tod',[]).append( [float(row[0].split()[1]) for row in data])
                self.data[group][version].setdefault('itime',[]).append([float(row[0].split()[2]) for row in data])
                self.data[group][version].setdefault('sza',[]).append([float(row[0].split()[3]) for row in data])
                self.data[group][version].setdefault('saa',[]).append([float(row[0].split()[4]) for row in data])
                self.data[group][version].setdefault('ea',[]).append([float(row[0].split()[5]) for row in data])
                self.data[group][version].setdefault('va',[]).append([float(row[0].split()[6]) for row in data])
                self.data[group][version].setdefault('chocho',[]).append([float(row[0].split()[7]) for row in data])
                self.data[group][version].setdefault('chocho_e',[]).append([float(row[0].split()[8]) for row in data])
                self.data[group][version].setdefault('no2',[]).append([float(row[0].split()[9]) for row in data])
                self.data[group][version].setdefault('no2_e',[]).append([float(row[0].split()[10]) for row in data])
                self.data[group][version].setdefault('o4',[]).append([float(row[0].split()[11]) for row in data])
                self.data[group][version].setdefault('o4_e',[]).append([float(row[0].split()[12]) for row in data])
                self.data[group][version].setdefault('ri',[]).append([float(row[0].split()[13]) for row in data])
                self.data[group][version].setdefault('ci',[]).append([float(row[0].split()[14]) for row in data])
                self.data[group][version].setdefault('rms',[]).append([float(row[0].split()[15]) for row in data])
                self.data[group][version].setdefault('no2_cold',[]).append([float(row[0].split()[16]) for row in data])
                self.data[group][version].setdefault('no2_cold_e',[]).append([float(row[0].split()[17]) for row in data])
                self.data[group][version].setdefault('ring',[]).append([float(row[0].split()[18]) for row in data])
                self.data[group][version].setdefault('ring_e',[]).append([float(row[0].split()[19]) for row in data])
                self.data[group][version].setdefault('offset',[]).append([float(row[0].split()[20]) for row in data])
                self.data[group][version].setdefault('h2o',[]).append([float(row[0].split()[21]) for row in data])
                self.data[group][version].setdefault('h2o_e',[]).append([float(row[0].split()[22]) for row in data])
                self.data[group][version].setdefault('o3',[]).append([float(row[0].split()[23]) for row in data])
                self.data[group][version].setdefault('o3_e',[]).append([float(row[0].split()[24]) for row in data])

                #-----------------------------------------------------------
                #fractional day to julian day
                #-----------------------------------------------------------
                for k, doy in enumerate(self.data[group][version]['doy']):
                    doy_w =  np.asarray(doy)
                    ft_w = np.asarray(self.data[group][version]['tod'][k])            

                    if (group == 'BOU') or (group == 'MOH') or (group == 'IAP'):

                        self.data[group][version].setdefault( 'DT',[] ).append( doytodate(doy_w-1, ft_w, iyear = 2013))
                    else:

                        self.data[group][version].setdefault( 'DT',[] ).append( doytodate(doy_w, ft_w, iyear = 2013))

                self.data[group][version].setdefault('vaplt',[]).append( getgroupname(vaplts[i]))



    def closeFig(self):
        self.pdfsav.close()

    def fltrData(self, maxrms=0.001,minsza=0.0, maxsza=90.0, maxOff=5, vaplt=51,
                rmsFlg=False, szaFlg=False, ofFlg=False, LDFlg=False, VAFlg=False):

        #--------------------------------
        # Filtering has not yet been done
        #--------------------------------
        #self.inds       = []
        self.inds        = {}
        #self.nobsVA     = []
        #self.nobsVARMS  = []
        #self.nobsVADL   = []

        listver =  list(set(self.ver))
        listver.sort()
        listgroup = list(set(self.group))
        listgroup.sort()

        #keydict = dict(zip(vaplt, set(self.group)))
        #print vaplt.sort(key=dict(zip(vaplt, set(self.ver)).get))

        for ver in listver:

            self.data[ver] = {}

            for i, group in enumerate(listgroup):

                indsall = []
                indsallVA = []

                VAplt = self.data[group][ver]['vaplt'][0]
                #------------
                # Filter Data
                #------------
                nobs = len(np.asarray(self.data[group][ver]['doy'][0]))
                print '\ngroup: %s and version %s' % (group, ver)
                print 'Number of total observations before filtering = {}'.format(nobs)
        
                #-----------------------------
                # Standard VA
                #-------- ---------------------                
                if VAFlg:
                    
                    indVA =  np.where(np.asarray(self.data[group][ver]['va'][0]) == VAplt)[0]
                    print ('Total number observations at the standard VA = {}'.format(len(indVA)))
                    self.data[group][ver].setdefault('nobs',[]).append(len(indVA))
                    self.data[ver].setdefault('nobsVA',[]).append(len(indVA))


                #-----------------------------
                # Find flag RMS
                #-----------------------------                
                if rmsFlg:
                    indsT =  np.where(np.asarray(self.data[group][ver]['rms'][0]) >= maxrms)[0]
                    print ('Total number observations found with high RMS = {}'.format(len(indsT)))
                    indsall = np.union1d(indsT, indsall)

                    indrmsva = []
                
                    for dd, DL in enumerate(self.data[group][ver]['rms'][0]):
                
                        if (np.asarray(self.data[group][ver]['rms'][0][dd]) >= maxrms) & (np.asarray(self.data[group][ver]['va'][0][dd]) == VAplt):
                            indrmsva.append(dd)
                        #self.nobsVARMS.append(len(indrmsva))
                    
                    self.data[ver].setdefault('nobsVARMS',[]).append(len(indrmsva))
                         
                    print ('Total number observations found with high RMS at the std VA = {}'.format(len(indrmsva)))

                #-----------------------------
                # Find flag SZA
                #-----------------------------                
                if szaFlg:
                    indsT =  np.where(np.asarray(self.data[group][ver]['sza'][0]) >= maxsza)[0]
                    print ('Total number observations found with high SZA = {}'.format(len(indsT)))
                    indsall = np.union1d(indsT, indsall)
                
                    indsT =  np.where(np.asarray(self.data[group][ver]['sza'][0]) <= minsza)[0]
                    print ('Total number observations found with low SZA = {}'.format(len(indsT)))
                    indsall = np.union1d(indsT, indsall)
                
                #-----------------------------
                # Find flag offset
                #-----------------------------                
                if ofFlg:
                    indsT =  np.where(np.asarray(self.data[group][ver]['offset'][0]) >= maxOff)[0]
                    print ('Total number observations found with high offset = {}'.format(len(indsT)))
                    indsall = np.union1d(indsT, indsall)
            
                #-----------------------------
                # Find flag detection limit
                #-----------------------------                
                if LDFlg:
                    rms = np.asarray(self.data[group][ver]['rms'][0])
                    DLchocho = detectionlimit(rms)/1e15
                 
                    inddl = []
                    for dd, DL in enumerate(DLchocho):
                        if np.asarray(self.data[group][ver]['chocho'][0][dd]) <= DL:
                            inddl.append(dd)
                          
                        #indsT =  np.where(np.asarray(self.data[i]['chocho']) <= mindscd)[0]
                    print ('Total number observations below the detection limit = {}'.format(len(inddl)))
                    indsall = np.union1d(inddl, indsall)

                    inddlva = []
                    for dd, DL in enumerate(DLchocho):
                        if (np.asarray(self.data[group][ver]['chocho'][0][dd]) <= DL) & (np.asarray(self.data[group][ver]['va'][0][dd]) ==VAplt):
                            inddlva.append(dd)
                    #self.nobsVADL.append(len(inddlva))
                    self.data[ver].setdefault('nobsVADL',[]).append(len(inddlva))
                             
                    print ('Total number observations below the detection limit at the std VA = {}'.format(len(inddlva)))

                #-----------------------------
                # VA flag
                #-----------------------------                
                if VAFlg:
                    indsT =  np.where(np.asarray(self.data[group][ver]['va'][0]) != VAplt)[0]
                    print ('Total number observations found with different VA = {}'.format(len(indsT)))
                    indsall = np.union1d(indsT, indsall)

                #self.inds.append(indsall)
                self.data[group][ver].setdefault('inds',[]).append(indsall)
                self.data[group][ver].setdefault('nobsVA',[]).append(len(indVA))
                if rmsFlg: self.data[group][ver].setdefault('nobsVARMS',[]).append(len(indrmsva))
                if LDFlg:  self.data[group][ver].setdefault('nobsVADL',[]).append(len(inddlva))

                del(indsall)
                del(indsT)


    def pltvcorr(self, fltr=False, maxrms=0.001, minsza=0.0, maxsza=90.0, maxOff=5, vaplt=51,
             rmsFlg=False, szaFlg=False, ofFlg=False, LDFlg=False, VAFlg=False, verxplt='' ):

        print '\nPrinting Correlation plot of different version..........\n'
        #--------------------
        # Call to filter data
        #--------------------

        listver =  list(set(self.ver))
        listver.sort()

        if len(listver) > 1:
            print 'There are %s versions' %str(len(listver))
 
            listgroup = list(set(self.group))
            listgroup.sort()

            xver    = verxplt
            listver.remove(xver)

        
            if fltr: self.fltrData(maxrms=maxrms,minsza=minsza,maxsza=maxsza,maxOff=maxOff, vaplt=vaplt,
                                        rmsFlg=rmsFlg, szaFlg=szaFlg, ofFlg=ofFlg, LDFlg=LDFlg, VAFlg=VAFlg)     
            else: self.inds = np.array([])

            clmap        = 'jet'
            cm           = plt.get_cmap(clmap) 
            norm = colors.Normalize( vmin=1, vmax=20 )

            fig, axs = plt.subplots(len(listver), len(listgroup), figsize=(16,10), sharex=True, sharey=True)
            #fig, axs = plt.subplots(len(listgroup), figsize=(10,10), sharex=True)

            for g, group in enumerate(listgroup):

                #---------------------------------
                # Remove data based on filter inds
                #---------------------------------

                if fltr: index = self.data[group][xver]['inds'][0]
                else:    index = []
            
                ea_flt       = np.delete(self.data[group][xver]['ea'][0], index)
                va_flt       = np.delete(self.data[group][xver]['va'][0], index)
                doy_flt      = np.delete(self.data[group][xver]['doy'][0], index)
                chocho_flt   = np.delete(self.data[group][xver]['chocho'][0], index)
                chocho_e_flt = np.delete(self.data[group][xver]['chocho_e'][0], index)
                datet_flt    = np.delete(self.data[group][xver]['DT'][0],index)

                inds  = np.where( (np.array(ea_flt) >= 1) & (np.array(ea_flt) <= 20))[0]
                #inds  = np.where(np.array(ea_flt) == 3)[0]
                chocho_fix_w = np.asarray(chocho_flt[inds])
                dt_fix_w =  np.array(datet_flt[inds])
              
                ea_fix_w = np.asarray(ea_flt[inds])
                doy_fix_w = toYearFraction(dt_fix_w)  

                
                for v, ver in enumerate(listver):

                    #---------------------------------
                    # Remove data based on filter inds
                    #---------------------------------
                    ea_flt       = np.delete(self.data[group][ver]['ea'][0], self.data[group][ver]['inds'][0])
                    va_flt       = np.delete(self.data[group][ver]['va'][0], self.data[group][ver]['inds'][0])
                    doy_flt      = np.delete(self.data[group][ver]['doy'][0], self.data[group][ver]['inds'][0])
                    chocho_flt   = np.delete(self.data[group][ver]['chocho'][0], self.data[group][ver]['inds'][0])
                    chocho_e_flt = np.delete(self.data[group][ver]['chocho_e'][0], self.data[group][ver]['inds'][0])
                    datet_flt    = np.delete(self.data[group][ver]['DT'][0], self.data[group][ver]['inds'][0])

                    groupname = str(self.data[group][ver]['groupname'][0])

                    inds  = np.where( (np.array(ea_flt) >= 1) & (np.array(ea_flt) < 90))[0]
                    chocho_w = np.asarray(chocho_flt[inds])
                    dt_w =  np.asarray(datet_flt[inds])
                    ea_w = np.asarray(ea_flt[inds])
                    doy_w = toYearFraction(dt_w)       

                    len1 = len(dt_fix_w)
                    len2 = len(dt_w)

                    #------------------------------------
                    #IN case the days are not unique
                    #------------------------------------ 
                    doy_fix_w, indices= np.unique(doy_fix_w, return_index=True)
                    chocho_fix_w = chocho_fix_w[indices]

                    doy_w, indices= np.unique(doy_w, return_index=True)
                    chocho_w = chocho_w[indices]

                    #------------------------------------
                    #FInding the same datetime of measurements in diff versions
                    #------------------------------------ 

                    intrsctVals = np.intersect1d(doy_w, doy_fix_w, assume_unique=False)
                 
                    inds1       = np.nonzero( np.in1d( doy_fix_w, intrsctVals, assume_unique=False ) )[0]
                    inds2       = np.nonzero( np.in1d( doy_w, intrsctVals, assume_unique=False ) )[0]

                    chocho_2 = chocho_w[inds2]
                    chocho_1 = chocho_fix_w[inds1]

                    EAsf = ea_w[inds2]

                    #------------------------------------
                    #PLot
                    #------------------------------------
                    o2o = np.array([-1, 10, 0.5]) 

                    # Fit line using all data
                    slope, intercept, r_value, p_value, std_err = stats.linregress(chocho_1, chocho_2)
            
                    #axs[v, g].scatter(chocho_1, chocho_2)
                    sc = axs[v, g].scatter(chocho_1,chocho_2, c=EAsf,cmap=cm,norm=norm)
                    axs[v, g].plot(o2o, o2o, '--', color='gray')
                    axs[v, g].plot(o2o, o2o*0.8, '--', color='gray')
                    axs[v, g].plot(o2o*0.8, o2o, '--', color='gray')
                    axs[v, g].grid(True, which='both')
                    axs[v, g].set_title('setting '+ver[1] +' - '+groupname, fontsize = 14)
                    axs[v, g].set_ylim(-0.025, 7)
                    axs[v, g].set_xlim(-0.025, 7)
                    axs[v, g].tick_params(axis='both',which='both',labelsize=14)
                    axs[v, g].text(0.95, 0.05, "slope={0:.2f}\nintercept={1:.2f}\nr$^2$={2:.2f}".format(slope, intercept, r_value**2),
                    verticalalignment='bottom', horizontalalignment='right', transform=axs[v, g].transAxes)

                    fig.text(0.04, 0.5, 'dSCD [x10$^{15}$ molecules$\cdot$cm$^{-2}$]', fontsize = 16, horizontalalignment='right',
                    verticalalignment='center', rotation='vertical')#, transform=ax[k].transAxes)

                    fig.text(0.5, 0.02, 'dSCD [x10$^{15}$ molecules$\cdot$cm$^{-2}$] - setting '+verxplt[1], fontsize = 16, horizontalalignment='center',
                    verticalalignment='center', rotation='horizontal')#, transform=ax[k].transAxes)
                    
                    cax  = fig.add_axes([0.2, 0.96, 0.6, 0.025])
                    cbar = fig.colorbar(sc, cax=cax, orientation='horizontal')
                    cbar.set_label('EA', fontsize=14) 

                    #axs[v, g].set_ylabel(r'CHOCHO dSCD [x10$^{15}$ molecules$\cdot$cm$^{-2}$]',multialignment='center', fontsize=14)
                    #axs[v, g].set_xlabel(r'CHOCHO dSCD [x10$^{15}$ molecules$\cdot$cm$^{-2}$]',multialignment='center', fontsize=14)
                    

            plt.subplots_adjust(left=0.06, right=0.95, top=0.89, bottom=0.06)

            if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
            else:           plt.show(block=False)


    def pltsig(self, fltr=False, maxrms=0.001, minsza=0.0, maxsza=90.0, maxOff=5, vaplt=51,
             rmsFlg=False, szaFlg=False, ofFlg=False, LDFlg=False, VAFlg=False ):

        print '\nPrinting Correlation plot of different version..........\n'
        #--------------------
        # Call to filter data
        #--------------------

        listver =  list(set(self.ver))
        listver.sort()

        clr = clrplt()

        if len(listver) > 1:
            print 'There are %s versions' %str(len(listver))
 
            listgroup = list(set(self.group))
            listgroup.sort()
        
            if fltr:
                self.fltrData(maxrms=maxrms,minsza=minsza,maxsza=maxsza,maxOff=maxOff, vaplt=vaplt,
                                        rmsFlg=rmsFlg, szaFlg=szaFlg, ofFlg=ofFlg, LDFlg=LDFlg, VAFlg=VAFlg)     

                N = len(self.data['V1']['nobsVA'])
                
                ind = np.arange(N)  

                rmsObs = []
                dlObs  = []
               
                for v, ver in enumerate(listver):
                
                    if rmsFlg: rmsObs.append(np.true_divide(np.array(self.data[ver]['nobsVARMS'][:]), np.array(self.data[ver]['nobsVA'][:])) * 100. )
                    if LDFlg:  dlObs.append(np.true_divide(np.array(self.data[ver]['nobsVADL'][:]), np.array(self.data[ver]['nobsVA'][:])) * 100. )

                rmsObs = np.asarray(rmsObs)
                dlObs = np.asarray(dlObs)

                width = 0.2

                if LDFlg:
                
                    #BELOW DETECTION LIMIT
                    fig, ax = plt.subplots(figsize=(9,6))

                    if 'V1' in self.data: b1 = ax.bar(ind, dlObs[0], width, color=clr[0], align='center', label='Setting 1')
                    if 'V2' in self.data: b2 = ax.bar(ind + width, dlObs[1], width, color=clr[1], align='center', label='Setting 2')
                    if 'V3' in self.data: b3 = ax.bar(ind + width*2.0, dlObs[2], width, color=clr[2], align='center', label='Setting 3')
                    if 'V4' in self.data: b4 = ax.bar(ind + width*3.0, dlObs[3], width, color=clr[3], align='center', label='Setting 4')
                
                    ax.set_ylabel('$\%$ of data below DL')
                    ax.set_xticks(ind + width*2.0)
                    xTickMarks = [getgroupname(x) for x in listgroup]
                    xtickNames = ax.set_xticklabels(xTickMarks)

                    plt.legend(prop={'size':12}, loc='upper left')
                    plt.setp(xtickNames, rotation=45, fontsize=10)

                    ax.set_ylim(0, 100)
                    ax.set_xlim(-width*2.0,len(ind))

                    listgroup2 = [getgroupname(x) for x in listgroup]
                    
                    ax.set_xticklabels(listgroup2, rotation=40,  multialignment='left')
                    ax.tick_params(axis='both',which='both',labelsize=14)
                    ax.tick_params(axis=u'x', which=u'both',length=0)

                    plt.subplots_adjust(left=0.1, right=0.93, top=0.94, bottom=0.15)

                if rmsFlg:

                    #ABOVE MAX RMS
                    fig2, ax = plt.subplots(figsize=(9,6))

                    if 'V1' in self.data: b1 = ax.bar(ind, rmsObs[0], width, color=clr[0], align='center', label='Setting 1')
                    if 'V2' in self.data: b2 = ax.bar(ind + width, rmsObs[1], width, color=clr[1], align='center', label='Setting 2')
                    if 'V3' in self.data: b3 = ax.bar(ind + width*2.0, rmsObs[2], width, color=clr[2], align='center', label='Setting 3')
                    if 'V4' in self.data: b4 = ax.bar(ind + width*3.0, rmsObs[3], width, color=clr[3], align='center', label='Setting 4')
                
                    ax.set_ylabel('$\%$ of data above max RMS')
                    ax.set_xticks(ind + width*2.0)
                    xTickMarks = [getgroupname(x) for x in listgroup]
                    xtickNames = ax.set_xticklabels(xTickMarks)

                    plt.legend(prop={'size':12}, loc='upper left')
                    plt.setp(xtickNames, rotation=45, fontsize=10)

                    ax.set_ylim(0, 100)
                    ax.set_xlim(-width*2.0,len(ind))

                    listgroup2 = [getgroupname(x) for x in listgroup]
                    
                    ax.set_xticklabels(listgroup2, rotation=40,  multialignment='left')
                    ax.tick_params(axis='both',which='both',labelsize=14)
                    ax.tick_params(axis=u'x', which=u'both',length=0)

                    plt.subplots_adjust(left=0.1, right=0.93, top=0.94, bottom=0.15)

                #for i, rect in enumerate(b3):
                #    ax.text(rect.get_x() + rect.get_width()*1.0, rect.get_height() +  rect.get_height()*0.05, 'N = %d' %int(self.data[ver2plt]['nobsVA'][i]), ha='center', va='bottom')
            
            if self.pdfsav: 
                if LDFlg:  self.pdfsav.savefig(fig,dpi=200)
                if rmsFlg: self.pdfsav.savefig(fig2,dpi=200)
            else:           plt.show(block=False) 
  
        else: 
            'Filter flag is False'
            exit()
               
            
         
    def pltts(self, easplt, fltr=False, maxrms=0.001, minsza=0.0, maxsza=90.0, maxOff=5, vaplt=51,
             rmsFlg=False, szaFlg=False, ofFlg=False, LDFlg=False, VAFlg=False, title='', ver2plt=''):

        print '\nPrinting plots..........\n'
        
        clr = clrplt()

        listgroup = list(set(self.group))
        listgroup.sort()

        DateFmt  = DateFormatter('%d/%m')
    
        #--------------------
        # Call to filter data
        #--------------------

        if fltr: self.fltrData(maxrms=maxrms,minsza=minsza,maxsza=maxsza,maxOff=maxOff, vaplt=vaplt,
                                              rmsFlg=rmsFlg, szaFlg=szaFlg, ofFlg=ofFlg, LDFlg=LDFlg, VAFlg=VAFlg)     
        else: self.inds = np.array([])

        neas =  len(easplt)

        fig, axs = plt.subplots(neas, figsize=(10,10), sharex=True)
    
        for i, group in enumerate(listgroup):

            #---------------------------------
            # Remove data based on filter inds
            #---------------------------------

            if fltr: index = self.data[group][ver2plt]['inds'][0]
            else:    index = []

            ea_flt       = np.delete(self.data[group][ver2plt]['ea'][0], index)
            va_flt       = np.delete(self.data[group][ver2plt]['va'][0], index)
            doy_flt      = np.delete(self.data[group][ver2plt]['doy'][0], index)
            chocho_flt   = np.delete(self.data[group][ver2plt]['chocho'][0], index)
            chocho_e_flt = np.delete(self.data[group][ver2plt]['chocho_e'][0], index)
            datet_flt    = np.delete(self.data[group][ver2plt]['DT'][0],index)

            for n, nea in enumerate(easplt):
                #---------------------------------
                inds  = np.where(np.array(ea_flt) == nea)[0]
                chocho_w = np.asarray(chocho_flt[inds])
                dt_w =  np.asarray(datet_flt[inds])
                ea_w = np.asarray(ea_flt[inds])

                namegroup = getgroupname(group)
               
                axs[n].scatter(dt_w,chocho_w, edgecolor=clr[i], label=namegroup, color='white')
                axs[n].grid(True, which='both')
                axs[n].set_ylim(-0.25, 6)
                axs[n].set_title('EA = %s'% nea)
                axs[n].xaxis.set_major_formatter(DateFmt)
                axs[n].tick_params(axis='both',which='both',labelsize=12)
                axs[n].set_xlim( dt.date(2013,6,4), dt.date(2013,8,3)  )

               # if n != neas-1: axs[n].set_xticklabels([])
                if n == neas/2: axs[n].set_ylabel(r'CHOCHO dSCD [x10$^{15}$ molecules$\cdot$cm$^{-2}$]',multialignment='center', fontsize=14)
                if n == neas-1: axs[n].set_xlabel('Date in %s'% '2013', multialignment='center', fontsize=14)
                if n == 0: axs[n].legend(prop={'size':11}, loc='upper center', bbox_to_anchor=(0., 1.32, 1., .1), ncol=int(len(listgroup)))
        
        fig.suptitle(title, fontsize=16)
        #plt.subplots_adjust(left=0.08, right=0.95, top=0.95, bottom=0.05)
        plt.subplots_adjust(left=0.08, right=0.95, top=0.9, bottom=0.05)


        if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
        else:           plt.show(block=False)    

       #--------------------------------
       #Bar plot with statistics
       #--------------------------------
        # N = len(self.data[ver2plt]['nobsVA'])
       
        # #self.nobsVA
        # if rmsFlg: rmsObs = np.true_divide(np.array(self.data[ver2plt]['nobsVARMS'][:]), np.array(self.data[ver2plt]['nobsVA'][:])) * 100.
        # if LDFlg: dlObs  = np.true_divide(np.array(self.data[ver2plt]['nobsVADL'][:]), np.array(self.data[ver2plt]['nobsVA'][:])) * 100.


        # ind = np.arange(N)  # the x locations for the groups
        
        # width = 0.3
        #   # the width of the bars

        # if fltr:

        #     fig, ax = plt.subplots( figsize=(7.5,6) )
        #     if rmsFlg: b2 = ax.bar(ind, rmsObs, width, color='b', align='center')
        #     if LDFlg:  b3 = ax.bar(ind + width, dlObs, width, color='g', align='center')

        #     # add some text for labels, title and axes ticks
        #     ax.set_ylabel('$\%$')
        #     ax.set_xticks(ind + width)
        #     ax.set_ylim(0, 100)
        #     listgroup2 = [getgroupname(x) for x in listgroup]
        #     ax.set_xticklabels(listgroup2, rotation=40,  multialignment='left')
        #     ax.tick_params(axis='both',which='both',labelsize=14)
        #     ax.tick_params(axis=u'x', which=u'both',length=0)

        #     if (rmsFlg) & (LDFlg): ax.legend((b2[0], b3[0]), ('RMS above %s'%maxrms, 'Below 1$\sigma$ detection limit'))

        #     for i, rect in enumerate(b3):
           
        #         ax.text(rect.get_x() + rect.get_width()*1.0, rect.get_height() +  rect.get_height()*0.05, 'N = %d' %int(self.data[ver2plt]['nobsVA'][i]), ha='center', va='bottom')

        #     plt.subplots_adjust(left=0.1, right=0.93, top=0.94, bottom=0.15)

            
        #     if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
        #     else:           plt.show(block=False)


    def plttsdoi(self, easplt, fltr=False, maxrms=0.001, minsza=0.0, maxsza=90.0, maxOff=5, vaplt=51,
             rmsFlg=False, szaFlg=False, ofFlg=False, LDFlg=False, VAFlg=False, dois = 0.0, dtrange=False, title='', ver2plt=''):

        print '\nPrinting plots..........\n'
         
        clr = clrplt()

        listver =  list(set(self.ver))
        listver.sort()

        listgroup = list(set(self.group))
        listgroup.sort()

        if dtrange:
            DateFmt  = DateFormatter('%H')
        else:  
            DateFmt  = DateFormatter('%d/%m')
    
        #--------------------
        # Call to filter data
        #--------------------
        if fltr: self.fltrData(maxrms=maxrms,minsza=minsza,maxsza=maxsza,maxOff=maxOff, vaplt=vaplt,
                               rmsFlg=rmsFlg, szaFlg=szaFlg, ofFlg=ofFlg, LDFlg=LDFlg, VAFlg=VAFlg)     
        else: self.inds = np.array([])

        neas =  len(easplt)
        Ndoi =  len(dois)

        fig, axs = plt.subplots(neas, Ndoi, figsize=(10,10), sharex=False)
        
        for i, group in enumerate(listgroup):

            #---------------------------------
            # Remove data based on filter inds
            #---------------------------------
            if fltr: index = self.data[group][ver2plt]['inds'][0]
            else:    index = []
            
            ea_flt       = np.delete(self.data[group][ver2plt]['ea'][0], index)
            va_flt       = np.delete(self.data[group][ver2plt]['va'][0], index)
            doy_flt      = np.delete(self.data[group][ver2plt]['doy'][0], index)
            chocho_flt   = np.delete(self.data[group][ver2plt]['chocho'][0], index)
            chocho_e_flt = np.delete(self.data[group][ver2plt]['chocho_e'][0], index)
            datet_flt    = np.delete(self.data[group][ver2plt]['DT'][0], index)

            for n, nea in enumerate(easplt):
                #---------------------------------
                inds  = np.where(np.array(ea_flt) == nea)[0]
                chocho_w = np.asarray(chocho_flt[inds])
                dt_w =  np.asarray(datet_flt[inds])
                ea_w = np.asarray(ea_flt[inds])  

                namegroup = getgroupname(group)

                for dd, doi in enumerate(dois):
                   
                    axs[n, dd].scatter(dt_w, chocho_w, edgecolor=clr[i], label=namegroup, color='white')
                    axs[n, dd].grid(True, which='both')
                    axs[n, dd].set_ylim(-0.8, 6)
                    axs[n, dd].set_title('EA = %s'% nea)
                    axs[n, dd].xaxis.set_major_formatter(DateFmt)
                    axs[n, dd].tick_params(axis='both', which='both',labelsize=12)
                    
                    if dtrange:
                        axs[n, dd].set_xlim((dt.datetime(doi.year, doi.month, doi.day, 4, 0), dt.datetime(doi.year, doi.month, doi.day, 20, 0)) )


                    if n != neas-1: axs[n, dd].set_xticklabels([])
                    if n == neas/2: axs[n, dd].set_ylabel(r'CHOCHO dSCD [x10$^{15}$ molecules$\cdot$cm$^{-2}$]',multialignment='center', fontsize=14)
                    if n == neas-1: axs[n, dd].set_xlabel('Hour [UT] ('+str(doi.day)+'/'+str(doi.month)+'/'+str(doi.year)+')', multialignment='center', fontsize=14)
                    #if n == 0: axs[n, dd].scatter(dt_w,chocho_w, edgecolor=clr[i], label=namegroup, color='white')
                
            plt.legend(prop={'size':11}, loc='upper center', bbox_to_anchor=(-0.12, 6.23), ncol=int(len(listgroup)))
        
        fig.suptitle(title, fontsize=16)
        #fig.autofmt_xdate()

        plt.subplots_adjust(left=0.08, right=0.95, top=0.9, bottom=0.05)

        if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
        else:           plt.show(block=False)            



    def plttsdoihcorr(self, easplt, fltr=False, maxrms=0.001, minsza=0.0, maxsza=90.0, maxOff=5, vaplt=51,
             rmsFlg=False, szaFlg=False, ofFlg=False, LDFlg=False, VAFlg=False, dois = 0.0, dtrange=False, title='', ver2plt='', group4mean=[]):

        print '\nPrinting plots..........\n'
        
         
        clr = clrplt()

        listver =  list(set(self.ver))
        listver.sort()

        listgroup = list(set(self.group))
        listgroup.sort()


        if dtrange:
            DateFmt  = DateFormatter('%H')
        else:  
            DateFmt  = DateFormatter('%d/%m')
    
        #--------------------
        # Call to filter data
        #--------------------
        if fltr: self.fltrData(maxrms=maxrms,minsza=minsza,maxsza=maxsza,maxOff=maxOff, vaplt=vaplt,
                               rmsFlg=rmsFlg, szaFlg=szaFlg, ofFlg=ofFlg, LDFlg=LDFlg, VAFlg=VAFlg)

        else: self.inds = np.array([])

        neas =  len(easplt)
        Ndoi =  len(dois)
        

        doi_i = dt.datetime(dois[0].year, dois[0].month, dois[0].day, 0, 0)
        doi_f = dt.datetime(dois[-1].year, dois[-1].month, dois[-1].day, 23, 0)

        doi_doy = toYearFraction([doi_i, doi_f])
        
        fig, axs = plt.subplots(neas, Ndoi, figsize=(10,10), sharex=False)
        fig2, axs2 = plt.subplots(neas, Ndoi, figsize=(10,10), sharex=False)
        fig3, axs3 = plt.subplots(3, figsize=(10,10), sharex=True)

        for n, nea in enumerate(easplt):
            
            chocho_h     = []
            chocho_std_h = []
            cnt_h        = []
            dt_h         = []
            ea_h         = []
            chocho_m_h   = []
            namegroup    = []

            rsquare_g      = []
            slope_g        = []
            intercept_g    = []
            r_g            = []
            xx_g           = []

            for group in listgroup:

                #---------------------------------
                # Remove data based on filter inds
                #---------------------------------

                if fltr: index = self.data[group][ver2plt]['inds'][0]
                else:    index = []
            
                ea_flt       = np.delete(self.data[group][ver2plt]['ea'][0], index)
                va_flt       = np.delete(self.data[group][ver2plt]['va'][0], index)
                doy_flt      = np.delete(self.data[group][ver2plt]['doy'][0], index)
                chocho_flt   = np.delete(self.data[group][ver2plt]['chocho'][0], index)
                chocho_e_flt = np.delete(self.data[group][ver2plt]['chocho_e'][0], index)
                datet_flt    = np.delete(self.data[group][ver2plt]['DT'][0], index)

                doy_flt = toYearFraction(datet_flt)

                inds       =  np.where( (np.array(ea_flt) == nea) & (np.asarray(doy_flt) > doi_doy[0]) & (np.asarray(doy_flt) < doi_doy[-1]))[0]
                chocho_w   =  np.asarray(chocho_flt[inds])
                dt_w       =  np.asarray(datet_flt[inds]) 

                
                dataAvg, std, dt_avg, cnt = hourAvg(chocho_w,dt_w, dois[0], dois[-1], dateAxis=1, meanAxis=0)
    

                chocho_h.append(dataAvg)
                dt_h.append(dt_avg)
                cnt_h.append(cnt)
                chocho_std_h.append(std)
                namegroup.append(getgroupname(group))

                #print group, len(inds), len(dataAvg), len(chocho_h)
                
            chocho_h     = np.asarray(chocho_h)
            dt_h         = np.asarray(dt_h) 
            cnt_h        = np.asarray(cnt_h)
            chocho_std_h = np.asarray(chocho_std_h)
            ea_h         = np.asarray(ea_h)

            intrsctVals = np.intersect1d(listgroup, group4mean, assume_unique=False)
            indsmean    = np.nonzero( np.in1d( listgroup, intrsctVals, assume_unique=False ) )[0]

            chocho_h_g = np.mean(chocho_h[indsmean], axis=0)
            chocho_h_g = np.asarray(chocho_h_g)

            #-------------------------------------
            #
            #------------------------------------
            for dd, doi in enumerate(dois):   

                for i, group in enumerate(listgroup):
                    labelgroup  =  getgroupname(group)
                    axs[n, dd].scatter(dt_h[i],chocho_h[i], edgecolor=clr[i], label=labelgroup, color='white')
                    axs2[n, dd].scatter(dt_h[i],np.true_divide(chocho_h[i]-chocho_h_g, chocho_h_g) *100.0, edgecolor=clr[i], label=labelgroup, color='white')                

                axs[n, dd].scatter(dt_h[0],chocho_h_g, edgecolor='k', color='k')
                axs[n, dd].grid(True, which='both')
                axs[n, dd].set_ylim(-0.8, 6.0)
                axs[n, dd].set_title('EA = %s'% nea)
                axs[n, dd].xaxis.set_major_formatter(DateFmt)
                axs[n, dd].tick_params(axis='both',which='both',labelsize=12)


                axs2[n, dd].grid(True, which='both')
                axs2[n, dd].set_ylim(-100, 100)
                axs2[n, dd].set_title('EA = %s'% nea)
                axs2[n, dd].xaxis.set_major_formatter(DateFmt)
                axs2[n, dd].tick_params(axis='both',which='both',labelsize=12)
                    
                if dtrange:
                    axs[n, dd].set_xlim(dt.datetime(doi.year, doi.month, doi.day, 04, 0), dt.datetime(doi.year, doi.month, doi.day, 20, 0) )
                    axs2[n, dd].set_xlim(dt.datetime(doi.year, doi.month, doi.day, 04, 0), dt.datetime(doi.year, doi.month, doi.day, 20, 0) )

                if n != neas-1:
                    axs[n, dd].set_xticklabels([])
                    axs2[n, dd].set_xticklabels([])
                if n == neas/2: 
                    axs[n, 0].set_ylabel(r'CHOCHO dSCD [x10$^{15}$ molecules$\cdot$cm$^{-2}$]',multialignment='center', fontsize=14)
                    axs2[n, 0].set_ylabel(r'Relative difference [$\%$, (group - mean)/mean]',multialignment='center', fontsize=14)
                if n == neas-1: 
                    axs[n, dd].set_xlabel('Hour [UT] ('+str(doi.day)+'/'+str(doi.month)+'/'+str(doi.year)+')', multialignment='center', fontsize=14)
                    axs2[n, dd].set_xlabel('Hour [UT] ('+str(doi.day)+'/'+str(doi.month)+'/'+str(doi.year)+')', multialignment='center', fontsize=14)
                #if n == 0: 
                    #axs[n, dd].scatter(dt_h[i],chocho_h[i], edgecolor=clr[i], label=labelgroup, color='white')
                    #axs2[n, dd].scatter(dt_h[i],chocho_h[i], edgecolor=clr[i], label=labelgroup, color='white')
                    
                handles, labels = axs[0,0].get_legend_handles_labels()
                handles2, labels2 = axs2[0,0].get_legend_handles_labels()

            fig.legend(handles, labels, prop={'size':12},  bbox_to_anchor=(0.5, 0.965), loc='upper center', ncol=int(len(listgroup)))
            fig2.legend(handles2, labels2, prop={'size':12},  bbox_to_anchor=(0.5, 0.965), loc='upper center', ncol=int(len(listgroup)))
        
            #plt.legend(handles, labels, prop={'size':11}, loc='upper center', bbox_to_anchor=(-0.12, 6.23), ncol=int(len(listgroup)))
            #plt.legend(prop={'size':11}, loc='upper center', bbox_to_anchor=(-0.12, 6.23), ncol=int(len(listgroup)))

            fig.suptitle(title, fontsize=16)
            fig2.suptitle(title, fontsize=16)

            fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.05)
            fig2.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.05)
                

            #-------------------------------------
            #
            #--------------------------------------
            for i, gly in enumerate(chocho_h):

                mask1 = ~np.isnan(chocho_h_g)
                mask2 = ~np.isnan(gly)

                xm = np.ma.masked_array(chocho_h_g,mask=np.isnan(chocho_h_g)).compressed()
                ym = np.ma.masked_array(gly,mask=np.isnan(chocho_h_g)).compressed()

                mask = ~np.isnan(xm) & ~np.isnan(ym)

                if (len(xm[mask]) > 1) & (len(ym[mask]) >1):                    
                    slope, intercept, r_value, p_value, std_err = stats.linregress(xm[mask],ym[mask])
                    slope_g.append(slope)
                    intercept_g.append(intercept)
                    r_g.append(r_value)
                    xx_g.append(i)
                else:
                    slope_g.append(float('nan'))
                    intercept_g.append(float('nan'))
                    r_g.append(float('nan'))
                    xx_g.append(i)


            axs3[0].scatter(xx_g,slope_g, label=str(nea), color=clr[n])           
            axs3[0].grid(True, which='both')
            axs3[0].set_xlim(0, 4)
            axs3[0].set_xlim(-0.5, len(xx_g)-0.5)
            #axs[0].set_title('Slope')
            axs3[0].set_ylabel('Slope')
            axs3[0].tick_params(axis='both',which='both',labelsize=12)

            
            axs3[1].scatter(xx_g,intercept_g, color=clr[n])           
            axs3[1].grid(True, which='both')
            #axs[1].set_title('Intercept')
            axs3[1].set_ylabel('Intercept [x10$^{15}$ molecules$\cdot$cm$^{-2}$]')
            axs3[1].tick_params(axis='both',which='both',labelsize=12)

            axs3[2].scatter(xx_g,r_g, color=clr[n])           
            axs3[2].grid(True, which='both')
            #axs[2].set_title('Coefficient of Correlation (r)')
            axs3[2].set_ylabel('Coefficient of Correlation (r)')
            #axs[2].set_xlabel('Group')
            axs3[2].tick_params(axis='both',which='both',labelsize=12)

        handles, labels = axs3[0].get_legend_handles_labels()

        #plt.legend(handles, labels, prop={'size':12}, loc='upper center', bbox_to_anchor=(0.5, 3.6), ncol=int(neas))
        fig3.legend(handles, labels, prop={'size':12},  bbox_to_anchor=(0.5, 0.96), loc='upper center', ncol=int(neas))
        fig3.suptitle(title, fontsize=16) 
        fig3.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1)     

        my_xticks = namegroup
        plt.xticks(xx_g, my_xticks, rotation=45)


        if self.pdfsav: 
            self.pdfsav.savefig(fig,dpi=200)
            self.pdfsav.savefig(fig2,dpi=200)
            self.pdfsav.savefig(fig3,dpi=200)
        else: plt.show(block=False)  


    def pltraw(self, eaplt, vaplt=51, ver2plt=''):

        print '\nPrinting plots..........\n'

        iyear = 2013
        imnth = 6
        iday  = 12
        fyear = 2013
        fmnth = 8
        fday  = 1

        i_date   = dt.date(iyear,imnth,iday)                                                     # Initial Day
        f_date   = dt.date(fyear,fmnth,fday)                                                     # Final Day
        numDays = (f_date + dt.timedelta(days=1) - i_date).days
        dateList =[i_date + dt.timedelta(days=i) for i in range(0, numDays, 1)] 

        clr = clrplt()

        listver =  list(set(self.ver))
        listver.sort()

        listgroup = list(set(self.group))
        listgroup.sort()
       
        DateFmt  = DateFormatter('%H')   
        #--------------------
        # Call to filter data
        #--------------------
        for d in dateList:
            fig, axs = plt.subplots(3, 2, figsize=(10,8), sharex=True)
            
            for i, group in enumerate(listgroup):
                   
                ea_flt       = np.asarray(self.data[group][ver2plt]['ea'][0])
                va_flt       = np.asarray(self.data[group][ver2plt]['va'][0])
                doy_flt      = np.asarray(self.data[group][ver2plt]['doy'][0])
                rms_flt      = np.asarray(self.data[group][ver2plt]['rms'][0])
                chocho_flt   = np.asarray(self.data[group][ver2plt]['chocho'][0])
                o4_flt       = np.asarray(self.data[group][ver2plt]['o4'][0])
                no2_flt      = np.asarray(self.data[group][ver2plt]['no2'][0])
                ring_flt     = np.asarray(self.data[group][ver2plt]['ring'][0])
                no2c_flt     = np.asarray(self.data[group][ver2plt]['no2_cold'][0])
                h2o_flt      = np.asarray(self.data[group][ver2plt]['h2o'][0])
                datet_flt    = np.asarray(self.data[group][ver2plt]['DT'][0])

                #---------------------------------
                inds  = np.where(np.array(ea_flt) == eaplt)[0]
                chocho = np.asarray(chocho_flt[inds])
                rms = np.asarray(rms_flt[inds])
                o4 = np.asarray(o4_flt[inds])
                no2 = np.asarray(no2_flt[inds])
                no2c = np.asarray(no2c_flt[inds])
                ring = np.asarray(ring_flt[inds])
                h2o = np.asarray(h2o_flt[inds])

                dt_w =  np.asarray(datet_flt[inds])
                ea_w = np.asarray(ea_flt[inds])  

                namegroup = getgroupname(group)
                       
                axs[0, 0].scatter(dt_w, rms, edgecolor=clr[i], label=namegroup, color='white')
                axs[0, 0].set_ylim(0, 0.001)
                axs[0, 0].set_ylabel('RMS')
                
                axs[0, 1].scatter(dt_w, chocho, edgecolor=clr[i],label=namegroup, color='white')
                axs[0, 1].set_ylim(0, 5.5)
                axs[0, 1].set_ylabel('CHOCHO [x10$^{15}$]')
                
                axs[1, 0].scatter(dt_w, o4, edgecolor=clr[i], label=namegroup, color='white')
                axs[1, 0].set_ylim(0, 20000)
                axs[1, 0].set_ylabel('O$_4$ [x10$^{40}$]')
                
                axs[1, 1].scatter(dt_w, no2, edgecolor=clr[i], label=namegroup,  color='white')
                axs[1, 1].set_ylim(0, 400)
                axs[1, 1].set_ylabel('NO$_2$ [x10$^{15}$]')
                

                axs[2, 0].scatter(dt_w, ring, edgecolor=clr[i], label=namegroup, color='white')
                axs[2, 0].set_ylim(-0.045, 0.045)
                axs[2, 0].set_ylabel('Ring')
                axs[2, 0].set_xlabel('UT')

                if group == 'BIR': h2o =  np.empty(len(h2o))

                axs[2, 1].scatter(dt_w, h2o, edgecolor=clr[i], label=namegroup, color='white')
                axs[2, 1].set_ylim(0, 15)
                axs[2, 1].set_ylabel('H$_2$O [x10$^{23}$]')                               
                axs[2, 1].set_xlim((dt.datetime(d.year, d.month, d.day, 4, 0), dt.datetime(d.year, d.month, d.day, 20, 0)) )
                axs[2, 1].set_xlabel('UT')


                for jj in range(3):
                    for pp in range(2):
                        axs[jj, pp].grid(True, which='both')
                        axs[jj, pp].xaxis.set_major_formatter(DateFmt)
                        axs[jj, pp].tick_params(axis='both', which='both',labelsize=12)

                fig.suptitle(d, fontsize=16)
            
            axs[0,0].legend(prop={'size':11}, loc='upper center', bbox_to_anchor=(1, 1.3), ncol=int(len(listgroup)))        
            #plt.legend(prop={'size':11}, loc='upper center', bbox_to_anchor=(0., 0.5, 1., .1), ncol=int(len(listgroup)))
            

            plt.subplots_adjust(left=0.11, right=0.93, top=0.9, bottom=0.075)

            if self.pdfsav: self.pdfsav.savefig(fig)
            else:           plt.show(block=False)

            #plt.cla()
            plt.close()                    


            