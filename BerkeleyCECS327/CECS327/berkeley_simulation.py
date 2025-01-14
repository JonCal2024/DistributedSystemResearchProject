import simgrid

from simgrid import Actor, Engine, Host, Mailbox, this_actor

from random import uniform

import sys



SYNC_INTERVAL = 3

SYNC_ROUNDS = 5



# master-begin

def master(*args):

    workers = []

    master_mailbox = Mailbox.by_name(this_actor.get_host().name)

    for i in range(3, len(args)):

        workers.append(Mailbox.by_name(args[i]))

    this_actor.info(f"Got {len(workers)} workers")



    for mailbox in workers:

        message = {"msg_type": "master_name", "master": this_actor.get_host().name}

        mailbox.put(message, len(message))



        this_actor.sleep_for(5)



    for index in range(1, SYNC_ROUNDS):

        this_actor.info(f"Sync round {index} starting...")

        this_actor.info(f"Master clock is at {Engine.clock}")

        for mailbox in workers:

            message = {"msg_type": "clock_request"}

            mailbox.put(message, len(message))



        t1 = Engine.clock

        for mailbox in workers:

            message = mailbox.get()

            if message["msg_type"] == "clock_response":

                t2 = Engine.clock

                t3 = message["timestamp"]

                offset = (t2 + t1) / 2 - t3

                this_actor.info(f"Received clock response from {mailbox.name}, offset = {offset}")

        this_actor.sleep_for(SYNC_INTERVAL)



    for mailbox in workers:

        message = {"msg_type": "end_simulation"}

        mailbox.put(message, len(message))

# master-end



# worker-begin

def worker(*args):

    assert len(args) == 0, "The worker expects to not get any argument"



    mailbox = Mailbox.by_name(this_actor.get_host().name)

    clock_offset = 0



    message = mailbox.get()

    if message["msg_type"] == "master_name":

        master_mailbox = Mailbox.by_name(message["master"])

    done = False

    while not done:

        message = mailbox.get()

        if message["msg_type"] == "clock_request":

            timestamp = Engine.clock

            response = {"msg_type": "clock_response", "timestamp": timestamp}

            mailbox.put(response, len(response))

        elif message["msg_type"] == "end_simulation":

            done = True



    this_actor.info("Exiting now.")

# worker-end



# main-begin

if __name__ == '__main__':

    assert len(sys.argv) > 2, "Usage: python berkeley_simulation.py platform_file deployment_file"



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

# main-end

