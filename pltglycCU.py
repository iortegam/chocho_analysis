#!/usr/bin/python
##!/home/ivan/miniconda2/bin/python
##!/usr/bin/python
#----------------------------------------------------------------------------------------
# Name:
#      pltglycCU.py
#
# Purpose:
#      plot the results of the amalysis of the CU Boulder SPectra
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
from collections                     import OrderedDict
import classgly as dc
import numpy as np
#import matplotlib.pyplot as plt

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


def findData(group, version, dataDir):
    '''Return the correct data file'''
    
    if group == 'BIR':
        folder = group + '/bira_Cu-Boulder_analysis/'
        if version == 'V1':
            #DirFile = dataDir + folder + 'bira_CU-Boulder_Setting1-VIS434460_CHOCHO_20130718.asc'
            DirFile = dataDir + folder + 'bira_CU-Boulder_Setting1-VIS434460_CHOCHO_20130718_v2.asc'
        if version == 'V3':
            DirFile = dataDir + folder + 'bira_CU-Boulder_Setting3-VIS434460_CHOCHO_20130718.asc'
            #DirFile = dataDir + folder + 'bira_CU-Boulder_Setting3-VIS434460_CHOCHO_20130718_v2.asc'

    elif group == 'BRE':
        #folder = group + '/v8/v8/'
        folder = group + '/v7/v7/'
        if version == 'V1':
            #DirFile = dataDir + folder + 'Boulder_instr_Vis434460_CHOCHO_20130618_v8a.asc'
            DirFile = dataDir + folder + 'Boulder_instr_Vis434460_CHOCHO_20130618_v7a.asc'
        if version == 'V3':
            DirFile = dataDir + folder + 'Boulder_instr_Vis434458_CHOCHO_20130618_v8c.asc'
            #DirFile = dataDir + folder + 'Boulder_instr_Vis434458_CHOCHO_20130618_v8d.asc'

    elif group == 'HEI':
        folder = group+'/'
        
        if version == 'V1':
            DirFile = dataDir + folder + 'CUB_vis434460_glyoxal_noonref_v3_NDSC_20130618_v20160701.asc'
            
        if version == 'V3':
            DirFile = dataDir + folder + 'CUB_vis434460_glyoxal_currentref_v3_NDSC_20130618_v20160701.asc'

    elif group == 'INT':
        folder = group + '/madcatglyoxalforcuboulderspectra/'
        
        if version == 'V1':
            DirFile = dataDir + folder + 'INTA_instrument_setting1_CHOCHO_20130618_v1.asc'
            
        if version == 'V3':
            DirFile = dataDir + folder + 'INTA_instrument_setting3_CHOCHO_20130618_v1.asc'

    elif group == 'INT':
        folder = group + '/madcatglyoxalforcuboulderspectra/'
        
        if version == 'V1':
            DirFile = dataDir + folder + 'INTA_instrument_setting1_CHOCHO_20130618_v1.asc'
            
        if version == 'V3':
            DirFile = dataDir + folder + 'INTA_instrument_setting3_CHOCHO_20130618_v1.asc'
    
    elif group == 'MAI-JR':
        folder = group + '/reglyoxalintercomparison/'
        
        if version == 'V1':
            DirFile = dataDir + folder + 'MPIC_CU-Boulder_Vis1_CHOCHO_20130618_v2.asc'
            #DirFile = dataDir + folder + 'MPIC_CU-Boulder_Vis1_CHOCHO_20130618_v3.asc'
            #DirFile = dataDir + folder + 'MPIC_CU-Boulder_Vis1_CHOCHO_20130618_v11.asc'
            
        if version == 'V3':
            DirFile = dataDir + folder + 'MPIC_CU-Boulder_Vis3_CHOCHO_20130618_v2.asc'
            #DirFile = dataDir + folder + 'MPIC_CU-Boulder_Vis3_CHOCHO_20130618_v3.asc'
            #DirFile = dataDir + folder + 'MPIC_CU-Boulder_Vis3_CHOCHO_20130618_v11.asc'

    elif group == 'MAI-YW':
        folder = group + '/MPIC_YW//submited_results/originalSF&Cali/'
        #folder = 'submited_results/fitted wavelength dependent gaussian SF & fitted Cali/'
        #folder = 'submited_results/shifted SF by 0.0413 & fitted Cali/'
        
        if version == 'V1':
            DirFile = dataDir + folder + 'MPICMDOASyw_CU-Boulder_1#_CHOCHO_20130618_v1.asc'
            
        if version == 'V3':
            DirFile = dataDir + folder + 'MPICMDOASyw_CU-Boulder_3#_CHOCHO_20130618_v1.asc'


    fileName = glob.glob(DirFile)
    
    if not fileName:
        print 'Check filename for %s and version %s' %(group, version)
        sys.exit()

    return DirFile

