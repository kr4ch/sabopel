import serial
import serial.tools.list_ports
import time
import json
import copy
import threading

from subprocess import Popen, PIPE, check_call, check_output


# defines
timer_switch_enabled = True # camera will only switch automatically when this is set to true. Otherwise when endpoint barrier is passed.
waiting_time_camera_endpoint = 0.0 # when the checkpoint is passed, the timer will be started. After this time in s, the camera will be switched to the endpoint camera

TIME_TOTAL_REFERENCE = 14.0
TIME_RUN_REFERENCE = 4.0

# global Variables 
team_name = ''
dict_runs = {'run_counter': 0, 'run_nr':[], 'team_name':[], 'run_time':[], 'checkpoint_time':[], 'total_time':[], 'points_time_total':[], 'points_time_run':[], 'points_bonus':[], 'points_total':[]} # information about all runs (saved in JSON)
dict_run = {'run_nr':0, 'team_name':'', 'run_time':0, 'checkpoint_time':0, 'total_time':0, 'points_time_total':0, 'points_time_run':0, 'points_bonus':0, 'points_total':0} # information for only one run


def find_element_in_pipe(pipe_name, element_name):
#    p = Popen(["gstd-client", "list_elements", pipe_name], \
#        stdin=PIPE, stdout=PIPE, stderr=PIPE)
#    output, err = p.communicate("")
    output = check_output(["gstd-client", "list_elements", pipe_name])
    outputLines = output.splitlines()
    for line in outputLines:
#        print(line)
        if str(element_name) in str(line):
            startPos = str(line).find(str(element_name)) - 2
            print(startPos)
            if startPos != -1:
#                print(str(line[startPos:len(line)-1]))
                return line[startPos:len(line)-1]
#    print("unable to find " + str(element_name))
    return "unable to find " + str(element_name)

