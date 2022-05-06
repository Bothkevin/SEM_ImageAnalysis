class Location:

    def SEM_path():
        path = r'.\SEM_EXAMPLE\\'
        return path

    def SEM_folder():
        folders = [r'Ladybug\\',r'Flower-like\\',r'Antenna-reactor\\',r'Mixed_before\\','Mixed After\\']
        return folders

    def SEM_scale():
        SetScale = [[300,300,500,300],
                    [300,300,500,500],
                    [500,400,500,500],
                    [500,1000,1000],
                    [400,500,300,300,400,400]]
        return SetScale

    def SEM_highIntensity():
        Intensity1 = [[0.75,0.75,0.8,0.8],
                    [0.7,0.75,0.7,0.8],
                    [0.75,0.8,0.8,0.7],
                    [0.7,0.75,0.75],
                    [0.7,0.75,0.8,0.85,0.9,0.73]]
        return Intensity1
    def SEM_mediumIntensity():
        Intensity2 = [[0.69,0.69,0.75,0.7],
                        [0.65,0.65,0.6,0.75],
                        [0.65,0.69,0.69,0.6],
                        [0.6,0.7,0.7],
                        [0.65,0.72,0.72,0.78,0.8,0.7]]
        return Intensity2
    def SEM_ignoreIntensity():
        Intensity3 = [[1.0,1.0,1.0,1.0],
                    [1.0,1.0,1.0,1.0],
                    [1.0,1.0,1.0,1.0],
                    [1.0,1.0,1.0],
                    [1.0,1.0,1.0,1.0,1.0,1.0]]
        return Intensity3

    def SEM_ScaleUnit():
        SetScaleUnit ='nm'
        return SetScaleUnit

    def SetColor():
        color = [(0,206,209,255),(255,223,0,255)]
        return color

    def MinDistance():
        MinDis = 15
        return MinDis
