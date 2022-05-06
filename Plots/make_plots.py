import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

def colormap(image, elementmap, color):

    colormask = elementmap.data[:,:,0] >0
    image.data[colormask] = color

    return image


def plot_circles(MinDis, AP, CalibratedCopy,Scalebar,save):

    fig = plt.figure(figsize = (28,20))
    ax = plt.subplot()
    CurrentR = MinDis/Scalebar
    for j in range(0,len(AP)):
        CurrentX = AP[j][0]
        CurrentY = AP[j][1]
        Circle = plt.Circle((CurrentX, CurrentY), CurrentR, color = 'red', fill = False, linewidth = 5)
        ax.add_patch(Circle)
    ax.imshow(CalibratedCopy)
    ax.set_axis_off()
    fig.tight_layout(pad=3)
    fig.savefig(save+'AntennaReactor.png')
    plt.close('all')


def plot_MassContour(frame,Area,MassCenterX,MassCenterY,COLOR,save):
    fig = plt.figure(figsize = (7,5))
    ax1 = plt.subplot()
    for j in range(0,len(MassCenterX)):
        CurrentR = np.sqrt(Area[j]/np.pi)
        if CurrentR != 0:
            CurrentX = MassCenterX[j]
            CurrentY = MassCenterY[j]
            Circle = plt.Circle((CurrentX,CurrentY), CurrentR,color = COLOR)
            ax1.add_artist(Circle)
    ax1.imshow(frame)
    ax1.set_title(save)
    ax1.set_axis_off()
    fig.tight_layout(pad=3)
    fig.savefig(save+'Contour.png')
    plt.close('all')


def plot_histograms(Area,Scalebar,SetScaleUnit,maxvalue,save,AP):
    bins = int(100/(2*Scalebar))
    fig = plt.figure(figsize=(28,10))
    gs = gridspec.GridSpec(1,2)

    ax1 = plt.subplot(gs[0,0])
    D = []
    dMax = 0
    dMin = 2*np.sqrt(Area[0]/np.pi)

    for A in Area:
        currentD = 2*np.sqrt(A/np.pi)
        if currentD > dMax:
            dMax = currentD
        if currentD < dMin:
            dMin = currentD
        D.append(currentD)

    RD = [round(num,1) for num in D]

    ax1.hist(RD,bins)
    ax1.set_xticks(np.arange(0,maxvalue,10))
    ax1.set_xlabel('Diameter [nm]', size = 28)
    ax1.set_ylabel('Count [a.u.]', size = 28)
    ax1.set_xlim([0,maxvalue])
    ax1.set_title(save)
    ax1.tick_params(direction = 'out', length = 8, width = 4, colors = 'k', grid_color = 'k', grid_alpha = 0.5, labelsize = 24)

    ax2 = plt.subplot(gs[0,1])

    NumberParticles = len(RD)
    cell_text = [[NumberParticles, '%.1f' %dMax, '%.1f' %dMin, len(AP)]]
    column_labels = ['Number of Particles', 'Max. Diameter [nm]', 'Min. Diameter [nm]', '# Antenna-Reactor']
    ax2. axis('tight')
    ax2.axis('off')
    table = ax2.table(cellText = cell_text, colLabels = column_labels, loc = 'center')
    table.auto_set_font_size(False)
    table.set_fontsize(20)
    table.scale(1,4)

    fig.tight_layout(pad = 3)
    fig.savefig(save + 'Histogram.png')
    plt.close('all')
