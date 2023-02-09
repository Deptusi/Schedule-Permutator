import mainPermutator,tester_Permutator
import pandas, dataframe_image

""" Define functions """
def readData(path:str):
    df=pandas.read_csv(path)
    classes={}
    df.loc[:,'classColor']=df['classColor'].str.replace(
        '[','').str.replace(']','').str.replace(' ','').str.split(',')
    
    df.loc[:,'classColor']=df['classColor'].apply(lambda x: tuple(map(int,x)))
    print(df['classColor'])
    for index,row in df.drop_duplicates(subset=['className']).iterrows():
        classes[row['className']]=mainPermutator.ClassDetails(row['className'],row['classColor'])
    for index,row in df.iterrows():
        schedule=mainPermutator.ProfessorSchedule(row['professorName'],row['classCode'])
        timesList=list(row['classSchedule'].replace('[','').replace(']','').replace(' ','').split(','))
        for timeName in timesList:
            times=timeName.split('-')
            timeRange=mainPermutator.DetailedTimeRange(
                row['className'],row['classColor'],row['professorName'],row['classCode'],
                times[0],times[1]
            )
            schedule.insertTimeRange(timeRange)
        classes[row['className']].addSchedule(schedule,row['classCode'])
    return classes

def testPermutation(classes:dict[str:mainPermutator.ClassDetails]):
    v=mainPermutator.permutateSchedules(classes)
    # mainPermutator.buildDFfromWeekSchedule(v)
    print()
    for index, schedule in enumerate(v):
        # print(f'Building {index}')
        # print(schedule.weekranges)
        schedule.generateImageFromSchedule(f'dataTesting\\images\\schedule_{index+1}.png',f'Horario {index+1}')
        # df=mainPermutator.buildDFfromWeekSchedule(schedule)
        # # df.to_html('test.html')
        # dataframe_image.export(df,f'dataTesting\\images\\schedule_{index+1}.png')
        # dataframe_image.export(d)

""" Execute """
if __name__=='__main__':
    data=readData('dataTesting\\data0.csv')
    # print(data)
    testPermutation(data)