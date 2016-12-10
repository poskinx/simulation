import simpy
import random
from matplotlib import pyplot as plt
from matplotlib import style

###### General variables ######
LAMBDA = 20         # paq/second
MU = 50             # paq/second
SERVICE_T = 0.02    # Average service time (exponential time)
ARRIVAL_T = 0.05    # Average arrival time (exponential time)
NUM_SERVERS = 1     # number of servers in the queue
SIM_TIME = 350      # time of simulation in seconds, T:{35, 175, 350, 1750}
SIM_NUM = 20        # number of simulations
TRANSFER_TIME = []  # array to accumulate the transfer time of each petition processed
AVERAGE_TT = []     # array to accumulate the mean transfer time of each simulation


class Queue(object):
    """ A queue with a certain number of servers (``NUM_SERVERS``) to
        serve petitions in parallel
        Petitions have to request a server. When they got one, they
        can start being processed by the server and wait for it to finish
        which takes (``SERVICE_T``) in seconds.
    """

    def __init__(self, env, num_servers):
        self.env = env
        self.server = simpy.Resource(env, num_servers)

    def service(self, petition, service_time):
        """The serving processes. It takes a ``petition`` processes and tries
                to serve it."""
        yield self.env.timeout(service_time)
        # print("%s: ##### My service time is %.5f." % (petition, service_time))


def petition(env, name, queue, service_time):
    """The petition process (each petition has a ``name``) arrives at the queue
        (``queue``) and requests a server.

        Then starts the serving process, waits for it to finish and
        leaves to never come back ...
        """
    # print('%s arrives at the queue at %.5f.' % (name, env.now))
    arriving_time = env.now
    with queue.server.request() as request:
        yield request

        # print('%s enters the queue at %.5f.' % (name, env.now))
        yield env.process(queue.service(name, service_time))

        # print('%s leaves the queue at %.5f.' % (name, env.now))
        leaving_time = env.now
        transfer_time = (leaving_time - arriving_time)
        TRANSFER_TIME.append(transfer_time)
        # print('%s: ##### My transfer time is %.5f.' % (name, transfer_time))


def setup(env, num_servers):
    """Create a queue and keep creating petitions approx. every
    ``arrival_time`` seconds."""
    # Create the queue
    queue = Queue(env, num_servers)

    # # Generate 4 initial petitions
    # for i in range(4):
    #     env.process(petition(env, 'Petition %d' % i, queue))
    y = 0
    # Generate more petitions while the simulation is running
    while True:
        lambd = 1 / ARRIVAL_T
        yield env.timeout(random.expovariate(lambd))
        mu = 1 / SERVICE_T
        service_time = random.expovariate(mu)
        y += 1
        env.process(petition(env, 'Petition %d' % y, queue, service_time))


for i in range(0, SIM_NUM):

    # Setup and start the simulation
    print('MM1 Queue')
    # Create an environment and start the setup process
    env = simpy.Environment()
    env.process(setup(env, NUM_SERVERS))

    # Execute!
    env.run(until=SIM_TIME)

    # Calculating the average of each simulation
    AVERAGE_TT.append(sum(TRANSFER_TIME)/len(TRANSFER_TIME))
    print("Average %d transfer time : %.9f" % (i, AVERAGE_TT[i]))


x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
y = AVERAGE_TT

R = 1/(MU-LAMBDA)
print('Theoretical transfer time %.8f' % R)

y2 = [R] * SIM_NUM

style.use('ggplot')

plt.scatter(x, y)
plt.plot(x, y2, 'r', label='theoretical transfer time')

plt.title('MM1 Queue')
plt.xlabel('Number of simulations')
plt.ylabel('Transfer time')
plt.legend()

plt.show()
