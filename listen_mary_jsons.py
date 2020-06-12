import inotify.adapters 
import os 

#i =inotify.adapters.InotifyTree('/fred/oz100/pipes/DWF_PIPE/JSONS')
notifier = inotify.adapters.Inotify()
notifier.add_watch('/fred/oz100/pipes/DWF_PIPE/JSONS/')

for event in notifier.event_gen():
    if event is not None:
        print(event)
        #if 'IN_CREATE' in event[1]:
            #print(event)
   
            #filename = event[3]
            #print(filename)
            #if filename.endswith('.json'):
             #   os.system('python submit_mary_job.py ' + str(event[3]))
