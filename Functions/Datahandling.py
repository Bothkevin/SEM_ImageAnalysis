import hyperspy.api as hs
import os
import glob
import cv2 as cv
import numpy as np

from Custom.Location import Location
from Plots.make_plots import colormap, plot_circles, plot_MassContour, plot_histograms

#Loads the images, including corresponding scale
def load_image(file,foldercounter,filecounter):

    Original_image = hs.load(file)
    SetScale = Location.SEM_scale()
    CurrentScale = SetScale[foldercounter][filecounter]

    return Original_image, CurrentScale


def Calibrate_image(Original, Scale, SetScaleUnit):

    Xmin = 0
    Ymin = 0
    Xmax = len(Original.data[0,:])
    Ymax = len(Original.data[:,0])

    CalibratedCopy = Original.deepcopy()
    CalibratedCopy.change_dtype('uint8')
    CalibrateMask = CalibratedCopy.data[:,:,0] > 0

    CalibrateCounter = 0
    for pixel in CalibrateMask[:,0]:
        if pixel == False:
            Ymax = CalibrateCounter
            break
        CalibrateCounter += 1

    PictureCopy = Original.isig[Xmin:Xmax, Ymin:Ymax]
    ColorCopy = Original.isig[Xmin:Xmax, Ymin:Ymax]
    ScalebarCopy = Original.isig[Xmax/2:Xmax, Ymax:Ymax+10]
    PictureCopy.change_dtype('uint8')
    ScalebarCopy.change_dtype('uint8')

    ScalebarCounter = 0
    for j in range(0,len(ScalebarCopy.data[1,:]),1):
        if ScalebarCopy.data[2,j][0] > 170:
            if ScalebarCounter == 0:
                FirstTick = j
            else:
                LastTick = j
            ScalebarCounter += 1
    deltaTick = LastTick - FirstTick
    Scalebar = Scale/deltaTick

    ColorCopy.axes_manager[0].scale = Scalebar
    ColorCopy.axes_manager[1].scale = Scalebar
    ColorCopy.axes_manager[0].units = SetScaleUnit
    ColorCopy.axes_manager[1].units = SetScaleUnit

    PictureCopy.axes_manager[0].scale = Scalebar
    PictureCopy.axes_manager[1].scale = Scalebar
    PictureCopy.axes_manager[0].units = SetScaleUnit
    PictureCopy.axes_manager[1].units = SetScaleUnit

    Original.axes_manager[0].scale = Scalebar
    Original.axes_manager[1].scale = Scalebar
    Original.axes_manager[0].units = SetScaleUnit
    Original.axes_manager[1].units = SetScaleUnit

    return Original, PictureCopy, ColorCopy, Scalebar


def MaskZeroBelow(Image, Intensity, foldercounter, filecounter):

    MaxPixel = Image.data[:,:,0].max()
    Threshold = int(MaxPixel*Intensity[foldercounter][filecounter])
    Mask = Image.data[:,:,0] < Threshold
    MaskedImage = Image.deepcopy()
    MaskedImage.data[Mask] = 0

    return MaskedImage

def MaskZeroAbove(Image, Intensity, foldercounter, filecounter):

    MaxPixel = Image.data[:,:,0].max()
    Threshold = int(MaxPixel*Intensity[foldercounter][filecounter])
    Mask = Image.data[:,:,0] > Threshold
    MaskedImage = Image.deepcopy()
    MaskedImage.data[Mask] = 0

    return MaskedImage


def Convert_RGBA_to_GrayScale(image):

    row, col, ch = image.data.shape
    GrayScale = np.zeros((row,col), dtype = 'uint8')
    r,g,b,a = image.data[:,:,0],image.data[:,:,1],image.data[:,:,2],image.data[:,:,3]
    GrayScale = (r+g+b)/3

    return GrayScale


def find_contours(GrayScale):

    tmp = 'tmp.png'
    cv.imwrite(tmp,GrayScale)
    frame = cv.imread(tmp)
    os.remove(tmp, dir_fd = None)
    frame = cv. cvtColor(frame, cv.COLOR_BGR2GRAY)
    ret, frame = cv.threshold(frame,10,255,cv.THRESH_BINARY)
    contours, hierarchy = cv.findContours(frame,cv.RETR_TREE,cv.CHAIN_APPROX_TC89_L1)
    return contours, frame


def Mass_centers(contours):

    Area = []
    MassCenterX = []
    MassCenterY = []
    TotalArea = 0

    for contour in contours:
        CurrentArea = cv.contourArea(contour)
        if CurrentArea > 5:
            Area.append(CurrentArea)
            TotalArea += CurrentArea
            M = cv.moments(contour,0)
            if(M['m00']!=0):
                MassCenterX.append(int(M['m10']/M['m00']))
                MassCenterY.append(int(M['m01']/M['m00']))
    return Area, MassCenterX, MassCenterY, TotalArea


