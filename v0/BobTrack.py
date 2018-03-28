import serial
import serial.tools.list_ports
import time
import json
import copy
import threading


# defines
timer_switch_enabled = True # camera will only switch automatically when this is set to true. Otherwise when endpoint barrier is passed.
waiting_time_camera_endpoint = 2.0 # when the checkpoint is passed, the timer will be started. After this time in s, the camera will be switched to the endpoint camera


# global Variables 
team_name = ''
dict_runs = {'run_counter': 0, 'run_nr':[], 'team_name':[], 'run_time':[], 'checkpoint_time':[]} # information about all runs (saved in JSON)
dict_run = {'run_nr':0, 'team_name':'', 'run_time':0, 'checkpoint_time':0} # information for only one run







def show_camera_start():
    global dict_run
    # show camera start and make overlay with dict_run['team_name']
    print("camera start")

def show_camera_checkpoint():
    global dict_run
    # show camera start and make overlays with dict_run['team_name'] and dict_run['checkpoint_time']
    print("camera checkpoint")


def show_camera_endpoint_real(_rank):
    global dict_run
    # show camera start and make overlays with dict_run['team_name'], dict_run['run_time'], and dict_run['difference_to_first']

    #"{0:.3f}".format(dict_run['run_time'])
    print("camera endpoint", _rank)


def show_camera_endpoint_timer():
    global dict_run
    # show camera start and make overlays with dict_run['team_name'], dict_run['run_time'], and dict_run['difference_to_first']
    print("camera endpoint")










# Displays the best players on the terminal.
# How many places have to be shown are set using _show_nr.
def show_ranking(_show_nr):

    print("\nRanking")
    
    try:
        dict_ranking = json.load(open('ranking.json'))
        
        maxLength = len(dict_ranking['team_name'])
        
        for x in range(0, min(_show_nr,maxLength)):
            print(str(x+1)+':\t',"{:<20}".format(dict_ranking['team_name'][x]), '\tbest time:', "{0:.3f}".format(dict_ranking['run_time'][x]), '\tdifference:', "{0:.3f}".format(dict_ranking['difference_to_first'][x]))
                  
        print('')

    except:
        return False    
        
    
    
# loads the runs.json with all the runs, sorts it using the run_time and restores the file in ranking.json
# Difference to the first place is also calculated in here.
def get_runtime_ranking(_team_name):
    global dict_ranking
    
    used_team_names = [] # if a team name is already in this list, it won't be in the ranking list anymore (only once per ranking list)
    
   # if a team name is already saved, do not append it again
    try:
        dict_runs = json.load(open('runs.json'))
        
        dict_ranking = {'run_nr':[], 'team_name':[], 'run_time':[], 'checkpoint_time':[], 'difference_to_first':[]} # make sure directory is empty
        fastest_run_time = min(dict_runs['run_time']) # this is the fastest time from all runs
        length = len(dict_runs['run_nr'])
        
        for x in range(0, length):
            index = dict_runs['run_time'].index(min(dict_runs['run_time']))
            
            if dict_runs['team_name'][index] not in used_team_names: # copy only to rank list, when the team isn't already in there

                # minimum runtime found, copy all corresponding values
                dict_ranking['run_nr'].append(dict_runs['run_nr'][index])
                dict_ranking['team_name'].append(dict_runs['team_name'][index])
                dict_ranking['run_time'].append(dict_runs['run_time'][index])
                dict_ranking['checkpoint_time'].append(dict_runs['checkpoint_time'][index])
                dict_ranking['difference_to_first'].append(dict_runs['run_time'][index] - fastest_run_time)
                
                used_team_names.append(dict_ranking['team_name'][-1]) # add newest entry to make only one entry
            
            # delete entries to get next place in ranking
            del dict_runs['run_nr'][index]
            del dict_runs['team_name'][index]
            del dict_runs['run_time'][index]
            del dict_runs['checkpoint_time'][index]
            
            
            
        # write ranking file    
        try:
            with open('ranking.json', 'w') as outfile:
                json.dump(dict_ranking, outfile)
        except:
            print("problems writing JSON file 'dict_ranking.json'")
                
        return dict_ranking['team_name'].index(_team_name) +1 # return actual place in the ranking

    except:
        return False
    
    

def timer_switch_endpoint_camera():
    #print("timer elapsed, show endpoint camera")
    show_camera_endpoint_timer()


    

# writes the value to the bluno
def write_to_bluno(val):
    b = bytearray()
    b.extend(map(ord, chr(val)))
    ser.write(b)
    

 
   
