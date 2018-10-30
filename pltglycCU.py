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
from scipy import stats


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

    if group == 'BOU':
        folder = group+'/'
        if version == 'V1':
            #DirFile = dataDir + folder + 'CUBoulder_2DMAXDOAS_v1_06182013_CHOCHO_06182013_v1_const.asc'
            DirFile = dataDir + folder + 'CUBoulder_2DMAXDOAS_v1_06182013_CHOCHO_06182013_v1.asc'
        if version == 'V3':
            DirFile = dataDir + folder + 'CUBoulder_2DMAXDOAS_v1_06182013_CHOCHO_06182013_v1.asc'
    
    if group == 'BIR':
        folder = group + '/bira_Cu-Boulder_analysis/'
        if version == 'V1':
            #DirFile = dataDir + folder + 'bira_CU-Boulder_Setting1-VIS434460_CHOCHO_20130718.asc'
            DirFile = dataDir + folder + 'bira_CU-Boulder_Setting1-VIS434460_CHOCHO_20130718_v2.asc'
        if version == 'V3':
            DirFile = dataDir + folder + 'bira_CU-Boulder_Setting3-VIS434460_CHOCHO_20130718.asc'
            #DirFile = dataDir + folder + 'bira_CU-Boulder_Setting3-VIS434460_CHOCHO_20130718_v2.asc'

    elif group == 'BRE':
        folder = group + '/v8/v8/'
        #folder = group + '/v7/v7/'
        if version == 'V1':
            DirFile = dataDir + folder + 'Boulder_instr_Vis434460_CHOCHO_20130618_v8a.asc'
            #DirFile = dataDir + folder + 'Boulder_instr_Vis434460_CHOCHO_20130618_v7a.asc'
        if version == 'V3':
            DirFile = dataDir + folder + 'Boulder_instr_Vis434458_CHOCHO_20130618_v8c.asc'

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
            #DirFile = dataDir + folder + 'MPIC_CU-Boulder_Vis1_CHOCHO_20130618_v2.asc'
            #DirFile = dataDir + folder + 'MPIC_CU-Boulder_Vis1_CHOCHO_20130618_v3.asc'
            DirFile = dataDir + folder + 'MPIC_CU-Boulder_Vis1_CHOCHO_20130618_v11.asc'
            
        if version == 'V3':
            #DirFile = dataDir + folder + 'MPIC_CU-Boulder_Vis3_CHOCHO_20130618_v2.asc'
            #DirFile = dataDir + folder + 'MPIC_CU-Boulder_Vis3_CHOCHO_20130618_v3.asc'
            DirFile = dataDir + folder + 'MPIC_CU-Boulder_Vis3_CHOCHO_20130618_v11.asc'

    elif group == 'MAI-YW':
        #folder = group + '/MPIC_YW//submited_results/originalSF&Cali/'
        #folder = group + '/MPIC_YW/submited_results/fittedwavelengthdependentgaussianSF&fittedCali/'
        folder = group + '/MPIC_YW/submited_results/shiftedSFby0.0413&fittedCali/'
        
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
    elif group == 'MAI-JR': groupn = 'MPIC-JR'
    elif group == 'HEI': groupn = 'Heidelberg'
    elif group == 'INT': groupn = 'INTA'
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
    groups       = ['BIR', 'BRE', 'BOU', 'HEI', 'INT', 'MAI-JR', 'MAI-YW']                 #Group ID identifier

    #----------------------
    # Importan Inputs for plots
    #----------------------
    version    = 'V1'                                                             #Name of retrieval version to process (v1,v2,v3, or v4)
    easplt      = [2,3,5,8, 10, 30]                                                          #EAs for plots

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
    saveFlg    = True   

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

    if saveFlg: pdfsav = PdfPages(pltFile)
    else:       pdfsav = False

    clr = dc.clrplt()

    Data = OrderedDict()

    groups = list(set(groups))
    groups.sort()

    for i,group in enumerate(groups):
        retDir = findData(group, version, dataDir)

        Data[group] = dc.readDataCU(retDir, group, version)

    #-------------------------------------------------------------------------
    #                          PLOTS
    #-------------------------------------------------------------------------
    
    fig, axs = plt.subplots(len(easplt), figsize=(9.25,11), sharex=True)

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

            if n == len(easplt)-1: axs[n].set_xlabel('Time [UT]', fontsize=12)
            if n ==  len(easplt)/3: axs[n].set_ylabel(r'CHOCHO dSCD [x10$^{15}$ molecules$\cdot$cm$^{-2}$]',multialignment='left', fontsize=14)

    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, prop={'size':11},  bbox_to_anchor=(0.5, 0.985), loc='upper center', ncol=int(len(groups)))
    fig.subplots_adjust(left=0.08, right=0.95, top=0.925, bottom=0.05)



    xgroup  = 'BOU'
    groups2 = [g for g in groups if g != xgroup]

    clr2    = [c for i, c in enumerate(clr) if groups[i] != xgroup]
    
    datet_xgroup         = np.squeeze(np.asarray(Data[xgroup]['tod']))
    chocho_xgroup        = np.squeeze(np.asarray(Data[xgroup]['chocho']))
    ea_xgroup            = np.squeeze(np.asarray(Data[xgroup]['ea']))



    fig2, axs = plt.subplots(len(easplt), figsize=(9.25,11), sharex=True)
    fig3, axs3 = plt.subplots(3, figsize=(10,10), sharex=True)

    for n, nea in enumerate(easplt):

        rsquare_g      = []
        slope_g        = []
        intercept_g    = []
        r_g            = []
        xx_g           = []
        namegroup2     = []

        for i, group in enumerate(groups2):

            namegroup = getgroupname(group)
  
            datet_flt         = np.squeeze(np.asarray(Data[group]['tod']))
            chocho_flt        = np.squeeze(np.asarray(Data[group]['chocho']))
            ea_flt            = np.squeeze(np.asarray(Data[group]['ea']))

            inds      = np.where(np.array(ea_xgroup) == nea)[0]

            chocho_x  = np.asarray(chocho_xgroup[inds])
            dt_x      =  np.asarray(datet_xgroup[inds])
            ea_x      = np.asarray(ea_xgroup[inds])

            inds2      = np.where(np.array(ea_flt) == nea)[0]

            chocho_w  = np.asarray(chocho_flt[inds2])
            dt_w      =  np.asarray(datet_flt[inds2])
            ea_w      = np.asarray(ea_flt[inds2])

            if len(chocho_w) != len(chocho_x):
                chocho_w = np.interp(dt_x, dt_w, chocho_w )

            slope, intercept, r_value, p_value, std_err = stats.linregress(chocho_x,chocho_w)
            slope_g.append(slope)
            intercept_g.append(intercept)
            r_g.append(r_value)
            xx_g.append(i)
            namegroup2.append(namegroup)
             
            axs[n].scatter(dt_x, np.true_divide(chocho_w-chocho_x, chocho_x)*100., edgecolor=clr2[i], label=namegroup, color='white')
            axs[n].grid(True, which='both')
            axs[n].set_ylim(-180, 180)
            axs[n].set_xlim(5, 20)
            axs[n].set_title('EA = %s'% nea)
            axs[n].tick_params(axis='both', which='both',labelsize=12)

            if n == len(easplt)-1: axs[n].set_xlabel('Time [UT]', fontsize=12)
            if n ==  len(easplt)/3: axs[n].set_ylabel(r'Relative difference [$\%$, (group - Boulder)/Boulder]',multialignment='left', fontsize=14)

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

    handles, labels = axs[0].get_legend_handles_labels()
    fig2.legend(handles, labels, prop={'size':11},  bbox_to_anchor=(0.5, 0.985), loc='upper center', ncol=int(len(groups)))
    fig2.subplots_adjust(left=0.1, right=0.95, top=0.925, bottom=0.05)

    handles, labels = axs3[0].get_legend_handles_labels()

    fig3.legend(handles, labels, prop={'size':12},  bbox_to_anchor=(0.5, 0.96), loc='upper center', ncol=int(len(easplt)))
    #fig3.suptitle(title, fontsize=16) 
    fig3.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1)     

    my_xticks = namegroup2
    plt.xticks(xx_g, my_xticks, rotation=45)

    if saveFlg: 
        pdfsav.savefig(fig,dpi=200)
        pdfsav.savefig(fig2,dpi=200)
        pdfsav.savefig(fig3,dpi=200)
    else: plt.show(block=False)    
  

        



    if saveFlg: pdfsav.close() 

    if not saveFlg:
        user_input = raw_input('Press any key to exit >>> ')
        sys.exit()    



if __name__ == "__main__":
    main()
