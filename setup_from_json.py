import argparse
import json


def read_json_input(filename):
    """Read input data from a json file

    Parameters
    ----------
    filename: str
        Name of the json input file

    Returns
    -------
    json_data: dict
        Json data
    """
    with open(filename, 'r') as f:
        json_data = json.load(f)
        print(json_data)
        
    return json_data


def make_mastersystem(json_data):
    """Create the template for mastersystem.pro

    Parameter
    ---------
    json_data: dict
        Dictionary built from the json package at read.

    Returns
    -------
    template: str
        Formatted string using info from json.
    """

    #if 'old_template_name' not in json_data['parameters'].keys():
        #dates = json_data['parameters']['mary_run_template'] if type(
            #json_data['parameters']['mary_run_template']) is str else str(
            #[s for s in json_data['parameters']['mary_run_template']])
    #else:
        #dates = json_data['parameters']['template_date'] if type(
            #json_data['parameters']['template_date']) is str else str(
            #[s for s in json_data['parameters']['template_date']])

    return """
pro mastersystem

;;;This program defined the ID code for the transients
;;;discovered during systematic searches in archival data.

;;;;;;;;;;;;;;;;;;;
;EDIT HERE
field='%s'
dates=['%s']
seed='%s%s'
last_mary_run = %s + 1
;FINISHED EDITING
;;;;;;;;;;;;;;;;;;;

extnum=60

;;;For each date
for d=0, n_elements(dates)-1 do begin

date=dates[d]

;;;Check all the Mary runs with the specifield date, field, seed:
lsmarycommand='ls $marywork | grep '+field+'_'+date+'_m'+seed+'_'
spawn, lsmarycommand, lsmaryout


;;;Check that there are enough Mary runs
if (n_elements(lsmaryout) le 1) then begin

    print, 'Too few Mary runs! Something wrong?'
    ;;;;;;;;stop

endif

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;Search radius (1.5 arcsec)
RADCOINCIDENCE=1.5/3600.0
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


;;;Assuming that the numbers after the seed are in a sequence from 1 onward,
;;;Iterate through all of them.

for k=last_mary_run, n_elements(lsmaryout) do begin

k1=string(k)
sequencenumber=strcompress(seed+'_'+k1, /remove_all)

;;;Name of the master catalog:
mastername=strcompress('/fred/oz100/pipes/DWF_PIPE/MARY_CAT' + '/' + field + '_' + date + '_m' + sequencenumber + '.masterlist.txt', /remove_all)

;;;Remove 'system' from the mary number:
sequenceclean0=STRSPLIT(sequencenumber, /EXTRACT, '_')
sequenceclean=sequenceclean0[-1]


;;; Read the list of transients already discovered (with coordinates).
;;; Mary information refer to the first time the transient was discovered.
readcol, format='(F,D,D,A,A,A,A,A,A,A,A)', '/home/fstars/MARY4OZ/transients/transients_coo.txt', IDtr, RAtr, DECtr, FIELDtr, DATEtr, MARYtr, CCDtr, NUMtr,  /SILENT


;;;Open the files to be updated:
OpenU, luncoo, /get_lun, '/home/fstars/MARY4OZ/transients/transients_coo.txt', /APPEND
OpenU, lunclean, /get_lun, '/home/fstars/MARY4OZ/transients/transients_clean.txt', /APPEND


;;;;;;;;;;;;Avoid clobbering?
Openw, lun, /get_lun, mastername

;;;Initialise a counter to keep track of how many new transients are added:
counter=0


;;;For each CCD:
for i=0, extnum-1 do begin

    ;;; i1 is the number of the ccd (STRING)
    i0=string(i+1)
    i1=strcompress(i0, /remove_all)

;;; Path to the single catalog to be read:
    path_cat='/fred/oz100/pipes/DWF_PIPE/MARY_WORK/' + field + '_' + date + '_m' + sequencenumber  + '/ccd' + i1 + '/catalogs'

    singlename=strcompress(path_cat + '/candidates_ranked.cat', /remove_all)


;;; Check if the /candidates_ranked.cat catalog exists:

    lscommand='ls ' + singlename
    spawn, lscommand, lsout

    if (lsout ne '') then begin

;;; Read the catalog:
        readcol, format='(A,A,A,D,D,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A)', singlename, cand, x, y, RA, DEC, mag, magerr,$
        GSCclassI,GSCclass,GSCnumfound,GSCra,GSCdec,GSCepoch,GSCFMAG,GSCJMAG,GSCVMAG,GSCNMAG,priority, mjd, /SILENT

        ;;;Remove possible consecutive repetitions:
        if (min(uniq(RA) eq uniq(DEC)) AND (n_elements(uniq(RA)) ne n_elements(cand))) then begin
            indexnorep=uniq(RA)
            cand=cand[indexnorep]
            x=x[indexnorep]
            y=y[indexnorep]
            RA=RA[indexnorep]
            DEC=DEC[indexnorep]
            mag=mag[indexnorep]
            magerr=magerr[indexnorep]
            GSCclassI=GSCclassI[indexnorep]
            GSCclass=GSCclass[indexnorep]
            GSCnumfound=GSCnumfound[indexnorep]
            GSCra=GSCra[indexnorep]
            GSCdec=GSCdec[indexnorep]
            GSCepoch=GSCepoch[indexnorep]
            GSCFMAG=GSCFMAG[indexnorep]
            GSCJMAG=GSCJMAG[indexnorep]
            GSCVMAG=GSCVMAG[indexnorep]
            GSCNMAG=GSCNMAG[indexnorep]
            priority=priority[indexnorep]
            mjd=mjd[indexnorep]
            print, 'Repetition found and corrected'


        endif

        for z=0, n_elements(cand)-1 do begin

            ;;;Consider only existent RA&DEC, and only priority=>0 candidates
            if (RA[z] ne 0.0 and DEC[z] ne 0.0 AND priority[z] ge 0) then begin

                ;;;Initialize an array for new ID code:
                IDnew=0


;;; We must assign transients a sequence number.
;;; First, check if the transient was already discovered:
;;;Compute the distance between the candidate and each the transients already discovered on the same CCD, in case the priority level is not 0:

                indexCCD=where(CCDtr eq i+1)
                if (indexCCD[0] ne -1) then begin
                    RAtrshort=RAtr(indexCCD)
                    DECtrshort=DECtr(indexCCD)
                    IDtrshort=IDtr(indexCCD)
                    for t=0, n_elements(indexCCD)-1 do begin
                        dist=sqrt( (ra[z]-RAtrshort[t])^2 + (dec[z]-DECtrshort[t])^2  )
                        if (dist le RADCOINCIDENCE) then IDnew=IDtrshort[t]
                    endfor ;;; t, transients already discovered in the same CCD

                endif

            ;;;Assign a new ID number in case there is no match:
                if (IDnew eq 0) then begin
                    counter=counter+1.
                    IDnew=IDtr[-1]+counter
                    ;;;Update the catalogs of transients:
                    printf, luncoo, format='(I,D,D,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A)', IDnew,RA[z],DEC[z],' ',FIELD,' ',DATE,' ',SEQUENCENUMBER,' ',I1,' ',cand[z]
                    printf, lunclean, format='(I,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A)', IDnew,' ',FIELD,' ',DATE,' ',SEQUENCENUMBER,' ',I1,' ',cand[z]
                endif

                idnew0=string(IDnew)
                idnew1=strcompress(idnew0, /remove_all)

                ;;;Write the information in the *.txt files:
                printf, lun, format='(A,D,D,D)', idnew1+'  '+field+'  '+i1+'  '+SEQUENCEclean+'  '+DATE + '  ' + cand[z]$
                +'  '+ x[z]+'  '+y[z]+'  '+mag[z]+'  '+magerr[z]+'  '+priority[z]+'  '+GSCclassI[z]+' ' $
                +GSCclass[z]+' '+GSCnumfound[z]+' '+GSCepoch[z]+' '+GSCFMAG[z]+' '+GSCJMAG[z]+' '+GSCVMAG[z]+' '+GSCVMAG[z], mjd[z], $
                RA[z], DEC[z]



            endif


        endfor   ;;; z, new candidates in each CCD

    endif


endfor




close, luncoo
free_lun, luncoo

close, lunclean
free_lun, lunclean

close, lun
free_lun, lun


;---------------------------------------------

print, ' '
print, '...Done.'
print, 'Finished  field='+field + ' date='+date+ ' mary run=' + sequencenumber
print, ' '

endfor ;;;Finish the loop of dates









endfor

end

    """ % (
        json_data['parameters']['field'],
        json_data['parameters']['date'],
        json_data['parameters']['mary_seed_name'],
        json_data['parameters']['steps'],
        json_data['parameters']['last_mary_run']
    )