# Save the new collected information to the JSON file
def save_to_json():
    global dict_runs, dict_run
    
    # load JSON file if it already exists
    try:
        dict_runs = json.load(open('runs.json'))
    except:
        print('')
        
    dict_runs['run_counter'] += 1
    
    # append lists with new values
    dict_runs['run_nr'].append(dict_runs['run_counter'])
    dict_runs['team_name'].append(dict_run['team_name'])
    dict_runs['run_time'].append(dict_run['run_time'])
    dict_runs['checkpoint_time'].append(dict_run['checkpoint_time'])
    
    
    try:
        with open('runs.json', 'w') as outfile:
            json.dump(dict_runs, outfile)
    except:
        print("problems writing JSON file")
    
    
    
    
def exe_cmd_first_barrier():
    print('Started')
    
    
    
    
def exe_cmd_second_barrier():
    global dict_run
    
    show_camera_checkpoint() # checkpoint passed, switch camera
    
    if timer_switch_enabled:
        timer_endpoint_camera = threading.Timer(waiting_time_camera_endpoint,timer_switch_endpoint_camera)
        timer_endpoint_camera.start()
    
    # read the rest of the input data
    ser_in = []
    
    # wait until all the time string is received
    while (ser.inWaiting() < 4):
        time.sleep(0.005)
    
    for x in range(0, 4):
      ser_in.append(ord(ser.read()))

    checkpointTime = (ser_in[3]<<24 | ser_in[2]<<16 | ser_in[1]<<8 | ser_in[0]) / 1000000.0
    
    dict_run['checkpoint_time'] = checkpointTime
    
    print('Checkpoint at:', checkpointTime, 's')
    
    
    
    
def exe_cmd_third_barrier():
    global team_name, dict_run
    
    
    # read the rest of the input data
    ser_in = []
    
    # wait until all the time string is received
    while (ser.inWaiting() < 4):
        time.sleep(0.005)
    
    for x in range(0, 4):
      ser_in.append(ord(ser.read()))

    runTime = (ser_in[3]<<24 | ser_in[2]<<16 | ser_in[1]<<8 | ser_in[0]) / 1000000.0
    
    dict_run['run_time'] = runTime
    
    print('Endpoint at:', runTime, 's')
    
    
    
    save_to_json() # save information of this run 
    
    rank = get_runtime_ranking(dict_run['team_name']) # generate ranking file ranking.json and return actual ranking of this team
    print('Actual ranking:', rank)

    show_camera_endpoint_real(rank)
    
    show_ranking(5) # show the whole ranking in the terminal
    
    
    
    
    # wait until a new team started
    team_name_temp = input("Enter a team name to restart...") 
    if team_name_temp != '': # when no team name is entered, the same team will start again
        team_name = team_name_temp           
        
    dict_run['team_name'] = team_name 
    

    # send the ready command to the bluno
    write_to_bluno(0x56)
    
    show_camera_start() # team is ready, show camera at start position
    
    
    
    
def exe_cmd_ready():
    global team_name
    print('Ready when you are', team_name)


# Commands from Bluno which call corresponding functions 
exe_cmd = { 
    0x41 : exe_cmd_first_barrier, # 'A'
    0x42 : exe_cmd_second_barrier, # 'B'
    0x43 : exe_cmd_third_barrier, # 'C'
    0x52 : exe_cmd_ready # 'R' Bluno is ready for new round 
}




ports = list(serial.tools.list_ports.comports())
for p in ports:    
    if 'Arduino' in p:
        print('Connect to ' + str(p))
        break # leave, correct port already found

    
# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
#    port=str(p)[:4],
	port='/dev/ttyACM0',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0
)

ser.isOpen()

ser.reset_input_buffer()
ser.reset_output_buffer()


time.sleep(1)
show_ranking(1000) # show all teams

team_name = input("Enter a team name to get started...")
dict_run['team_name'] = team_name 

show_camera_start() # team is ready, show camera at start position


# send the ready command to the bluno
write_to_bluno(0x59) # restart
time.sleep(1)
write_to_bluno(0x56) # ready for starting
    
while 1 :
  
    # to avoid a lazy system, the input buffer has to be reset  when there are to many information in it
    # if ser.inWaiting() > 20 :
        # ser.reset_input_buffer()
        #print('dump')
    
    
    if ser.inWaiting() != 0:
        command = ser.read()
        #print(command)

        # read command and select function to run
        func = exe_cmd.get(ord(command), "nothing")
        if func != "nothing":
            func()
        
    