def getgroupname(group):
    ''' Get the name of the group'''

    if group == 'BIR': groupn = 'BIRA'
    elif group == 'BRE': groupn = 'Bremen'
    elif group == 'BOU': groupn = 'Boulder'
    elif group == 'MAI-YW': groupn = 'MPIC-YW'
    elif group == 'MAI-jr': groupn = 'MPIC-JR'
    elif group == 'HEI': groupn = 'Heidelberg'
    else: groupn = group

    return groupn





                            #----------------------------#
                            #                            #
                            #        --- Main---         #
                            #                            #
                            #----------------------------#

def main():

    #----------------------
    # Importan Inputs
    #----------------------
    groups       = ['BIR', 'BRE', 'HEI', 'INT', 'MAI-JR', 'MAI-YW']                 #Group ID identifier

    #----------------------
    # Importan Inputs for plots
    #----------------------
    version    = 'V1'                                                             #Name of retrieval version to process (v1,v2,v3, or v4)
    easplt      = [1,2,3,5,10]                                                          #EAs for plots

    #----------------------
    #Choose pls to display
    #----------------------
    plt1        = True  

    #----------------------
    # Date range to process
    #----------------------
    doi         = [dt.datetime(2013,06,18, 4, 0), dt.datetime(2013,06,19, 22, 0)]          #days of interest with clear sky

    #----------------------
    #Flag to save Figures in PDF
    #----------------------
    saveFlg    = False   

    #----------------------
    # Directories
    #---------------------- 
    dataDir = '/home/ivan/chocho/data_CU_spectra/'

    #----------------------
    # PDF: Figure name
    #----------------------
    pltFile  = '/home/ivan/chocho/fig/pltCompCU.pdf'


                            #----------------------------#
                            #                            #
                            #        --- start---        #
                            #                            #
                            #----------------------------#

    if saveFlg: pdfsav = PdfPages(outFname)
    else:       pdfsav = False

    clr = dc.clrplt()

    Data = OrderedDict()

    for i,group in enumerate(groups):
        retDir = findData(group, version, dataDir)

        Data[group] = dc.readDataCU(retDir, group, version)

    #-------------------------------------------------------------------------
    #                          PLOTS
    #-------------------------------------------------------------------------

    
    fig, axs = plt.subplots(len(easplt), figsize=(8,10), sharex=True)

    for i, group in enumerate(groups):

        namegroup = getgroupname(group)

        datet_flt         = np.squeeze(np.asarray(Data[group]['tod']))
        chocho_flt        = np.squeeze(np.asarray(Data[group]['chocho']))
        ea_flt            = np.squeeze(np.asarray(Data[group]['ea']))

        for n, nea in enumerate(easplt):

            inds      = np.where(np.array(ea_flt) == nea)[0]
            chocho_w  = np.asarray(chocho_flt[inds])
            dt_w      =  np.asarray(datet_flt[inds])
            ea_w      = np.asarray(ea_flt[inds])
             
            axs[n].scatter(dt_w, chocho_w, edgecolor=clr[i], label=namegroup, color='white')
            axs[n].grid(True, which='both')
            axs[n].set_ylim(-0.8, 6)
            axs[n].set_xlim(5, 20)
            axs[n].set_title('EA = %s'% nea)
            axs[n].tick_params(axis='both', which='both',labelsize=12)

    plt.legend(prop={'size':11}, loc='upper center', bbox_to_anchor=(0.5, 6.3), ncol=int(len(groups)))

    if saveFlg: pdfsav.savefig(fig,dpi=200)
    else: plt.show(block=False)    

        



    if saveFlg: pdfsav.close() 

    if not saveFlg:
        user_input = raw_input('Press any key to exit >>> ')
        sys.exit()    



if __name__ == "__main__":
    main()
