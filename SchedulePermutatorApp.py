import os,pandas,warnings,tempfile,json,re,PIL.Image
from alive_progress import alive_bar
warnings.filterwarnings(action='ignore')

from kivy.app                                   import App
from kivy.uix.gridlayout                        import GridLayout
from kivy.uix.boxlayout                         import BoxLayout
from kivy.uix.textinput                         import TextInput
from kivy.uix.button                            import Button
from kivy.uix.label                             import Label
from kivy.uix.colorpicker                       import ColorPicker
from kivy.uix.anchorlayout                      import AnchorLayout      
from kivy.uix.spinner                           import Spinner
from kivy.core.window                           import Window
from kivy.lang                                  import Builder
from kivy.uix.popup                             import Popup
from kivy.uix.scrollview                        import ScrollView
from kivy.uix.filechooser                       import FileChooserListView


import config
logger=config.logger

from permutator.mainPermutator import *


""" Define Classes """
class mainSchedulePermutatorApp(App):
    def build(self):
        Window.clearcolor=(config.__colors__["DarkTheme"]["Primary"])
        self.root=Builder.load_file('supportFiles\AppSchedulePermutator.kv')
        return SchedulePermutatorApp()

class SchedulePermutatorApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spacing= '10dp'
        self.padding= '5dp'
        self.orientation='vertical'
        
        self.subjectsGrid=subjectsGrid()

        self.add_widget(logoLayout())
        self.add_widget(ExecuteRow(self.subjectsGrid))
        self.add_widget(self.subjectsGrid)
        
class ColorPopup(Popup):
    def __init__(self, callerWidget:Button,**kwargs):
        super().__init__(**kwargs)
        self.title='Color'
        self.caller=callerWidget
        self.Box=BoxLayout(orientation='vertical')
        self.colorPicker=ColorPicker()
        self.execute=Button(text='Continue',size_hint_y=0.1)
        self.execute.bind(on_release=self.dismiss)

        self.Box.add_widget(self.colorPicker)
        self.Box.add_widget(self.execute)
        self.add_widget(self.Box)
    def on_dismiss(self):
        color=self.colorPicker.color
        color[3]=1
        self.caller.background_color=color
        return super().on_dismiss()

class HoursRow(BoxLayout):
    def __init__(self, weekday=1,start:str='',end:str='',**kwargs):
        super().__init__(**kwargs)
        self.orientation='horizontal'

        self.days={
            'MON':1,'TUE':2,'WED':3,'THU':4,'FRI':5,'SAT':6,'SUN':7
        }
        self.revesedDays={value:key for key,value in self.days.items()}

        self.clearBTN=Button(text='X',size_hint_x=0.1,background_color=[1,0,0,1])
        self.weekSpinner=Spinner(values=self.days.keys(),size_hint_x=0.25)
        self.weekSpinner.text=self.revesedDays[weekday]
        self.startInput=TextInput(text=start,multiline=False)
        self.endInput=TextInput(text=end,multiline=False)
        self.startInput.bind(focus=self.on_enter)
        self.endInput.bind(focus=self.on_enter)
        self.clearBTN.bind(on_release=self.destroyRow)
        

        self.add_widget(self.clearBTN)
        self.add_widget(self.weekSpinner)
        self.add_widget(self.startInput)
        self.add_widget(self.endInput)
    def getStartTime(self) -> str:
        return f'{self.days[self.weekSpinner.text]}T{self.startInput.text}'
    def getEndTime(self) -> str:
        return f'{self.days[self.weekSpinner.text]}T{self.endInput.text}'
    def destroyRow(self,instance):
        self.parent.remove_widget(self)
    def on_enter(self,instance,focus):
        if not focus:
            if not re.fullmatch('^(0[0-9]|1[0-9]|2[0-3]|[0-9]):[0-5][0-9]$',instance.text):
                instance.text=''
