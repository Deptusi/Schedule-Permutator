import datetime, random, itertools, pandas
from datetimerange import DateTimeRange
from calendar_view.core.event import Event
from calendar_view.core.event import EventStyle
from calendar_view.calendar import Calendar
from calendar_view.config import style
from calendar_view.core import data
import config
from tqdm import tqdm
logger=config.logger
style.hour_height=150
style.event_title_font.size=12
style.event_notes_font.size=12
style.image_bg=(255,255,255,245)

""" Define classes """

class DetailedTimeRange(DateTimeRange):
    def __init__(
        self,
        className:str,classColor:str,professorName:str,classCode:str,
        start_datetime: datetime.datetime | str | None = ..., end_datetime: datetime.datetime | str | None = ..., start_time_format: str = '%dT%H:%M:%S', end_time_format: str = '%dT%H:%M:%S') -> None:
        
        super().__init__(start_datetime, end_datetime, start_time_format, end_time_format)
        self.className=className
        self.classColor=classColor
        self.professorName=professorName
        self.classCode=classCode
    def getCalendarEvent(self) -> Event:
        return Event(
            title=self.className,
            notes=self.getNotes(),
            day_of_week=int(self.start_datetime.strftime('%d'))-1,
            start=self.start_datetime.strftime('%H:%M'),
            end=self.end_datetime.strftime('%H:%M'),
            style=EventStyle(event_fill=self.classColor)
        )
    def getNotes(self) -> str:
        if self.classCode=='' and self.professorName=='':
            return ''
        elif self.professorName=='':
            return self.classCode
        elif self.classCode=='':
            return self.professorName
        else:
            return f'{self.professorName} - {self.classCode}'

class WeekSchedule():
    def __init__(self):
        self.weekranges=[]
    def insertTimeRange(self,newTimeRange:DetailedTimeRange):
        for timeRange in self.weekranges:
            if newTimeRange.is_intersection(timeRange):
                return False
        self.weekranges.append(newTimeRange)
        return True
    def getWeekStartEndHours(self):
        startHours=[int(timeRange.start_datetime.strftime('%H')) for timeRange in self.weekranges]
        endHours  =[int(timeRange.end_datetime.strftime('%H')) for timeRange in self.weekranges]
        minHour,maxHour=min(startHours),max(endHours)+1
        return f'{minHour} - {maxHour}'
    def getEventsFromSchedule(self):
        for timeRange in self.weekranges:
            yield timeRange.getCalendarEvent()
    def generateImageFromSchedule(self,savePath:str,title:str=None):
        config = data.CalendarConfig(
            dates='Mo - Su',
            hours=self.getWeekStartEndHours(),
            show_date=False,
            show_year=False,
            title=title
        )
        events=self.getEventsFromSchedule()
        calendar = Calendar.build(config)
        calendar.add_events(events)
        calendar.save(savePath)

class ProfessorSchedule(WeekSchedule):
    def __init__(self,professorName:str,classCode:str=''):
        super().__init__()
        self.professorName=professorName
        self.classCode=classCode
class ClassDetails():
    def __init__(self,name:str,color:str) -> None:
        self.name=name
        self.color=color
        self.schedules={}
    def addSchedule(self,schedule:ProfessorSchedule,classCode:str=''):
        while classCode=='' or classCode in self.schedules.keys():
            classCode=f'AUTOCODE-{len(self.schedules)}.{random.randint(1,999999)}'
        schedule.classCode=classCode
        self.schedules[classCode]=schedule
        return schedule

""" Define Functions """
def mergeSchedules(scheduleList:list[ProfessorSchedule]):
    newSchedule=WeekSchedule()
    for schedule in scheduleList:
        for timeRange in schedule.weekranges:
            validSchedule=newSchedule.insertTimeRange(timeRange)
            if not validSchedule:
                return False
    newSchedule.weekranges.sort(key=lambda x: x.start_datetime)
    return newSchedule
def permutateSchedules(classes:dict[str:ClassDetails]):
    permutatedList=(itertools.product(
        *[classSchedule.schedules.values() for classSchedule in classes.values()],
        repeat=1
    ))

    permutatedLen=1
    for classSchedule in classes.values():
        permutatedLen*=len(classSchedule.schedules)
    iterCount,totalCount,validCount=0,permutatedLen,0
    
    for scheduleList in permutatedList:
        iterCount+=1
        logger.info(f'Calculating ({iterCount}/{totalCount}): {validCount}')
        try:
            mergedSchedule=mergeSchedules(scheduleList)
            if mergedSchedule!=False:
                validCount+=1
                yield mergedSchedule    
        except:
            continue
""" Execute """
if __name__=='__main__':
    pass