def make_mary4parameters(json_data):
    """Create the template for mary4parameters.pro

    Parameter
    ---------
    json_data: dict
        Dictionary built from the json package at read.

    Returns
    -------
    template: str
        Formatted string using info from json.
    """
    return """
; This script, to be run at the beginning of Mary,
; lists all the parameters that can be controlled by the user.


;-----------------------
;     OBSERVATIONS
;-----------------------

; Insert the sequence number (string) of the Mary run (of the night):
SEQUENCENUMBER='test2'  ;;;DO NOT CHANGE!

;Insert the field observed:
FIELD='%s'
;FIELDNUMBER='1' ;;;Number associated with the specific field.

; Insert the date of the observation (string, YYMMDD):
DATE='%s'

; Insert the date of the TEMPLATE (If fast images?):
DATETEMP='%s'

;Insert the filter used for the observation:
FILTER='%s'




;---------------------------
;    PIPELINE SETUP
;---------------------------



; Insert the number (integer) of extensions (CCDs) for each image:
EXTNUM=60

; Do you want to process only a defined array of CCDs? ("YES"/"NO").
; This option dominates over EXTNUM
; default "NO"
someccdschoice="NO"

; If you chose to process a defined array of CCDs (someccdschoice eq "YES")
; Define the array of CCDs.  Integers. E.g.: ccdarr=[1,10,22]
ccdarr=[1,2,3,4,5,6,7,8,9]


; Insert the desired walltime for the qsubmission on OzSTAR ('minutes')
walltime='300'

; insert the name of the text file listing the images (scientific and templates)
;All the images in a list will be stacked together.
;;;If the username is fstars, then Mary will point to the MARY_CONTROL directory to find the lists.

@$marydir/userfinderbatch.pro

if (username ne 'fstars') then list_images_sci='$marywork/list_images_sci.txt'
if (username ne 'fstars') then list_images_temp='$marywork/list_images_temp.txt'
if (username eq 'fstars') then list_images_sci='/home/fstars/MARY4OZ/list_images_sci.txt'
if (username eq 'fstars') then list_images_temp='/home/fstars/MARY4OZ/list_images_temp.txt'
    """ % (
        json_data['parameters']['field'],
        json_data['parameters']['date'],
        000000 if 'old_template_name' in json_data['parameters'].keys() else
        json_data['parameters']['mary_run_template'],
        json_data['parameters']['filter'],
    )