class HoursMenu(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout=GridLayout(cols=1, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        
        self.timeAddBTN=Button(text='+',size_hint_y=None)
        self.timeAddBTN.bind(on_release=self.addTimeRow)
        self.addTimeRow()
        self.add_widget(self.layout)
    def addTimeRow(self,instance=None,hour=None):
        if hour==None:
            hour=HoursRow(size_hint_y=None)
        self.layout.add_widget(hour)
        self.placeTimeAddButton()
    def placeTimeAddButton(self,instance=None):
        try:
            self.layout.remove_widget(self.timeAddBTN)
        except:
            pass
        self.layout.add_widget(self.timeAddBTN)
class HoursMenuPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.Box=BoxLayout(orientation='vertical')
        self.grid=HoursMenu()
        self.continueBTN=Button(text='Continue',size_hint_y=0.1)
        self.continueBTN.bind(on_release=self.dismiss)

        self.add_widget(self.Box)
        self.buildTopRow()
        self.Box.add_widget(self.grid)
        self.Box.add_widget(self.continueBTN)
    def buildTopRow(self):
        self.TopRow=BoxLayout(orientation='horizontal',size_hint_y=0.1)
        self.TopRow.add_widget(Label(text='Weekday',size_hint_x=0.2))
        self.TopRow.add_widget(Label(text='StartTime (HH:MM)',size_hint_x=0.4))
        self.TopRow.add_widget(Label(text='EndTime (HH:MM)',size_hint_x=0.4))
        self.Box.add_widget(self.TopRow)

class SchedulesRow(BoxLayout):
    def __init__(self,subject:str,subjectColor, **kwargs):
        super().__init__(**kwargs)
        self.orientation='horizontal'
        self.subject=subject
        self.subjectColor=subjectColor

        # Generar widgets
        self.nameInput      =TextInput(text='')
        self.codeInput      =TextInput(text='')
        self.hoursMenu      =HoursMenuPopup()
        self.classesBTN     =Button(text='+',size_hint_x=0.3)
        self.classesBTN.bind(on_release=self.openHoursMenu)
        self.clearBTN       =Button(text='X',size_hint_x=0.1,background_color=[1,0,0,1])
        self.clearBTN.bind(on_release=self.destroyRow)

        self.add_widget(self.clearBTN)
        self.add_widget(self.nameInput)
        self.add_widget(self.codeInput)
        self.add_widget(self.classesBTN)
    def destroyRow(self,instance):
        self.parent.remove_widget(self)
    def openHoursMenu(self,instance=None):
        self.subject=self.parent.parent.parent.parent.parent.parent.title
        self.subjectColor=self.parent.parent.parent.parent.parent.parent.separator_color
        self.hoursMenu.title=f'{self.subject}: {self.nameInput.text} - {self.codeInput.text}'
        self.hoursMenu.separator_color=self.subjectColor
        self.hoursMenu.open()
class SchedulesMenu(ScrollView):
    def __init__(self, subject:str,subjectColor,**kwargs):
        super().__init__(**kwargs)
        self.subject=subject
        self.subjectColor=subjectColor
        self.layout=GridLayout(cols=1, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        
        self.scheduleAddBTN=Button(text='+',size_hint_y=None)
        self.scheduleAddBTN.bind(on_release=self.addScheduleRow)
        self.addScheduleRow()
        self.add_widget(self.layout)
    def addScheduleRow(self,instance=None,row=None):
        if row==None:
            row=SchedulesRow(self.subject,self.subjectColor,size_hint_y=None)
        self.layout.add_widget(row)
        self.placeScheduleAddButton()
    def placeScheduleAddButton(self,instance=None):
        try:
            self.layout.remove_widget(self.scheduleAddBTN)
        except:
            pass
        self.layout.add_widget(self.scheduleAddBTN)
class SchedulesMenuPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.Box=BoxLayout(orientation='vertical')
        self.grid=SchedulesMenu(self.title,self.separator_color)
        self.continueBTN=Button(text='Continue',size_hint_y=0.1)
        self.continueBTN.bind(on_release=self.dismiss)

        self.add_widget(self.Box)
        self.buildTopRow()
        self.Box.add_widget(self.grid)
        self.Box.add_widget(self.continueBTN)
    def buildTopRow(self):
        self.TopRow=BoxLayout(orientation='horizontal',size_hint_y=0.1)
        self.TopRow.add_widget(Label(text='Professor',size_hint_x=0.4))
        self.TopRow.add_widget(Label(text='Code',size_hint_x=0.4))
        self.Box.add_widget(self.TopRow)
    
class subjectRow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y=None
        self.height=50
        self.orientation='horizontal'

        # Generar widgets
        self.nameInput      =TextInput(text='')
        self.colorBTN       =Button(text='Color',size_hint_x=0.2,background_normal='supportFiles\Solid_white.svg.png',color=[0,0,0,1])
        self.colorPoper     =ColorPopup(self.colorBTN)
        self.colorBTN.bind(on_release=self.changeColor)
        self.schedulesMenu  =SchedulesMenuPopup()
        self.classesBTN     =Button(text='+',size_hint_x=0.3)
        self.classesBTN.bind(on_release=self.openSchedulesMenu)
        self.clearBTN       =Button(text='X',size_hint_x=0.1,background_color=[1,0,0,1])
        self.clearBTN.bind(on_release=self.destroyRow)
        

        # Agregar widgets
        self.add_widget(self.clearBTN)
        self.add_widget(self.nameInput)
        self.add_widget(self.colorBTN)
        self.add_widget(self.classesBTN)
    def destroyRow(self,instance):
        self.parent.remove_widget(self)
    def changeColor(self,instance=None):
        self.colorPoper.open()
    def openSchedulesMenu(self,instance=None):
        self.schedulesMenu.title=self.nameInput.text
        self.schedulesMenu.separator_color=self.colorPoper.colorPicker.color
        self.schedulesMenu.open()
class subjectsGrid(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint=(1, None)
        self.size=(Window.width, Window.height*4/5)
        self.layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.subjectAddBTN=Button(text='+',height=50,size_hint_y=None)
        self.subjectAddBTN.bind(on_release=self.addSubjetRow)
        self.getRows()
    def getRows(self) -> list[subjectRow]:
        self.rows=[]
        for i in range(2):
            row=subjectRow()
            self.rows.append(row)
            self.layout.add_widget(row)
        self.placeSubjectAddButton()
        self.add_widget(self.layout) 
    def placeSubjectAddButton(self):
        try:
            self.layout.remove_widget(self.subjectAddBTN)
        except:
            pass
        self.layout.add_widget(self.subjectAddBTN)
    def addSubjetRow(self,instance=None,subject=subjectRow()):
        self.layout.add_widget(subject)
        self.placeSubjectAddButton()
    
class ExecuteRow(BoxLayout):
    def __init__(self, subjects,**kwargs):
        super().__init__(**kwargs)

        self.subjectGrid=subjects

        self.loadBTN=Button(text='Load CSV')
        self.exportBTN=Button(text='Export CSV')
        self.calculateBTN=Button(text='Run Permutation')

        self.loadBTN.bind(on_release=self.selectCSV)
        self.exportBTN.bind(on_release=self.selectSaveCSV)
        self.calculateBTN.bind(on_release=self.SavePDFpermutations)

        self.add_widget(self.loadBTN)
        self.add_widget(self.exportBTN)
        self.add_widget(Label())
        self.add_widget(self.calculateBTN)
    def readGUIdata(self,instance=None):
        self.classes={}
        for subject_row in self.subjectGrid.layout.children:
            if type(subject_row)!=subjectRow:
                continue
            className   =subject_row.nameInput.text
            classColor  =tuple([int(255*color) for color in subject_row.colorPoper.colorPicker.color])
            details     =ClassDetails(className,classColor)
            for professor_row in subject_row.schedulesMenu.grid.layout.children:
                if type(professor_row)!=SchedulesRow:
                    continue
                classCode=professor_row.codeInput.text
                professorName=professor_row.nameInput.text
                schedule=ProfessorSchedule(professorName,classCode)
                for hour_row in professor_row.hoursMenu.grid.layout.children:
                    if type(hour_row)!=HoursRow:
                        continue
                    try:
                        timeRange=DetailedTimeRange(
                            className,classColor,professorName,classCode,
                            hour_row.getStartTime(),hour_row.getEndTime()
                        )
                        schedule.insertTimeRange(timeRange)
                    except:
                        pass
                if len(schedule.weekranges)>0:
                    details.addSchedule(schedule,classCode)
            if len(details.schedules)>0:
                self.classes[subject_row.nameInput.text]=details
    
    def SavePDFpermutations(self,instance=None):
        fileSaver(self.generatePDF,['*.pdf']).open() 
    def calculatePermutations(self):
        self.readGUIdata()
        if len(self.classes)==0:
            return
        self.permutations=list(permutateSchedules(self.classes))
        validCount,validTotal=1,len(self.permutations)
        for permutation in self.permutations:
            try:
                fileName=os.path.join(config.__defaultDir__,f'schedule_{validCount}.png')
                permutation.generateImageFromSchedule(fileName,f'Horario {validCount}')
                logger.info(f'Generating image {validCount}/{validTotal}')
                validCount+=1
                yield fileName
            except Exception as e:
                logger.exception(e)
    def generatePDF(self,savePath):
        imagesPaths=self.calculatePermutations()
        images=[PIL.Image.open(file).convert('RGB') for file in imagesPaths]
        images[0].save(
            savePath,save_all=True,append_images=images[1:]
        )

    def selectCSV(self,instance=None):
        fileSelector(self.loadCSV).open()
    def loadCSV(self,csvPath:str):
        self.loadData(csvPath)
        self.subjectGrid.layout.clear_widgets()
        for fullClass in self.classes.values():
            # fullClass=ClassDetails()
            subject=subjectRow()
            subject.nameInput.text=fullClass.name
            subject.colorPoper.colorPicker.set_color([color/255 for color in fullClass.color])
            buttonColor=subject.colorPoper.colorPicker.color
            buttonColor[3]=1
            subject.colorBTN.background_color=buttonColor
            subject.schedulesMenu.grid.layout.clear_widgets()
            for schedule in fullClass.schedules.values():
                # schedule=ProfessorSchedule()
                schedule_row=SchedulesRow(fullClass.name,fullClass.color,size_hint_y=None)
                schedule_row.nameInput.text=str(schedule.professorName)
                schedule_row.codeInput.text=str(schedule.classCode)
                schedule_row.hoursMenu.grid.layout.clear_widgets()
                for hours in schedule.weekranges:
                    # hours=DetailedTimeRange()
                    hour_row=HoursRow(
                        weekday=hours.start_datetime.day,
                        start=hours.start_datetime.strftime('%H:%M'),
                        end=hours.end_datetime.strftime('%H:%M'),
                        size_hint_y=None
                    )
                    schedule_row.hoursMenu.grid.addTimeRow(hour=hour_row)
                subject.schedulesMenu.grid.addScheduleRow(row=schedule_row)
            self.subjectGrid.addSubjetRow(subject=subject)
        pass
    def loadData(self,path:str='dataTesting\data0.csv'):
        df=pandas.read_csv(path,dtype=str)
        df.loc[:,'classColor']=df['classColor'].str.replace('[\[\]\s\(\)]','',regex=True).str.split(',').map(lambda x: tuple(map(int,x)))
        self.classes={}
        for index,row in df.drop_duplicates(subset=['className']).iterrows():
            self.classes[row['className']]=ClassDetails(row['className'],row['classColor'])
        for index,row in df.iterrows():
            schedule=ProfessorSchedule(row['professorName'],row['classCode'])
            timesList=list(row['classSchedule'].replace('[','').replace(']','').replace(' ','').split(','))
            for timeName in timesList:
                times=timeName.split('-')
                timeRange=DetailedTimeRange(
                    row['className'],row['classColor'],row['professorName'],row['classCode'],
                    times[0],times[1]
                )
                schedule.insertTimeRange(timeRange)
            self.classes[row['className']].addSchedule(schedule,row['classCode'])
    
    def selectSaveCSV(self,instance=None):
        fileSaver(self.exportCSV,['*.csv']).open() 
    def exportCSV(self,savePath=None):
        self.readGUIdata()
        saveData=[]
        for item in self.classes.values():
            for code,c in item.schedules.items():
                saveData.append(
                    {
                        'className'     :item.name,
                        'professorName' :c.professorName,
                        'classColor'    :item.color,
                        'classCode'     :code,
                        'classSchedule' :[sch for sch in c.weekranges],
                        })
        df=pandas.DataFrame(saveData)
        df.to_csv(savePath,index=None)
""" Define Support Classes """
class fileSelector(Popup):
    def __init__(self,callerFunction, **kwargs):
        super().__init__(**kwargs)

        self.calledFunction=callerFunction

        self.Box=BoxLayout(orientation='vertical')
        self.add_widget(self.Box)

        self.chooser=FileChooserListView(filters=['*.csv'],multiselect=False)
        self.chooser.path=os.getcwd()

        buttons=BoxLayout(orientation='horizontal',size_hint_y=0.1)
        self.selectBTN=Button(text='Select')
        self.cancelBTN=Button(text='Cancel')
        buttons.add_widget(self.cancelBTN)
        buttons.add_widget(self.selectBTN)
        self.cancelBTN.bind(on_release=self.dismiss)
        self.selectBTN.bind(on_release=self.selectFile)

        self.Box.add_widget(self.chooser)
        self.Box.add_widget(buttons)
    def selectFile(self,instance=None):
        print(self.chooser.selection[0])
        self.calledFunction(self.chooser.selection[0])
        return super().dismiss()
class fileSaver(Popup):
    def __init__(self,callerFunction,filters:list[str], **kwargs):
        super().__init__(**kwargs)
        self.calledFunction=callerFunction

        self.Box=BoxLayout(orientation='vertical')
        self.add_widget(self.Box)

        self.inputName=TextInput(multiline=False,size_hint_y=0.1)

        self.chooser=FileChooserListView(filters=filters,multiselect=False)
        self.chooser.path=os.getcwd()

        buttons=BoxLayout(orientation='horizontal',size_hint_y=0.1)
        self.selectBTN=Button(text='Save')
        self.cancelBTN=Button(text='Cancel')
        buttons.add_widget(self.cancelBTN)
        buttons.add_widget(self.selectBTN)
        self.cancelBTN.bind(on_release=self.dismiss)
        self.selectBTN.bind(on_release=self.selectFile)

        self.Box.add_widget(self.inputName)
        self.Box.add_widget(self.chooser)
        self.Box.add_widget(buttons)
    def selectFile(self,instance=None):
        self.calledFunction(self.verifyFile())
        return super().dismiss()
    def verifyFile(self):
        fileName=os.path.join(self.chooser.path,self.inputName.text)
        path,ext=os.path.splitext(fileName)
        fileName=path+self.chooser.filters[0].replace('*','')
        return fileName



class logoLayout(AnchorLayout):
    def popInstruccions(self):
        showInstruccions().open()
    def popLog(self):
        popLog()
    pass
class MyLabel(Label):
   def on_size(self, *args):
      self.text_size = self.size
class showInstruccions(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title='Instrucciones'
        self.separator_color=config.__colors__['DarkTheme']['PrimaryDark']
        self.size_hint=(1,0.8)
        self.auto_dismiss=True
        self.box=BoxLayout(orientation='vertical')
        self.add_widget(self.box)
        self.pdfInstruccions=Button(text='Abrir Instrucciones en PDF')
        self.pdfInstruccions.bind(on_press=self.pdf)
        self.box.add_widget(self.pdfInstruccions)
        self.videoInstruccions=Button(text='Mostrar video explicativo')
        self.videoInstruccions.bind(on_press=self.video)
        self.box.add_widget(self.videoInstruccions)
    def pdf(self,event):
        try:
            os.startfile(config.__instrucctionsPaths__['PDF'])
        except:
            logger.error('Instrucciones no encontradas')
        self.dismiss()
    def video(self,event):
        try:
            os.startfile(config.__instrucctionsPaths__['MP4'])
        except:
            logger.error('Instrucciones no encontradas')
        self.dismiss()
class ErrorLog(Popup):
    def __init__(self,error, **kwargs):
        super().__init__(**kwargs)
        self.title='Error de ejecucción'
        self.separator_color=config.__colors__['DarkTheme']['PrimaryDark']
        self.size_hint=(1,0.8)
        self.auto_dismiss=True
        self.box=BoxLayout(orientation='vertical')

        self.ErrorMessage=Label(text=str(error),size_hint_y=0.8)
        self.Actionbox=BoxLayout(orientation='horizontal',size_hint_y=0.2)
        self.popBtn=Button(text='Revisar LOG')
        self.popBtn.bind(on_release=self.popLog)
        self.disBtn=Button(text='Ignorar')
        self.disBtn.bind(on_release=self.autoDismiss)

        self.Actionbox.add_widget(self.disBtn)
        self.Actionbox.add_widget(self.popBtn)

        self.box.add_widget(self.ErrorMessage)
        self.box.add_widget(self.Actionbox)

        self.add_widget(self.box)
    def popLog(self,instance=None):
        try:
            os.startfile(logger.handlers[1].baseFilename)
        except:
            logger.error('No se pudo abrir el log')
        finally:
            self.dismiss()
    def autoDismiss(self,instance=None):
        self.dismiss()

""" Define Functions """
def mainSchedulePermutatorRun():
    # Window.maximize()
    app=mainSchedulePermutatorApp()
    app.run()
def popLog():
        try:
            os.startfile(logger.handlers[1].baseFilename)
        except:
            logger.error('No se pudo abrir el log')


""" Execution """
if __name__=='__main__':
    mainSchedulePermutatorRun()