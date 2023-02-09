

""" Define colors """
from kivy.utils import get_color_from_hex
__themeDict__={
        "DarkTheme":{
            "Primary"           :"#002c77",
            "PrimaryLight"      :"#4554a7",
            "PrimaryDark"       :"#00034a",
            "Secundary"         :"#009de0",
            "SecundaryLight"    :"#62ceff",
            "SecundaryDark"     :"#006fae",
            "PrimaryText"       :"#ffffff",
            "SecundaryText"     :"#000000"
            }
        }
__colors__=__themeDict__
for key,values in __themeDict__.items():
    for name, code in values.items():
        __colors__[key][name]=get_color_from_hex(code)
    
import os,json,tempfile,datetime
__defaultFolderPicker__=os.getcwd()
__logFolder__          =os.path.join(__defaultFolderPicker__,'logs')
if not os.path.isdir(__logFolder__):
    os.makedirs(__logFolder__)
__TODAY__       =datetime.datetime.today()


from supportFiles.privateLogger import privateLogger
logger=privateLogger(Folder='logs',DateRef=True)

__instrucctionsPaths__={
    'PDF':'supportFiles\Instructivo SchedulePermutator.pdf',
    'MP4':'supportFiles\Instructivo SchedulePermutator.mp4'
}

""" Borrar archivos temporales """
def clearFolderFiles(folderFull:str):
    for rRoot,rFolders,rFiles in os.walk(folderFull):
        for file in rFiles:
            fileFull=os.path.join(rRoot,file)
            try:
                os.remove(fileFull)
            except Exception as e:
                continue
def clearDirectory(folderFull:str):
    try:
        os.removedirs(folderFull)
    except Exception as e:
        pass
def clearMSGfiles(files,root):
    for file in files:
        folderFull=os.path.join(root,file)
        name,ext=os.path.splitext(folderFull)
        if ext=='.msg':
            try:
                os.remove(folderFull)
            except:
                continue
for root,folders,files in os.walk(tempfile.gettempdir()):
    for folder in folders:
        if 'SchedulePermutator' in folder:
            folderFull=os.path.join(root,folder)
            logger.info(f'Borrando anterior carpeta temporal [{folderFull}]')
            clearFolderFiles(folderFull=folderFull)
            clearDirectory(folderFull=folderFull)
    clearMSGfiles(files,root)

__defaultDir__          =tempfile.mkdtemp(prefix='SchedulePermutator ')
logger.info(f'Default Folder: [{__defaultDir__}]')
