import simgrid
from simgrid import Actor, Engine, Host, Mailbox, this_actor
from random import uniform
import math
import sys
###
# GLOBAL VARIABLES (FOR ROUND DATA CALCULATION)
###
SYNC_INTERVAL = 3           # number of seconds the master waits between rounds
SYNC_ROUNDS = 50            # number of rounds (simulation ran with 5, 50, and 100 rounds)
ROUND_OFFSETS = []          # list of offsets in seconds that workers are from the master (cleared between rounds) 
OFFSET_MEANS = []           # list of offset means of each round (OFFSET_MEANS[0] : Round 1, OFFSET_MEANS[1] : Round 2, etc.)
OFFSET_DEVIATIONS = []      # list of offset standard deviations from the calculated means for that round (OFFSET_DEVIATIONS[0] : Round 1, OFFSET_DEVIATIONS[1] : Round 2, etc.)
MIN_OFFSET = float('inf')   # float that tracks the minimum offset detected in ENTIRE simulation period
MAX_OFFSET = 0.0            # float that tracks the maximum offset detected in ENTIRE simulation period

# master begin
def master(*args):
  global ROUND_OFFSETS, MIN_OFFSET, MAX_OFFSET
  workers = []                                                  # mailboxes of all worker processes
  master_mailbox = Mailbox.by_name(this_actor.get_host().name)  # create mailbox for master process
  
  # using names taken from deployment file (given through command line args), store worker mailboxes in a list
  for i in range(len(args)): 
    workers.append(Mailbox.by_name(args[i]))    
  this_actor.info(f"Got {len(workers)} workers")
  
  # send all workers the name associated with the master mailbox, to allow bidirectional communication
  for mailbox in workers:
    message = {"msg_type" : "master_name", "master" : this_actor.get_host().name}
    mailbox.put(message, len(message))  
    
  # sleep master process for 5 seconds to give workers time to prepare
  this_actor.sleep_for(5)
  
  # main logic loop for sync rounds
  for index in range(1, SYNC_ROUNDS + 1):
      ROUND_OFFSETS = []    # set ROUND_OFFSETS to an empty list at the start of each round
      
      this_actor.info(f"Sync round {index} starting...")
      this_actor.info(f"Master clock is at {Engine.clock}")
      
      # send a command to all workers to generate a randomized offset from the master clock (offset ranges from -5 to +5 seconds to master clock)
      for mailbox in workers:
        message = {"msg_type" : "clock_offset"}
        mailbox.put(message, len(message))
      
      # send a beginning sync message to all workers, including the timestamp on the master the message was sent
      for mailbox in workers:
        message = {"msg_type" : "sync_clock", "master_timestamp" : Engine.clock}
        mailbox.put(message, len(message))
        
        # sleep for 0.5 second to give worker time to process message
        this_actor.sleep_for(0.5)
        
        # send a sync followup message to worker
        message = {"msg_type" : "sync_followup"}
        mailbox.put(message, len(message))

        # wait for a response from the worker
        response = master_mailbox.get()
        
        # if message is of type 'delay_request', send back timestamp of when message was recieved
        if response["msg_type"] == "delay_request":
            t4 = Engine.clock
            message = {"msg_type" : "delay_response", "T4" : t4}
            mailbox.put(message, len(message))
        
        # wait for 'sync_complete' message from worker, to display master clock 
        response = master_mailbox.get()
        if response["msg_type"] == "sync_complete":
            this_actor.info(f"Master clock is at {Engine.clock} after syncing {mailbox.name}")
            
      this_actor.info(f"Sync round {index} over!\n")

      # caculate varibles from data collected during round
      analyze_offsets()
    
      # sleep for the sync interval before starting next round
      this_actor.sleep_for(SYNC_INTERVAL)
        
  # after rounds are complete, send shutdown message to all workers      
  for mailbox in workers:
    message = {"msg_type" : "end_simulation"}
    mailbox.put(message, len(message))
    
  # After simulation, output collected data
  this_actor.info('Round #\t| Mean offset AFTER syncing\t| Standard deviation of offset AFTER syncing')
  this_actor.info('----------------------------------------------------------------------------------')
  for round in range(1, SYNC_ROUNDS + 1):
    this_actor.info(f'{round}\t| {OFFSET_MEANS[round - 1]} \t| {OFFSET_DEVIATIONS[round - 1]}')
  this_actor.info(f'Simulation mean expected value: {sum(OFFSET_MEANS) / len(OFFSET_MEANS)}')
  this_actor.info(f'Simulation standard deviation expected value: {sum(OFFSET_DEVIATIONS) / len(OFFSET_DEVIATIONS)}')
  this_actor.info(f'Simulation smallest offset: {MIN_OFFSET}')
  this_actor.info(f'Simulation largest offset: {MAX_OFFSET}')