def determine_configuration(MCX1,MCY1,MCX2,MCY2, Area1,Area2, Closeness, Scale):

    Counter1 = 0
    CloseList = []
    TmpList = []
    Characterization = [None]*len(Area1)
    Position = []

    for A1 in Area1:
        Counter2 = 0
        R1 = np.sqrt(A1/np.pi)
        for A2 in Area2:
            R2 = np.sqrt(A2/np.pi)
            Distance = np.sqrt((MCX1[Counter1]-MCX2[Counter2])**2 + (MCY1[Counter1]-MCY2[Counter2])**2)
            if Distance <= R1+R2+Closeness/Scale and Distance > 2* Scale:
                NewEntry = int(Counter1), int(Counter2),Distance
                Newtempentry = str(Counter1)
                if Newtempentry in TmpList:
                    Characterization[Counter1] = 'Ladybug'
                else:
                    Characterization[Counter1] = 'Antenna-Reactor'
                CloseList.append(NewEntry)
                TmpList.append(Newtempentry)
            Counter2 += 1
        Counter1 += 1
    for tmp in TmpList:
        R1 = np.sqrt(Area1[int(tmp)]/np.pi)
        counter1 = 0
        for A1 in Area1:
            if counter1 != int(tmp):
                R11 = np.sqrt(A1/np.pi)
                Distance = np.sqrt((MCX1[int(tmp)]-MCX1[counter1])**2 + (MCY1[int(tmp)]-MCY2[counter1])**2)
                if Distance <= R1 + R11 + Closeness/Scale:
                    Characterization[int(tmp)] = 'Ladybug'
            counter1 += 1
    counter = 0
    for Char in Characterization:
        if Char == 'Antenna-Reactor':
            newPos = MCX1[counter], MCY1[counter]
            Position.append(newPos)
        counter += 1
    CloseArray = np.asarray(CloseList)
    ArrayPosition = np.asarray(Position)

    return CloseArray, Characterization, ArrayPosition


def treat_data():

    path = Location.SEM_path()
    folders = Location.SEM_folder()
    foldercounter = 0

    for folder in folders:
        filecounter = 0
        files = glob.glob(path+folder+'Picture*.tif')
        for file in files:
            save = file.split('\\')[-1]
            save = path + folder + 'Analysis\\' + save.split('.')[0] + '_'
            Ausave = save + 'Au_'
            Nisave = save + 'Ni_'
            #Copy and calibrate original image
            Original, Scale = load_image(file, foldercounter,filecounter)
            CalibratedOriginal, CalibratedCopy, ColorCopy, Scalebar = Calibrate_image(Original, Scale, Location.SEM_ScaleUnit())
            #Mask the pixels according to their intensity
            AuMasked = MaskZeroBelow(CalibratedCopy, Location.SEM_highIntensity(), foldercounter, filecounter)
            NiMasked = MaskZeroAbove(CalibratedCopy, Location.SEM_highIntensity(), foldercounter, filecounter)
            NiMasked = MaskZeroBelow(NiMasked, Location.SEM_highIntensity(), foldercounter, filecounter)
            #create a colormap
            Colormap = colormap(ColorCopy, AuMasked, Location.SetColor()[1])
            FinalColor = colormap(Colormap, NiMasked, Location.SetColor()[0])
            FinalColor.save(save+'Colormap.png', overwrite = True, scalebar = True)

            #convert to GrayScale
            AuGray = Convert_RGBA_to_GrayScale(AuMasked)
            NiGray = Convert_RGBA_to_GrayScale(NiMasked)

            #get the pixels belonging to either Au or Ni
            Aucontours, Auframe = find_contours(AuGray)
            Nicontours, Niframe = find_contours(NiGray)

            #Determine Area and position of particles
            AuArea, AuMassCenterX, AuMassCenterY, AuTotalArea = Mass_centers(Aucontours)
            NiArea, NiMassCenterX, NiMassCenterY, NiTotalArea = Mass_centers(Nicontours)

            #Determine the configuration and find the AntennaReactor positions
            CL, CH, AP = determine_configuration(AuMassCenterX, AuMassCenterY, NiMassCenterX, NiMassCenterY, AuArea, NiArea,Location.MinDistance(),Scalebar)

            #plot colormap with circles, Ni and Au areas with circle, and histogram
            plot_circles(Location.MinDistance(), AP, CalibratedCopy, Scalebar, save)
            plot_MassContour(Auframe, AuArea, AuMassCenterX, AuMassCenterY, 'red', Ausave)
            plot_MassContour(Auframe, AuArea, AuMassCenterX, AuMassCenterY, 'red', Ausave)
            plot_histograms(AuArea,Scalebar,Location.SEM_ScaleUnit(),50,Ausave,AP)
            plot_histograms(NiArea,Scalebar,Location.SEM_ScaleUnit(),50,Nisave,AP)

            filecounter += 1

        foldercounter += 1
