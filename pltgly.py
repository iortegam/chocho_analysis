#!/usr/bin/python
##!/home/ivan/miniconda2/bin/python
##!/usr/bin/python
#----------------------------------------------------------------------------------------
# Name:
#      pltgly.py
#
# Purpose:
#      
#
# Input files:
#       Notes:
#      
#        Options include:
#            -i <file> : Flag to specify input file
#            -?        : Show all flags
#
#
# Output files:
#       1)
#
#
# Notes:
#       1)
#
# References:
#
#----------------------------------------------------------------------------------------
                        #-------------------------#
                        # Import Standard modules #
                        #-------------------------#

import logging
import sys
import os
import getopt
import datetime as dt
import glob
import re
import shutil
import classgly as dc
#import matplotlib.pyplot as plt


                        #-------------------------#
                        # Define helper functions #
                        #-------------------------#
def usage():
    ''' Prints to screen standard program usage'''
    print 'plt_chocho.py -i <file>  -?'
    print '  -i <file> : Flag to specify input file for Layer 1 processing. <file> is full path and filename of input file'
    print '  -?        : Show all flags'

def ckDir(dirName,logFlg=False,exit=False):
    ''' '''
    if not os.path.exists( dirName ):
        print 'Input Directory %s does not exist' % (dirName)
        if logFlg: logFlg.error('Directory %s does not exist' % dirName)
        if exit: sys.exit()
        return False
    else:
        return True    