# master end

# worker begin
def worker(*args):
  global ROUND_OFFSETS, MIN_OFFSET, MAX_OFFSET
  assert len(args) == 0, "The worker expects to not get any argument"
  
  mailbox = Mailbox.by_name(this_actor.get_host().name) # set up own mailbox
  clock_offset = 0                                      # represents an offset from master clock (simulation clock)
  done = False                                          # main loop logic variable
  
  # wait for message from master that contains the name associated with the master mailbox
  message = mailbox.get()
  if message["msg_type"] == "master_name":
    master_mailbox = Mailbox.by_name(message["master"])
  
  # main loop
  while not done:
    # wait for message from master
    message = mailbox.get()
    
    # if 'clock_offset', generate a random offset from master clock to simulate de-sync (-5 to +5 seconds from master)
    if message["msg_type"] == "clock_offset":
        clock_offset = uniform(-1, 1) * 5
        this_actor.info(f"Node {mailbox.name} clock is at {Engine.clock + clock_offset}")
    # if 'sync_clock', take t2 timestamp and retrieve t1 timestamp from sent message
    elif message["msg_type"] == "sync_clock":
        t2 = (Engine.clock + clock_offset)
        t1 = message["master_timestamp"]
        
        # wait for message from master
        message = mailbox.get()
        
        # if 'sync_followup', take t3 timestamp and send response back to master
        if message["msg_type"] == "sync_followup":
            response = {"msg_type" : "delay_request"}
            t3 = (Engine.clock + clock_offset)
            master_mailbox.put(response, len(response))
        
        # wait for message from master
        message = mailbox.get()
        
        # if 'delay_response', take t4 timestamp 
        if message["msg_type"] == "delay_response":
            t4 = message["T4"]
        
        # offset of worker from master can be calculated from taken timestamps
        offset_from_master = ((t2 - t1) - (t4 - t3)) / 2
        
        # send message to have master display its clock (for comparison)
        response = {"msg_type" : "sync_complete"}
        master_mailbox.put(response, len(response))
        
        # output old clock time and new clock time of worker
        this_actor.info(f"Node {mailbox.name} clock is synced from {Engine.clock + clock_offset} to {Engine.clock + clock_offset - offset_from_master}!")
        
        # store offset of new clock time from master clock 
        ROUND_OFFSETS.append((Engine.clock + clock_offset - offset_from_master) - Engine.clock)
        
        # output offset of new clock time from master clock
        this_actor.info(f"({mailbox.name} clock is offset by {ROUND_OFFSETS[-1]} seconds)")
        
        # check to see if offset is the largest or smallest seen so far, and record if either
        if abs(ROUND_OFFSETS[-1]) < abs(MIN_OFFSET):
            MIN_OFFSET = ROUND_OFFSETS[-1]
        elif abs(ROUND_OFFSETS[-1]) > abs(MAX_OFFSET):
            MAX_OFFSET = ROUND_OFFSETS[-1]
            
    # if any other message, end worker  
    else:
        done = True
# worker end

# analyze_offsets begin
def analyze_offsets():
    global ROUND_OFFSETS, OFFSET_MEANS, OFFSET_DEVIATIONS
    
    elems_minus_mean_squared = 0 # will contain the sum of (all elements of ROUND_OFFSETS minus the means offset of that round), all squared
    
    OFFSET_MEANS.append( sum(ROUND_OFFSETS) / len(ROUND_OFFSETS) )  # record the mean of the offsets from this round
    
    for elem in ROUND_OFFSETS:
        elems_minus_mean_squared += (elem - OFFSET_MEANS[-1])**2
        
    OFFSET_DEVIATIONS.append( math.sqrt(elems_minus_mean_squared / (len(ROUND_OFFSETS) - 1)) )   # record the standard deviation of the offsets from this round
# analyze_offsets end

# main begin
if __name__ == '__main__':
    assert len(sys.argv) > 2, f"Usage: python3 app-masterworkers.py platform_file deployment_file"

    # Start SimGrid engine
    e = Engine(sys.argv)

    # Register the classes representing the actors
    e.register_actor("master", master)
    e.register_actor("worker", worker)

    # Load the platform description and then deploy the application
    e.load_platform(sys.argv[1]) 
    e.load_deployment(sys.argv[2])

    # Run the simulation
    e.run()

    this_actor.info("Simulation is over")
# main end