def make_mary4parameters_base(json_data):
    """Create the template for mary4parameters_base.pro

    Parameter
    ---------
    json_data: dict
        Dictionary built from the json package at read.

    Returns
    -------
    template: str
        Formatted string using info from json.
    """
    return """
; This script, to be run at the beginning of Mary,
; lists all the parameters that can be controlled by the user.



;-----------------------
;     OBSERVATIONS
;-----------------------

; Insert the sequence number (string) of the Mary run (of the night):
SEQUENCENUMBER='test1'

;Insert the field observed:
FIELD='ffff'
FIELDNUMBER='1' ;;;Number associated with the specific field.

; Insert the date of the observation (string, YYMMDD):
DATE='dddd'

; Insert the date of the TEMPLATE (If fast images?):
DATETEMP='tttt'

;Insert the filter used for the observation:
FILTER='%s'


;---------------------------
;     TEMPLATE IMAGES
;---------------------------


; Do you want to use an "old template", a stacked image stored in the TEMPLATES directory? ('YES'/'NO')?
useoldtemplate='%s'
oldtemp='%s'

; Do you want to use exactly the same template of another mary run? ('YES'/'NO')?
usemarytemplate='%s'

; Details of the mary run where you want to get the template from:
OTHERDATE='%s'
OTHERSEQUENCENUMBER='%s'
OTHERFIELD=field
OTHERFILTER=filter


;---------------------------
;    PIPELINE SETUP
;---------------------------

; Real time analysis setup, or are you using NOAO portal images? ('RT'/'NOAO')
pipesetup='RT'

;Path to images (active only if you chose NOAO images setup)
path_original='/fred/oz100/fstars/'+FIELD+'/IMAGES'


;Do you want to use weight maps (self-generated) for the coaddition? ('YES'/'NO')
wmapchoice='YES'


; Check WCS? ('YES'/'NO') if yes only images with correct WCS will be processed.
;;;NOT WORKING, LEAVE IT 'NO'
CHECKWCS='NO'


; Insert the number (integer) of extensions (CCDs) for each image:
EXTNUM=60


; insert the name of the text file listing the images (scientific and templates)
;All the images in a list will be stacked together.
;;;If the username is fstars, then Mary will point to the MARY_CONTROL directory to find the lists.

@$marydir/userfinderbatch.pro

list_images_sci='AAA.txt'
list_images_temp='TTT.txt'
;if (username ne 'fstars') then list_images_sci='$marywork/list_images_sci.txt'
;if (username ne 'fstars') then list_images_temp='$marywork/list_images_temp.txt'
;if (username eq 'fstars') then list_images_sci='/home/fstars/MARY4OZ/list_images_sci.txt'
;if (username eq 'fstars') then list_images_temp='/home/fstars/MARY4OZ/list_images_temp.txt'


;------------------------------
;     SOFTWARE VERSIONS
;------------------------------

;;;Swarp 2.38.0
callswarp='/apps/skylake/software/compiler/gcc/6.4.0/swarp/2.38.0/bin/swarp '
;;;;;callswarp='/home/iandreon/swarp-2.15.7/bin/swarp '


;;;SExtractor
callsex='/apps/skylake/software/mpi/gcc/6.4.0/openmpi/3.0.0/sextractor/2.19.5/bin/sex '

;;;HOTPANTS 5.1.11
callhotpants='/apps/skylake/software/compiler/gcc/6.4.0/hotpants/5.1.11/bin/hotpants '

;;;imcopy
callimcopy='/apps/skylake/software/mpi/gcc/6.4.0/openmpi/3.0.0/astrometry.net/0.74/bin/imcopy '

;;;imarith
callimarith='/apps/skylake/software/mpi/gcc/6.4.0/openmpi/3.0.0/astrometry.net/0.74/bin/imarith '

;;;Theano for ML classifier
calltheano='/fred/oz100/cjacobs/code/cnet_test_theano.sh '

;------------------------------
;      SEXTRACTOR and HOTPANTS
;------------------------------

;;;;;;;;;;"POSITIVE" SUBTRACTION;;;;;;;;;;;;;

DETECT_MINAREA_POS = '8'             ;# minimum number of pixels above threshold
THRESH_TYPE_POS='RELATIVE'           ;# threshold type: RELATIVE (in sigmas)
                                 ;# or ABSOLUTE (in ADUs)
DETECT_THRESH_POS = '1.8'           ;# <sigmas> or <threshold>,<ZP> in mag.arcsec-2
ANALYSIS_THRESH_POS = '1.8' 	 ;# <sigmas> or <threshold>,<ZP> in mag.arcsec-2



;;;;;;;;;;"NEGATIVE" SUBTRACTION;;;;;;;;;;;;;


DETECT_MINAREA_NEG = '8'             ;# minimum number of pixels above threshold
THRESH_TYPE_NEG='RELATIVE'           ;# threshold type: RELATIVE (in sigmas)
                                 ;# or ABSOLUTE (in ADUs)
DETECT_THRESH_NEG = '1.3'           ;# <sigmas> or <threshold>,<ZP> in mag.arcsec-2
ANALYSIS_THRESH_NEG = '1.3' 	 ;# <sigmas> or <threshold>,<ZP> in mag.arcsec-2


;;;The lower limit for the HOTPANTS images is determined
;;;by tlsigma*skyvalue (template), ilsigma*skyvalue (science image).
tlsigma=5.0
ilsigma=5.0



;-----------------------
;      IMAGE
;-----------------------

; Dimension of the image (< real size, to align the images)
XDIM=4000
YDIM=2000

;Do you want the size to be fixed even when using old templates? ('YES'/'NO')
fixoldchoice='YES'


; Nominal zeropoint:
zpt=25



;--------------------------------
;      SELECTION OF CANDIDATES
;--------------------------------

; !!!!!!!!!!!VERY IMPORTANT!!!!!!!!!!
; Do you want candidates for only rising, only fading, or both risig and fading luminosities?
; CHOICE=1 >>> only rising
; CHOICE=2 >>> both rising and fading
; CHOICE=3 >>> only fading
CHOICE=1


; max elongation allowed for the selection of the candidates:
elmax=1.8

; Nominal FWHM for the selection of the candidates (in pixels)
; (artifacts smaller than 2*fwhmnominal will be excluded
; and sources with FWHM<1/2*fwhmnominal will be excluded):
fwhmnominal=6.0

; Pixel scale [arcsec/pix]:
SCALE=0.263

; Rough seeing:
;;;;;;;;;;     to be removed  SEEING=fwhmnominal*scale

; Min isoarea (filtered) for a source to be selected:
isoareafmin=20

;Insert the number of pixels of the side of the box into
;which only a single source can stand:
;;;;;;;;;;;;;;to be removed          side=2.0*fwhmnominal

;--------------------------------
;  MACHINE LEARNING CLASSIFIER
;--------------------------------


; There is a neural network available (coded by Colin Jacobs)
; that allows to reject the CCD issues. Do you want to activete it? ('YES'/'NO')
; Note: one needs to activete the GPU nodes to use it.
mlchoice='NO'

; Threshold for the ML classifier to reject CCD issues:
; (0=CCD issue, 1=not CCD issue, typical value classthresh=0.5)
classthresh=0.5




;------------------------------------------
;  CATALOGS, BRIGHT SOURCES AND CROSSTALK
;------------------------------------------


;Do you want to manually set the SATURATION level, instead of using the one given in the header? ('YES'/'NO')
; If 'YES', choose the saturation level in ADUs:
satlevelchoice='YES'
fixsatlevel=5000


; What do you want to do with the crosstalk and with the saturating sources? ('KEEP'/'ELIMINATE')
; ELIMINATE -> no postage stamp will be created, no record in candidates list;
; FLAG -> (............to be coded............)
crosschoice='ELIMINATE'
saturchoice='ELIMINATE'

;Maximum number of sources allowed per CCD. If this number is exceeded,
;the program stops:
maxsources=50

;;;Do you want to query online or downloaded GSC catalog? ('O'/'D')
querychoice='D'

;;;Path of the downloaded catalogs (active only if the above is 'D')
pathdownloadedGSC='/home/iandreon/MARY4/catalogs/catalog_'+field+'_GSC2.3.fits'

;Search radius to compare with the GSC catalog. (arcsec)
radiusGSC=1.0

; Magnitude (R2 band for the USNO-B1) for which a source is considered too bright:
BRIGHTMAG=16  ;;;NOT ACTIVE

;------------------------------------------
;              RANKING
;------------------------------------------

;Array with other nights (integers)
nightsarray=[180607,180608,180609]

;When calculating a ranking, one can filter the mary runs
;that they prefer. (STRING, example: rankfilter='m*systembis5*')
rankfilter='*NOAO*'


;Matching radious for Mary detections in different mary runs:
;;;;;;;;;;;;;;;to be removed        matchradius=1.5


;---------------------------------------
;           PHOTOMETRY
;---------------------------------------

;The photometry of the candidates (and reference stars)
;on the science image and zeropoint calibration (sci+temp)
;are optional. Do you want to perform it within Mary?
photochoice='YES'

;;;Which catalog do you want to use for the calibration? ('USNO-B1'/'gaia')
catalogcalib='USNO-B1'

;Path to the stars used as reference:
path_star='/fred/oz100/pipes/DWF_PIPE/STARS/'+field

;--------------------------------
;      VISUALISATION
;--------------------------------

;Insert the radius of the circular rigion in pixels and world coord:
radcir_i='12'
radcir_w='8' + string(34B)

;Insert the side of the stamps (in pixels):
sidestamp=121

;Insert the zoom value to display the postage stamps (or 'to fit')
ZOOMVALUE='2'
    """ % (
        # observation
        json_data['parameters']['filter'],
        # template
        'YES' if 'old_template_name' in json_data['parameters'].keys() else 'NO',
        json_data['parameters']['old_template_name'] if 'old_template_name' in json_data['parameters'].keys() else 'not_needed',
        'YES' if 'old_template_name' not in json_data['parameters'].keys() else 'NO',
        000000 if 'old_template_name' in json_data['parameters'].keys() else
        json_data['parameters']['mary_run_template'],
        '' if 'old_template_name' in json_data['parameters'].keys() else '0',
    )


