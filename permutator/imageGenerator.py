from mainPermutator import *

from calendar_view.core.event import Event
from calendar_view.core.event import EventStyle




    pass
def getEventsFromSchedule(schedule:WeekSchedule):
    for timeRange in schedule.weekranges:
        yield timeRange.getCalendarEvent()