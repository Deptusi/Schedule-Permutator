import sys,os
sys.path.append(os.getcwd())
import mainPermutator
import random,itertools,pandas,names


def calculateSchedules():
    week=list(getWeekHours())
    classes={
        'Calculo':createClass('Calculo','Blue',weekHours=week),
        'Literatura':createClass('Literatura','Red',weekHours=week),
        'Biologia':createClass('Biologia','Green',weekHours=week),
        'Mecanica':createClass('Mecanica','Orange',weekHours=week),
        
    }
    return classes
    v=mainPermutator.permutateSchedules(classes)
    # for i,j in enumerate(v):
    #     print(i,j.weekranges)
    # mainPermutator.buildDFfromWeekSchedule(v[0])
def multipleGeneration(iteration=10):
    for i in range(iteration):
        df=generateDataInCSV()
        df.to_csv(f'dataTesting\\data{i}.csv',index=None)
def generateDataInCSV():
    week=list(getWeekHours())
    classes={
        'Calculo':createClass('Calculo','Blue',weekHours=week),
        'Literatura':createClass('Literatura','Red',weekHours=week),
        'Biologia':createClass('Biologia','Green',weekHours=week),
        'Mecanica':createClass('Mecanica','Orange',weekHours=week),
        'Calculo2':createClass('Calculo2','Blue',weekHours=week),
        'Literatura2':createClass('Literatura2','Red',weekHours=week),
        'Biologia2':createClass('Biologia2','Green',weekHours=week),
        'Mecanica2':createClass('Mecanica2','Orange',weekHours=week),
    }
    counters={name:0 for name in classes.keys()}
    v=1
    saveData=[]
    for item in classes.values():
        v*=(len(item.schedules.values()))
        for code,c in item.schedules.items():
            saveData.append(
                {
                    'className':item.name,
                    'professorName':c.professorName,
                    'classColor':item.color,
                    'classCode':code,
                    'classSchedule':[sch for sch in c.weekranges],
                    }
            )
    df=pandas.DataFrame(saveData)
    return df
    df.to_csv('dataTest.csv',index=False)
    
    # for i,j in enumerate(list(itertools.product(
    #     *[c.schedules.values() for c in classes.values()],repeat=1))):
    #     print(list(map(lambda x: x.weekranges[0],j)))

def getWeekHours():
    for i in range(1,8):
        for hour in range(0,24):
            startHour=hour
            endHour=f'{i}T{hour+1}' if hour+1 != 24 else f'{i+1}T00'
            yield (f'{i}T{startHour}:00:00',f'{endHour}:00:00')
def createSchedule(professorName:str,className:str,classColor:str,hours:int,weekHours:list):
    profClass=mainPermutator.ProfessorSchedule(professorName)
    copyWeekHours=[mainPermutator.DetailedTimeRange(
        className,classColor,professorName,profClass.classCode,hour[0],hour[1]
    ) for hour in weekHours]
    for i in range(hours):
        hourClass=random.choice(copyWeekHours)
        copyWeekHours.remove(hourClass)
        profClass.insertTimeRange(hourClass)
    return profClass
def createClass(className:str,classColor:str='',weekHours:list=[]):
    weekClass=mainPermutator.ClassDetails(className,colorate())
    hoursCount=random.randint(2,5)
    for i in range(random.randint(3,12)):
        sch=weekClass.addSchedule(createSchedule(
            names.get_full_name(),className,colorate(),hoursCount,weekHours))
    return weekClass

def colorate():
    return [
        random.randint(0,255),
        random.randint(0,255),
        random.randint(0,255),
        random.randint(0,255),
    ]
if __name__=='__main__':
    # calculateSchedules()
    # multipleGeneration()
    df=generateDataInCSV()
    df.to_csv(f'dataTesting\\dataHUGE.csv',index=None)