def make_controlccd(json_data):
    """Create the template for controlccd.py

    Parameter
    ---------
    json_data: dict
        Dictionary built from the json package at read.

    Returns
    -------
    template: str
        Formatted string using info from json.
    """
    return """
#
#Author: Igor Andreoni, 2018
#
###This program monitors when the output files
###are created after the end of a queue job. 
###[OR I CAN CREATE AN OUTPUT AFTER THE END OF EVERY MARY4CCD SCRIPT]
### At the end, it updates the parameter file, creating a new copy, and
### a new list of images to process.

i=0
import sys
import os.path
import subprocess
from subprocess import call
import time 
import pdb
from astropy.table import Table
import csv


#@@@@@@@@@@@@@@@
#I need to:
#- create the directories
#- create a log
#- copy and modify the parameter file
#- create the list of images (and modify the path in the param file)
#- skyp the set of images if the three of them are not available,
#  reporting the outcome in the log


def control(field='ngc6744', date='160806', datetemp='160730',ccd='1', listname='/home/fstars/MARY4OZ/list_images_tot.txt',step=3,maryseed='seed',useoldtemp='YES',usemarytemp='NO', synmode=False, synseed='systembis1_',clobber=True):	

#########################

#IF THE SYNTHESIS OPTION IS ACTIVE (synmode=True) create a meta-list_images_tot.txt 
    if (synmode == True):
        #list of mary run with the chosen synseed - TO BE SORTED
        listnotsorted=os.popen('ls /fred/oz100/pipes/DWF_PIPE/MARY_WORK | grep '+field+'_'+date+'_m'+synseed).read().splitlines()
        #insulate the number of mary run

        numlist=[]
        for name in listnotsorted:
            #This is needed in case there are missing numbers in the sequence of mary runs
            num=name.split('_')[-1]	
            numlist.append(int(num))
        #Sort the list
        numlist.sort()


        #Create command to create the list of images
        catcommand='cat'

        for num in numlist:
            catcommand=catcommand+' ' + '/fred/oz100/pipes/DWF_PIPE/MARY_WORK/'+field+'_'+date+'_m'+synseed+str(num)+'/ccd'+str(ccd) + '/list_images_sci.txt'

        #Create the list of images
        imlist2=os.popen(catcommand).read().splitlines()


#if (synmode=False) read the list of images 	
    if (synmode == False):

        # Read the list of images
        f = open(listname, 'r')
        #imgtable= f.read()
        imlist2=[]

        for line in f:
            singleimg=line.strip()
            imlist2.append(singleimg)
        f.close()

#Create a table organised with as many rows 
#as Mary runs, as many columns as images to be coadded in each Mary run	

    #How many groups, i.e. how many mary runs?
    step=int(step)
    ngroups=len(imlist2)/step
    n=0

    #How many images are left?
    nleft=len(imlist2)-(ngroups*step)

    '''if nleft == 0:
        print 'The number of images (' + str(len(imlist2)) + ') is a multiple of the chosen step (' + str(step)+'), very good.'
        #Total number of groups
        ntot=ngroups
    else:
        print 'The number of images (' + str(len(imlist2)) + ') is not a multiple of the chosen step (' + str(step)+').'
        print 'The last '+str(nleft)+' images will be coadded separately.'
        #Total number of groups
        ntot=ngroups+1'''

    #Create a list of lists, each with a number of images equal to the desired step
    data_rows=[]
    while n < ngroups:
        #initialise the variables
        images=[]
        add=0	

        for i in range(step):
        #Add an image to the individual row
            images.append(imlist2[(n*step)+add])
            add=add+1
        data_rows.append(images)
        n=n+1

    #Additional images
    if n == ngroups:
        #If there is at least one image:
        if nleft >=1:

            #initialise the variables
            images=[]
            add=0
            for i in range(nleft):
                images.append(imlist2[(n*step)+add]) 
                add=add+1

            #For the missing images add a '0' placeholder
            for k in range(step-nleft):
                images.append('0')

            data_rows.append(images)

    #Create the table with as many rows as mary runs, as many columns as images to be coadded in each mary run (step).
    t = Table(rows=data_rows, meta={'name': 'table of images'})


########################
#Initialise the parameters
    m=%s  #Mary run initialised
    SEQUENCENUMBER_BASE='test1'
    LIST_IMAGES_SCI_BASE='AAA.txt'
    LIST_IMAGES_TEMP_BASE='TTT.txt'
    FIELD_BASE='ffff'
    DATE_BASE='dddd'
    DATETEMP_BASE='tttt'
    USEOLDTEMP_BASE='useoldtempYN'
    USEMARYTEMP_BASE='usemarytempYN'

########################
#Update the lists
############################################################################
    #For each set of images
    for comp,i in zip(t['col0'],range(len(t['col0']))):
        #Increase the number of mary run
        m=m+1
        #name of the mary run (seed AAA run BBB)
        maryname=maryseed+str(m)	


#######################################

        if (clobber == False):
            #Don't clobber succesful processing, i.e. when the candidates_ranked.cat file is generated
            #Note that this will make the program re-analyse the data in case no good candidate was selected!
            finished='/fred/oz100/pipes/DWF_PIPE/MARY_WORK/'+field+'_'+date+'_m'+maryname+'/ccd'+str(ccd)+'/catalogs/candidates_ranked.cat'
            lsfinished=os.popen("ls " + finished).read().splitlines()

            #Skip the Mary run if the final file is present
            if (lsfinished != []):
                continue

########################
#Create the directories

        path_top='/fred/oz100/pipes/DWF_PIPE/MARY_WORK/'+field+'_'+date+'_m'+maryname
        path_ccd='/fred/oz100/pipes/DWF_PIPE/MARY_WORK/'+field+'_'+date+'_m'+maryname+'/ccd'+str(ccd)
        path_catalogs='/fred/oz100/pipes/DWF_PIPE/MARY_WORK/'+field+'_'+date+'_m'+maryname+'/ccd'+str(ccd)+'/catalogs'
        path_images='/fred/oz100/pipes/DWF_PIPE/MARY_WORK/'+field+'_'+date+'_m'+maryname+'/ccd'+str(ccd)+'/images'
        path_resamp='/fred/oz100/pipes/DWF_PIPE/MARY_WORK/'+field+'_'+date+'_m'+maryname+'/ccd'+str(ccd)+'/images_resampled'
        path_sub='/fred/oz100/pipes/DWF_PIPE/MARY_SUB/'+field+'_'+date+'_m'+maryname
        path_stamp='/fred/oz100/pipes/DWF_PIPE/MARY_STAMP/'+field+'_'+date+'_m'+maryname
        path_reg='/fred/oz100/pipes/DWF_PIPE/MARY_CAT/REGIONS/'+field+'_'+date+'_m'+maryname

        #Make the directories
        os.system('mkdir '+path_top)
        os.system('mkdir '+path_ccd)
        os.system('mkdir '+path_catalogs)
        os.system('mkdir '+path_images)
        os.system('mkdir '+path_resamp)
        os.system('mkdir '+path_sub)
        os.system('mkdir '+path_stamp)
        os.system('mkdir '+path_reg)

#Change directory		
        os.chdir(path_ccd)

#######################
#Create the list of science images
        scilist=path_ccd+'/list_images_sci.txt'
        templist='/home/fstars/MARY4OZ/list_images_temp.txt'

        #Clobber the list of science images
        os.system('rm ' + scilist)

        print('List of science images removed before beginning.')
        #Complete the list with as many images are present in each step
        for im in range(step):
            #Check if the image has a real code
            if (t[i][im] != '0'):
                with open(scilist, 'a') as scifile:
                        scifile.write(t[i][im] + '%s') 

######################
#If "new template images" are used, copy the list in each directory 
        if (useoldtemp == 'NO'):
            newtemplist=path_ccd+'/list_images_temp.txt'
            cptempcommand='cp '+templist+' '+newtemplist
            os.system(cptempcommand)
            #Reassign the template list variable
        else:
            newtemplist=templist


######################
#Create the parameter file

        #Copy the parameters file, changing the SEQUENCENUMBER and the path to the list of science images 
        oldparam='/home/fstars/MARY4OZ/mary4parameters_base.pro'
        newparam=path_ccd + '/mary4parameters.pro'

        #######
        ######

        #if (comp != '85'):
        #	continue


        ######
        #######

        awkcommand=''' awk '{gsub(/''' + SEQUENCENUMBER_BASE + '''/, "''' + maryname + '''")}; \
        {gsub(/''' + DATE_BASE + '''/, "''' + date + '''")}; \
        {gsub(/''' + DATETEMP_BASE + '''/, "''' + datetemp + '''")}; \
        {gsub(/''' + FIELD_BASE + '''/, "''' + field + '''")}; \
        {gsub(/''' + LIST_IMAGES_SCI_BASE + '''/, "''' + scilist + '''")}; \
        {gsub(/''' + LIST_IMAGES_TEMP_BASE + '''/, "''' + newtemplist + '''")}; \
        {gsub(/''' + USEOLDTEMP_BASE + '''/, "''' + useoldtemp + '''")}; \
        {gsub(/''' + USEMARYTEMP_BASE + '''/, "''' + usemarytemp + '''")}; \
        {print}' '''+oldparam+''' > '''+newparam

        os.system(awkcommand)

######################
#Create the ccdnumber.txt file
        with open('ccdnumber.txt', 'w') as ccdfile:
                ccdfile.write(ccd) 


######################
#Start the IDL command
        os.system("idl < /home/fstars/MARY4OZ/mary4ccd.pro ")

######################
#Define the name of the final output (finished.txt) and wait until the job is done
        #finalout=path_ccd+'/finished.txt'			

        #while not os.path.exists(finalout):
            #	time.sleep(3)
        #	print 'Checking for the final file to be created.....'
        #print 'Finished mary run m'+maryname



########################################################
########################################################
#  EDIT HERE
########################################################

#Insulate the ccd information
a=list(sys.argv)
ccdinput=str(a[1])

#Trigger the command
if (ccdinput != '30'):
#Define the main field, the dates, and the step for the coaddition (how many images do you want to coadd each time?)
    field='%s'

    #Date of the template
    datetemp='%s'

    #Date of the science image(s)
    for date in ['%s']:
        #How many images to be stacked together?
        for step in [%d]:
            #Define the seed for each mary run (e.g., 'rt'+str(step)  for the real-time processing)
            maryseedname='%s'+str(step) +'_'

            #Most important function!	
            control(field=field, date=date, datetemp=datetemp,ccd=ccdinput,step=step,maryseed=maryseedname,useoldtemp='%s',usemarytemp='%s', synmode=False, synseed='test1_',clobber=%s)
            #Added the "syn(thesis)" option, in order to consider only science images generated in previous Mary runs.
            #usesyn=True will use the image codes present in the list_images_sci.txt files of each Mary run with the same field, same date, but the 'synseed' seed.
            #At the moment the clobber is based on the presence of the candidates_ranked.cat files, thus the processing is repeated in case no good candidate was detected. 
print('SUCCESS')

    """ % (
        json_data['parameters']['last_mary_run'],
        r"\n",
        json_data['parameters']['field'],
        json_data['parameters']['mary_run_template'] if 'old_template_name' not in json_data['parameters'].keys() else
        000000,
        # Might need to add a condition if date is a list. In which case, look at previous functions for examples of one liners
        json_data['parameters']['date'],
        json_data['parameters']['steps'],
        json_data['parameters']['mary_seed_name'],
        'YES' if 'old_template_name' in json_data['parameters'].keys() else 'NO',
        'YES' if 'mary_run_template' in json_data['parameters'].keys() else 'NO',
        json_data['parameters']['clobber']

    )


def write_list_images_tot(json_data):
    """Writes list_images_tot.txt

    Parameter
    ---------
    json_data: dict
        Dictionary built from the json package at read.
    """
    s = json_data['parameters']['image_names'] 
    new_list =s.split(',')

    with open('list_images_tot.txt', 'w') as f:
        for im_num in new_list:
            s = im_num
            im_num = s.strip()
            f.write(im_num +'\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--json_filename',
                        help="JSON Input file",
                        type=str,
                        required=True)

    args = parser.parse_args()

    json_data = read_json_input(args.json_filename)

    with open('mastersystem.pro', 'w') as f:
        f.write(make_mastersystem(json_data))

    with open('mary4parameters.pro', 'w') as f:
        f.write(make_mary4parameters(json_data))

    with open('mary4parameters_base.pro', 'w') as f:
        f.write(make_mary4parameters_base(json_data))

    with open('controlccd.py', 'w') as f:
        f.write(make_controlccd(json_data))

    write_list_images_tot(json_data) 
    print('Mary Submit files saved')