def gstreamer_init():
    print("DBG: call gstreamer_init()")
    # Create pipelines
    pipelineName = "pipeStart"
    #pipelineStr = "videotestsrc ! video/x-raw, width=1920, height=1080 ! textoverlay text=\"START Screen\" valignment=top halignment=left font-desc=\"Sans, 30\" ! vaapisink fullscreen=true"
    pipelineStr = "udpsrc port=5001 caps=\"application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)MP2T-ES\" ! rtpbin ! rtpmp2tdepay ! tsdemux ! h264parse ! avdec_h264 ! videoconvert ! textoverlay text=\"START Screen\" valignment=top halignment=left font-desc=\"Sans, 30\" ! vaapisink fullscreen=true sync=false"
    p = Popen(["gstd-client", "pipeline_create", pipelineName, pipelineStr], \
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate("")

    pipelineName = "pipeCheck"
    #pipelineStr = "videotestsrc pattern=ball ! video/x-raw, width=1920, height=1080 !  textoverlay text=\"CHECK Screen\" valignment=top halignment=left font-desc=\"Sans, 30\" ! vaapisink fullscreen=true"
    pipelineStr = "udpsrc port=5002 caps=\"application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)MP2T-ES\" ! rtpbin ! rtpmp2tdepay ! tsdemux ! h264parse ! avdec_h264 ! videoconvert ! textoverlay text=\"Kurve Hafner\" valignment=top halignment=left font-desc=\"Sans, 20\" ! vaapisink fullscreen=true sync=false"
    p = Popen(["gstd-client", "pipeline_create", pipelineName, pipelineStr], \
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate("")

    pipelineName = "pipeEnd"
    #pipelineStr = "videotestsrc pattern=gradient ! video/x-raw, width=1920, height=1080 !  textoverlay text=\"END Screen\" valignment=top halignment=left font-desc=\"Sans, 30\" ! vaapisink fullscreen=true"
    pipelineStr = "udpsrc port=5000 caps=\"application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)MP2T-ES\" ! rtpbin ! rtpmp2tdepay ! tsdemux ! h264parse ! avdec_h264 ! videoconvert ! textoverlay text=\"END Screen\" valignment=top halignment=left font-desc=\"Sans, 30\" line-alignment=left ! vaapisink fullscreen=true sync=false"
    p = Popen(["gstd-client", "pipeline_create", pipelineName, pipelineStr], \
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate("")

    pipelineName = "pipeEndReal"
    #pipelineStr = "videotestsrc pattern=gradient ! video/x-raw, width=1920, height=1080 !  textoverlay text=\"END Screen\" valignment=top halignment=left font-desc=\"Sans, 30\" ! vaapisink fullscreen=true"
    pipelineStr = "udpsrc port=5000 caps=\"application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)MP2T-ES\" ! rtpbin ! rtpmp2tdepay ! tsdemux ! h264parse ! avdec_h264 ! videoconvert ! textoverlay text=\"END REAL Screen\" valignment=top halignment=left font-desc=\"Sans, 40\" line-alignment=left ! vaapisink fullscreen=true sync=false"
    p = Popen(["gstd-client", "pipeline_create", pipelineName, pipelineStr], \
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate("")

    # pipelineName = "pipeEndTimeAll"
    # #pipelineStr = "videotestsrc pattern=gradient ! video/x-raw, width=1920, height=1080 !  textoverlay text=\"END Screen\" valignment=top halignment=left font-desc=\"Sans, 30\" ! vaapisink fullscreen=true"
    # pipelineStr = "udpsrc port=5000 caps=\"application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)MP2T-ES\" ! rtpbin ! rtpmp2tdepay ! tsdemux ! h264parse ! avdec_h264 ! videoconvert ! textoverlay text=\"END REAL Screen\" valignment=top halignment=left font-desc=\"Sans, 40\" line-alignment=left ! vaapisink fullscreen=true sync=false"
    # p = Popen(["gstd-client", "pipeline_create", pipelineName, pipelineStr], \
    #     stdin=PIPE, stdout=PIPE, stderr=PIPE)
    # output, err = p.communicate("")

    # pipelineName = "pipeEndCatched"
    # #pipelineStr = "videotestsrc pattern=gradient ! video/x-raw, width=1920, height=1080 !  textoverlay text=\"END Screen\" valignment=top halignment=left font-desc=\"Sans, 30\" ! vaapisink fullscreen=true"
    # pipelineStr = "udpsrc port=5000 caps=\"application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)MP2T-ES\" ! rtpbin ! rtpmp2tdepay ! tsdemux ! h264parse ! avdec_h264 ! videoconvert ! textoverlay text=\"END REAL Screen\" valignment=top halignment=left font-desc=\"Sans, 40\" line-alignment=left ! vaapisink fullscreen=true sync=false"
    # p = Popen(["gstd-client", "pipeline_create", pipelineName, pipelineStr], \
    #     stdin=PIPE, stdout=PIPE, stderr=PIPE)
    # output, err = p.communicate("")

    # pipelineName = "pipeEndNotCatched"
    # #pipelineStr = "videotestsrc pattern=gradient ! video/x-raw, width=1920, height=1080 !  textoverlay text=\"END Screen\" valignment=top halignment=left font-desc=\"Sans, 30\" ! vaapisink fullscreen=true"
    # pipelineStr = "udpsrc port=5000 caps=\"application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)MP2T-ES\" ! rtpbin ! rtpmp2tdepay ! tsdemux ! h264parse ! avdec_h264 ! videoconvert ! textoverlay text=\"END REAL Screen\" valignment=top halignment=left font-desc=\"Sans, 40\" line-alignment=left ! vaapisink fullscreen=true sync=false"
    # p = Popen(["gstd-client", "pipeline_create", pipelineName, pipelineStr], \
    #     stdin=PIPE, stdout=PIPE, stderr=PIPE)
    # output, err = p.communicate("")

def stop_all_pipes():
    pipelineName = "pipeStart"
    p = Popen(["gstd-client", "pipeline_stop", pipelineName],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate("")
    pipelineName = "pipeCheck"
    p = Popen(["gstd-client", "pipeline_stop", pipelineName],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate("")
    pipelineName = "pipeEnd"
    p = Popen(["gstd-client", "pipeline_stop", pipelineName],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate("")
    pipelineName = "pipeEndReal"
    p = Popen(["gstd-client", "pipeline_stop", pipelineName],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate("")
    # pipelineName = "pipeEndTimeAll"
    # p = Popen(["gstd-client", "pipeline_stop", pipelineName],
    #     stdin=PIPE, stdout=PIPE, stderr=PIPE)
    # output, err = p.communicate("")
    # pipelineName = "pipeEndCatched"
    # p = Popen(["gstd-client", "pipeline_stop", pipelineName],
    #     stdin=PIPE, stdout=PIPE, stderr=PIPE)
    # output, err = p.communicate("")
    # pipelineName = "pipeEndNotCatched"
    # p = Popen(["gstd-client", "pipeline_stop", pipelineName],
    #     stdin=PIPE, stdout=PIPE, stderr=PIPE)
    # output, err = p.communicate("")


def delete_all_pipes():
    pipelineName = "pipeStart"
    p = Popen(["gstd-client", "pipeline_delete", pipelineName],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate("")
    pipelineName = "pipeCheck"
    p = Popen(["gstd-client", "pipeline_delete", pipelineName],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate("")
    pipelineName = "pipeEnd"
    p = Popen(["gstd-client", "pipeline_delete", pipelineName],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate("")
    pipelineName = "pipeEndReal"
    p = Popen(["gstd-client", "pipeline_delete", pipelineName],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate("")
    # pipelineName = "pipeEndTimeAll"
    # p = Popen(["gstd-client", "pipeline_delete", pipelineName],
    #     stdin=PIPE, stdout=PIPE, stderr=PIPE)
    # output, err = p.communicate("")
    # pipelineName = "pipeEndCatched"
    # p = Popen(["gstd-client", "pipeline_delete", pipelineName],
    #     stdin=PIPE, stdout=PIPE, stderr=PIPE)
    # output, err = p.communicate("")
    # pipelineName = "pipeEndNotCatched"
    # p = Popen(["gstd-client", "pipeline_delete", pipelineName],
    #     stdin=PIPE, stdout=PIPE, stderr=PIPE)
    # output, err = p.communicate("")


def show_camera_start():
    global dict_run
    # show camera start and make overlay with dict_run['team_name']
    print("camera start")
    stop_all_pipes()
    pipelineName = "pipeStart"
    elementName = find_element_in_pipe(pipelineName, "textoverlay")
    propertyName = "text"
    propertyValue = "Starting Next: " + str(dict_run['team_name'])
    print("propertyValue = " + propertyValue)
    p = Popen(["gstd-client", "element_set", pipelineName, elementName, propertyName, propertyValue],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    p = Popen(["gstd-client", "pipeline_play", pipelineName],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate("")

def show_camera_checkpoint():
    global dict_run
    # show camera start and make overlays with dict_run['team_name'] and dict_run['checkpoint_time']
    print("camera checkpoint")
    stop_all_pipes()
    pipelineName = "pipeCheck"
    elementName = find_element_in_pipe(pipelineName, "textoverlay")
    propertyName = "text"
#    propertyValue = "Checkpoint Time: " + str("{0:.3f}".format(dict_run['checkpoint_time']))
    propertyValue = ""
    p = Popen(["gstd-client", "element_set", pipelineName, elementName, propertyName, propertyValue],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    p = Popen(["gstd-client", "pipeline_play", pipelineName],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate("")



# Zieleinfahrt
def show_camera_endpoint_timer():
    global dict_run
    # show camera start and make overlays with dict_run['team_name'], dict_run['run_time'], and dict_run['difference_to_first']
    print("camera endpoint")
    stop_all_pipes()
    pipelineName = "pipeEnd"
    elementName = find_element_in_pipe(pipelineName, "textoverlay")
    propertyName = "text"
    propertyValue = "Zieleinfahrt\nCheckpoint Time: " + str("{0:.3f}".format(dict_run['checkpoint_time']))
    p = Popen(["gstd-client", "element_set", pipelineName, elementName, propertyName, propertyValue],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    p = Popen(["gstd-client", "pipeline_play", pipelineName],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate("")



# Ziel Lichtschranke passiert:
def show_camera_endpoint_real():#_rank):
    global dict_run
    # show camera start and make overlays with dict_run['team_name'], dict_run['run_time'], and dict_run['difference_to_first']

    # Get Ranking
#    dict_ranking = json.load(open('ranking.json'))
#    maxLength = len(dict_ranking['team_name'])
#    rankingString = ""
#    nrOfTeamsToShow = 5
#    for x in range(0, min(nrOfTeamsToShow,maxLength)):
#        rankingString = str(rankingString) + str(x+1)+':\t',"{:<20}".format(dict_ranking['team_name'][x]), '\tbest time:', "{0:.3f}".format(dict_ranking['run_time'][x]), '\tdifference:', "{0:.3f}".format(dict_ranking['difference_to_first'][x])

    stop_all_pipes()
    pipelineName = "pipeEndReal"
    elementName = find_element_in_pipe(pipelineName, "textoverlay")
    propertyName = "text"
    propertyValue = str(dict_run['team_name']) + "\nBob Time: " + str("{0:.3f}".format(dict_run['run_time']))# + "\nRank: " + str(_rank))# +
#        "\n\n\n" + 
#        str(rankingString)
    #+ " Difference to first: " + str("{0:.3f}".format(dict_run['difference_to_first'])) 
    p = Popen(["gstd-client", "element_set", pipelineName, elementName, propertyName, propertyValue],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)
    p = Popen(["gstd-client", "pipeline_play", pipelineName],
        stdin=PIPE, stdout=PIPE, stderr=PIPE)

    #"{0:.3f}".format(dict_run['run_time'])
    print("camera endpoint")#, _rank)










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


def show_ranking_total(_show_nr):

    print("\nRanking")
    
    try:
        dict_ranking = json.load(open('ranking_total.json'))
        
        maxLength = len(dict_ranking['team_name'])
        
        for x in range(0, min(_show_nr,maxLength)):
            print(str(x+1)+':\t',"{:<20}".format(dict_ranking['team_name'][x]), '\tscore:', "{0:.1f}".format(dict_ranking['points_total'][x]), '\tbest time:', "{0:.3f}".format(dict_ranking['run_time'][x]), '\tdifference:', "{0:.3f}".format(dict_ranking['difference_to_first'][x]))
                  
        print('')

    except:
        return False    
        
    
    
# loads the runs.json with all the runs, sorts it using the run_time and restores the file in ranking.json
# Difference to the first place is also calculated in here.
def get_ranking(_team_name):
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





# loads the runs.json with all the runs, sorts it using the run_time and restores the file in ranking.json
# Difference to the first place is also calculated in here.
def get_total_ranking(_team_name):
    global dict_ranking
    
    used_team_names = [] # if a team name is already in this list, it won't be in the ranking list anymore (only once per ranking list)
    
   # if a team name is already saved, do not append it again
    try:
        dict_runs = json.load(open('runs.json'))
        
        dict_ranking = {'run_nr':[], 'team_name':[], 'run_time':[], 'checkpoint_time':[], 'difference_to_first':[], 'total_time':[] , 'points_time_total':[], 'points_time_run':[], 'points_bonus':[], 'points_total':[]} # make sure directory is empty
        fastest_total_time = max(dict_runs['points_total']) # this is the best
        length = len(dict_runs['run_nr'])
        
        for x in range(0, length):
            index = dict_runs['points_total'].index(max(dict_runs['points_total']))
            
            if dict_runs['team_name'][index] not in used_team_names: # copy only to rank list, when the team isn't already in there

                # minimum runtime found, copy all corresponding values
                dict_ranking['run_nr'].append(dict_runs['run_nr'][index])
                dict_ranking['team_name'].append(dict_runs['team_name'][index])
                dict_ranking['run_time'].append(dict_runs['run_time'][index])
                dict_ranking['checkpoint_time'].append(dict_runs['checkpoint_time'][index])
                dict_ranking['difference_to_first'].append(dict_runs['run_time'][index] - fastest_run_time)

                dict_ranking['total_time'].append(dict_runs['total_time'][index])
                dict_ranking['points_time_total'].append(dict_runs['points_time_total'][index])
                dict_ranking['points_time_run'].append(dict_runs['points_time_run'][index])
                dict_ranking['points_bonus'].append(dict_runs['points_bonus'][index])
                dict_ranking['points_total'].append(dict_runs['points_total'][index] - fastest_run_time)
                
                used_team_names.append(dict_ranking['team_name'][-1]) # add newest entry to make only one entry
            
            # delete entries to get next place in ranking
            del dict_runs['run_nr'][index]
            del dict_runs['team_name'][index]
            del dict_runs['run_time'][index]
            del dict_runs['checkpoint_time'][index]

            del dict_runs['total_time'][index]
            del dict_runs['points_time_total'][index]
            del dict_runs['points_time_run'][index]
            del dict_runs['points_bonus'][index]
            del dict_runs['points_total'][index]
            
            
            
        # write ranking file    
        try:
            with open('ranking_total.json', 'w') as outfile:
                json.dump(dict_ranking, outfile)
        except:
            print("problems writing JSON file 'ranking_total.json'")
                
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
        

    print(dict_runs)
    dict_runs['run_counter'] += 1
    
    # append lists with new values
    dict_runs['run_nr'].append(dict_runs['run_counter'])
    dict_runs['team_name'].append(dict_run['team_name'])
    dict_runs['run_time'].append(dict_run['run_time'])
    dict_runs['checkpoint_time'].append(dict_run['checkpoint_time'])

    dict_runs['total_time'].append(dict_run['total_time'])
    dict_runs['points_time_total'].append(dict_run['points_time_total'])
    dict_runs['points_time_run'].append(dict_run['points_time_run'])
    dict_runs['points_bonus'].append(dict_run['points_bonus'])
    dict_runs['points_total'].append(dict_run['points_total'])
    
    try:
        with open('runs.json', 'w') as outfile:
            json.dump(dict_runs, outfile)
    except:
        print("problems writing JSON file")
    
    
    
    
def exe_cmd_first_barrier():
    print('Started')
    show_camera_checkpoint() # checkpoint passed, switch camera
    
    
    
def exe_cmd_second_barrier():
    global dict_run
    
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

    show_camera_checkpoint() # checkpoint passed, switch camera

    time.sleep(5) # DBG: Wait at least 5 sec
    
    
    
    
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
    

    show_camera_endpoint_real()
    
    show_ranking(5) # show the whole ranking in the terminal

    
    
def exe_cmd_ready():
    global team_name
    print('Ready when you are', team_name)





def calculate_points(_total_time, _run_time, _catch_state):
    global team_name, dict_run

    dict_run['points_time_total'] = int(100 + (TIME_TOTAL_REFERENCE - dict_run['total_time']) * 10)
    dict_run['points_time_run'] = int(100 + (TIME_RUN_REFERENCE - dict_run['run_time']) * 50)
    if _catch_state == 'catched': 
        dict_run['points_bonus'] = (dict_run['points_time_total'] + dict_run['points_time_run']) * 0.5
    else:
        dict_run['points_bonus'] = 0

    dict_run['points_total'] = dict_run['points_time_total'] + dict_run['points_time_run'] + dict_run['points_bonus']




def exe_cmd_time_all():
    global dict_run

    # read the rest of the input data
    ser_in = []
    
    # wait until all the time string is received
    while (ser.inWaiting() < 4):
        time.sleep(0.005)
    
    for x in range(0, 4):
      ser_in.append(ord(ser.read()))

    runTimeAll = (ser_in[3]<<24 | ser_in[2]<<16 | ser_in[1]<<8 | ser_in[0]) / 1000000.0
    
    dict_run['total_time'] = runTimeAll
    
    print('Total Time:', runTimeAll, 's')

#     stop_all_pipes()
#     pipelineName = "pipeEndTimeAll"
#     elementName = find_element_in_pipe(pipelineName, "textoverlay")
#     propertyName = "text"
#     propertyValue = str(dict_run['team_name']) + "\nTotal Time: " + str("{0:.3f}".format(dict_run['total_time']) + "\nRank: " + str(_rank))# +
# #        "\n\n\n" + 
# #        str(rankingString)
#     #+ " Difference to first: " + str("{0:.3f}".format(dict_run['difference_to_first'])) 
#     p = Popen(["gstd-client", "element_set", pipelineName, elementName, propertyName, propertyValue],
#         stdin=PIPE, stdout=PIPE, stderr=PIPE)
#     p = Popen(["gstd-client", "pipeline_play", pipelineName],
#         stdin=PIPE, stdout=PIPE, stderr=PIPE)


def exe_cmd_catched():    
    global team_name, dict_run
     
    print('shot catched')

    # calculate points
    calculate_points(dict_run['total_time'], dict_run['run_time'], 'catched')

    save_to_json() # save information of this run 
    
    rank_bob = get_ranking(dict_run['team_name']) # generate ranking file ranking.json and return actual ranking of this team
    print('Actual ranking for bob track:', rank_bob)

    rank_total = get_total_ranking(dict_run['team_name']) # generate ranking file ranking.json and return actual ranking of this team
    print('Actual ranking:', rank_total)

    print('points time total:', dict_run['points_time_total'])
    print('points time run:', dict_run['points_time_run'])
    print('points bonus:', dict_run['points_bonus'])
    print('points total:', dict_run['points_total'])

    show_ranking_total(1000)

    # wait until a new team started
    team_name_temp = input("Enter a team name to restart...") 
    if team_name_temp != '': # when no team name is entered, the same team will start again
        team_name = team_name_temp           
        
    dict_run['team_name'] = team_name 
    

    stop_all_pipes()
    delete_all_pipes()
    gstreamer_init()

    show_camera_start() # team is ready, show camera at start position
    


def exe_cmd_not_catched():    
    global team_name, dict_run
    
    print('shot not catched')

    # calculate points
    calculate_points(dict_run['total_time'], dict_run['run_time'], 'nothing')

    save_to_json() # save information of this run 

    rank_bob = get_ranking(dict_run['team_name']) # generate ranking file ranking.json and return actual ranking of this team
    print('Actual ranking for bob track:', rank_bob)
    
    rank_total = get_total_ranking(dict_run['team_name']) # generate ranking file ranking.json and return actual ranking of this team
    print('Actual ranking:', rank_total)
    
    print('points time total:', dict_run['points_time_total'])
    print('points time run:', dict_run['points_time_run'])
    print('points bonus:', dict_run['points_bonus'])
    print('points total:', dict_run['points_total'])

    show_ranking_total(1000)

    # wait until a new team started
    team_name_temp = input("Enter a team name to restart...") 
    if team_name_temp != '': # when no team name is entered, the same team will start again
        team_name = team_name_temp           
        
    dict_run['team_name'] = team_name 
    

    stop_all_pipes()
    delete_all_pipes()
    gstreamer_init()
    
    show_camera_start() # team is read
    


# Commands from Bluno which call corresponding functions 
exe_cmd = { 
    0x41 : exe_cmd_first_barrier, # 'A'
    0x42 : exe_cmd_second_barrier, # 'B'
    0x43 : exe_cmd_third_barrier, # 'C'
    0x44 : exe_cmd_time_all, # 'D'
    0x45 : exe_cmd_catched, # 'E'
    0x46 : exe_cmd_not_catched, # 'F'
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

stop_all_pipes()
delete_all_pipes()
gstreamer_init() # Initialize GStreamer receive pipelines


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
        
    