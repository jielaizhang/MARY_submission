import os 
import sys  

json_file = sys.argv[1]

mary_path = "/home/fstars/MARY4OZ/"

mary_run_save_path = "/fred/oz100/pipes/DWF_PIPE/JSONS/PAST_JOBS/"+ json_file+"/"
print('The JSON used is ' + json_file)
print('JSON file moved to: ' + mary_run_save_path)
if not os.path.exists(mary_run_save_path):
    os.makedirs(mary_run_save_path, 0o755)
else: 
    pass 

os.system('python setup_from_json.py --json_filename '+ json_file)

os.system('cp mastersystem.pro '+ mary_run_save_path+'.')
os.system('cp mary4parameters.pro ' + mary_run_save_path+'.')
os.system('cp mary4parameters_base.pro '+ mary_run_save_path+'.')
os.system('cp controlccd.py '+ mary_run_save_path +'.')
os.system('cp list_images_tot.txt '+mary_run_save_path+'.')
os.system('cp list_images_temp.txt '+mary_run_save_path+'.')

os.system('mv mastersystem.pro '+ mary_path+'.')
os.system('mv mary4parameters.pro ' + mary_path+'.')
os.system('mv mary4parameters_base.pro '+ mary_path+'.')
os.system('mv controlccd.py '+ mary_path +'.')
os.system('mv list_images_tot.txt '+mary_path+'.')
try: 
    os.system('mv list_images_temp.txt '+mary_path+'.')
except: 
    pass

os.system('idl /home/fstars/MARY4OZ/mary4qsub.pro')

os.system('mv '+json_file+' OLD_JSONS/.')