def ckFile(fName,logFlg=False,exit=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print 'File %s does not exist' % (fName)
        if logFlg: logFlg.error('Unable to find file: %s' % fName)
        if exit: sys.exit()
        return False
    else:
        return True

def ckDirMk(dirName,logFlg=False):
    ''' '''
    if not ( os.path.exists(dirName) ):
        os.makedirs( dirName )
        if logFlg: logFlg.info( 'Created folder %s' % dirName)  
        return False
    else:
        return True

                            #----------------------------#
                            #                            #
                            #        --- Main---         #
                            #                            #
                            #----------------------------#

def main(argv):

    #------------------
    # Set default flags
    #------------------
    logFile  = False
    lstFlg   = False
    pauseFlg = False
    #--------------------------------
    # Retrieve command line arguments
    #--------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:?')

    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit()

    #-----------------------------
    # Parse command line arguments
    #-----------------------------
    for opt, arg in opts:
        # Check input file flag and path
        if opt == '-i':

            pltInputs = {}

            ckFile(arg,exit=True)

            try:
                execfile(arg, pltInputs)
            except IOError as errmsg:
                print errmsg + ' : ' + arg
                sys.exit()

            if '__builtins__' in pltInputs:
                del pltInputs['__builtins__']               

        # Show all command line flags
        elif opt == '-?':
            usage()
            sys.exit()

        else:
            print 'Unhandled option: ' + opt
            sys.exit()

    ngroups = len(pltInputs['groups'])
   
    print '\nProcessing data from %s' % str(ngroups) + ' groups:' 
    for group in pltInputs['groups']: print group

    #---------------------------------
    # Check for the existance of files 
    # directories from input file
    #---------------------------------
    ckDir(pltInputs['dataDir'], exit=True)


    gas = dc.readoutdata(pltInputs['dataDir'],pltInputs['groups'], pltInputs['versions'], pltInputs['vaplt'] , outFname=pltInputs['pltFile'], saveFlg= pltInputs['saveFlg'])

    #---------------------------------
    #Plot pltvcorr: Correlation of different setting (version) numbers
    #---------------------------------
    if pltInputs['pltvcorr']:
        gas.pltvcorr(fltr=pltInputs['fltrFlg'],  maxrms= pltInputs['maxRMS'] , minsza=pltInputs['minSZA'],
             maxsza=pltInputs['maxSZA'], maxOff=pltInputs['maxOff'], vaplt=pltInputs['vaplt'], rmsFlg=pltInputs['rmsFlg'], 
             szaFlg=pltInputs['szaFlg'], ofFlg=pltInputs['ofFlg'], LDFlg=pltInputs['LDFlg'], VAFlg=pltInputs['VAFlg'], verxplt=pltInputs['versions'][0])

    #---------------------------------
    #Plot pltsig:
    #---------------------------------
    if pltInputs['pltsig']:
        gas.pltsig(fltr=pltInputs['fltrFlg'],  maxrms= pltInputs['maxRMS'] , minsza=pltInputs['minSZA'],
             maxsza=pltInputs['maxSZA'], maxOff=pltInputs['maxOff'], vaplt=pltInputs['vaplt'], rmsFlg=pltInputs['rmsFlg'], 
             szaFlg=pltInputs['szaFlg'], ofFlg=pltInputs['ofFlg'], LDFlg=pltInputs['LDFlg'], VAFlg=pltInputs['VAFlg'])

    #---------------------------------
    #Plot pltts: Time series of all data set and all groups
    #---------------------------------
    if pltInputs['pltts']:
    	gas.pltts(pltInputs['easplt'], fltr=pltInputs['fltrFlg'], maxrms= pltInputs['maxRMS'] , minsza=pltInputs['minSZA'],
             maxsza=pltInputs['maxSZA'], maxOff=pltInputs['maxOff'], vaplt=pltInputs['vaplt'], rmsFlg=pltInputs['rmsFlg'], 
             szaFlg=pltInputs['szaFlg'], ofFlg=pltInputs['ofFlg'], LDFlg=pltInputs['LDFlg'],
             VAFlg=pltInputs['VAFlg'], title='All data', ver2plt=pltInputs['versions'][0])

    #---------------------------------
    #Plot plttsdoi: Time series of specific dates of interest
    #---------------------------------
    if pltInputs['plttsdoih']:
        gas.plttsdoi(pltInputs['easplt'], fltr=pltInputs['fltrFlg'], maxrms= pltInputs['maxRMS'] , minsza=pltInputs['minSZA'],
                maxsza=pltInputs['maxSZA'], maxOff=pltInputs['maxOff'], vaplt=pltInputs['vaplt'], rmsFlg=pltInputs['rmsFlg'], 
                szaFlg=pltInputs['szaFlg'], ofFlg=pltInputs['ofFlg'], LDFlg=pltInputs['LDFlg'], VAFlg=pltInputs['VAFlg'],
                dois= pltInputs['doi_cs'], dtrange=True, title='Clear sky', ver2plt=pltInputs['versions'][0])

    #---------------------------------
    #Plot plttsdoih: Time series of specific dates of interest (Hourly averages)
    #---------------------------------
    if pltInputs['plttsdoih']:
        gas.plttsdoihcorr(pltInputs['easplt'], fltr=pltInputs['fltrFlg'], maxrms= pltInputs['maxRMS'] , minsza=pltInputs['minSZA'],
        maxsza=pltInputs['maxSZA'], maxOff=pltInputs['maxOff'], vaplt=pltInputs['vaplt'], rmsFlg=pltInputs['rmsFlg'], 
        szaFlg=pltInputs['szaFlg'], ofFlg=pltInputs['ofFlg'], LDFlg=pltInputs['LDFlg'], VAFlg=pltInputs['VAFlg'],
        dois= pltInputs['doi_cs'], dtrange=True, title='Clear sky', ver2plt=pltInputs['versions'][0], group4mean=pltInputs['group4mean'] )

        gas.plttsdoihcorr(pltInputs['easplt'], fltr=pltInputs['fltrFlg'], maxrms= pltInputs['maxRMS'] , minsza=pltInputs['minSZA'],
        maxsza=pltInputs['maxSZA'], maxOff=pltInputs['maxOff'], vaplt=pltInputs['vaplt'], rmsFlg=pltInputs['rmsFlg'], 
        szaFlg=pltInputs['szaFlg'], ofFlg=pltInputs['ofFlg'], LDFlg=pltInputs['LDFlg'], VAFlg=pltInputs['VAFlg'],
        dois= pltInputs['doi_os'], dtrange=True, title='Overcast', ver2plt=pltInputs['versions'][0], group4mean=pltInputs['group4mean'] )

        gas.plttsdoihcorr(pltInputs['easplt'], fltr=pltInputs['fltrFlg'], maxrms= pltInputs['maxRMS'] , minsza=pltInputs['minSZA'],
        maxsza=pltInputs['maxSZA'], maxOff=pltInputs['maxOff'], vaplt=pltInputs['vaplt'], rmsFlg=pltInputs['rmsFlg'], 
        szaFlg=pltInputs['szaFlg'], ofFlg=pltInputs['ofFlg'], LDFlg=pltInputs['LDFlg'], VAFlg=pltInputs['VAFlg'],
        dois= pltInputs['doi_bs'], dtrange=True, title='Broken clouds', ver2plt=pltInputs['versions'][0], group4mean=pltInputs['group4mean'] )


    #---------------------------------
    #Plot pltraw: 
    #---------------------------------
    if pltInputs['pltraw']:
        gas.pltraw(pltInputs['eaplt'], vaplt=pltInputs['vaplt'], ver2plt=pltInputs['versions'][0])


    if pltInputs['saveFlg']: gas.closeFig() 

        #gas.plt1()
    if not pltInputs['saveFlg']:
        user_input = raw_input('Press any key to exit >>> ')
        sys.exit()           # Exit program





if __name__ == "__main__":
    main(sys.argv[1:])