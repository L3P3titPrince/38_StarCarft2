"""
Sources
YouTube:https://www.youtube.com/watch?v=v3LJ6VvpfgI&list=PLQVvvaa0QuDcT3tPehHdisGMc8TInNqdq&index=2&t=0s&ab_channel=sentdex
zhihu.com:https://zhuanlan.zhihu.com/p/33897686
zhihu.com:https://zhuanlan.zhihu.com/p/100032133
SC2AI_github（Chiness):https://github.com/ClausewitzCPU0/SC2AI
TorchCraft:https://github.com/TorchCraft/TorchCraft
Offical_API:https://github.com/Blizzard/s2client-proto
Deepmind_pysc2(more reinforement learning):https://github.com/deepmind/pysc2
python-sc2:https://github.com/Dentosal/python-sc2
Introduction:https://pythonprogramming.net/starcraft-ii-ai-python-sc2-tutorial/
"""


"""
Env and package initial 
conda create 10_starcraft2
conda activate 10_starcraft2
# using pip without --user will only install in conda env when special envirnemnt is activate
pip install --upgrade sc2

"""

import random
import sc2
# Race = Terran, Zerg, Protoss
# run_game used to lanuch game and assign launch parameters
# maps to denote which map will be used
# Difficuly to choose computer level
from sc2 import run_game, maps, Race, Difficulty
# Bot is our AI algorithm and Computer is build-in computerAI, Human is player control
from sc2.player import Bot, Computer, Human
# NEXUS is the base of Protoss, PROBE is the worker of Protoss, PYLON is the population state fo Protoss
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, CYBERNETICSCORE, \
    STALKER, STARGATE, VOIDRAY

# this is test run_game function
class SentdeBot(sc2.BotAI):
    """
    Inherit CLASS sc2.BotAI, some method will be involoved
    """
    # 165 iterations per minute
    async def on_step(self, iteration):
        """
        Every step we goona to do
        :param iteration:
        :return:
        """
        # distribute_workers is built-in function
        # you start with 12 workers and tell them what to do
        # intellgience distribute workders for gas no more than three
        await self.distribute_workers()

# this is human vs AI function
class Bot1(sc2.BotAI):
    """
    build workers and pylons
    """
    def __init__(self):
        # somehow we know the build-in iteration is 165, so divide by this will
        self.ITERATIONS_PER_MINUTS = 165
        self.MAX_WORKERS = 80
    # 165 iterations per minute (not sure its right)
    async def on_step(self, iteration):
        self.iteration = iteration
        # distribute_workers() is build in function which can inherited from sc2.BotAI
        await self.distribute_workers()
        # this is my self-def function, need declare in this on_step() function
        await self.build_workers()
        # this is my self-def function, need declare in this on_step() function
        await self.build_pylons()
        # build assimilators
        await self.build_assimilator()
        # we have self.expand_now, but we still build our own expand function
        await self.manual_expand()
        # create CYBER and GATEWAY
        await self.build_offensive_force()
        # train STALKER
        await self.train_offensive_force()
        # set up a strategy about attack enemy
        await self.attack_enemy()

    async def build_workers(self):
        """
        Select idel base and build workers
        noqueue means current building sequence is empty
        workers will be limit in a fix number to mack combination more
        :return:
        """
        # if units number < max number for one NEXUS and total num of workers < maximize limitation
        if (len(self.units(PROBE)) < (len(self.units(NEXUS))*16)) and len(self.units(PROBE)) < self.MAX_WORKERS:
            # when we find no item is building in NEXUS's building sequence
            for nexus in self.units(NEXUS).ready.idle:
                # if we have enough gold to build PROBe
                if self.can_afford(PROBE):
                    # insert order for nexus to produce PROBE
                    await self.do(nexus.train(PROBE))

    async def build_pylons(self):
        """
        population < 5 then build PYLON
        :return:
        """
        # supply_left is population
        if self.supply_left < 5 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                # gold can buy a py
                if self.can_afford(PYLON):
                    # near is building location, we can use deep learning to optimize
                    # our PYLON will bulid near NEXUES
                    await self.build(PYLON, near=nexuses.first)

    async def build_assimilator(self):
        """

        :return:
        """
        # when NEXUS is idle,
        for nexus in self.units(NEXUS).ready:
            # looking for any vespene_geyser(油气井) are colse to nexus in 25 unit distance
            # you maybe find a lot of geyser, iteration them one by one, that's why we use plurality herer
            # 25 unit distance is too far away, maybe we can decrease to 10
            vaspenes = self.state.vespene_geyser.closer_than(15.0, nexus)
            # iteration each geyser
            for vaspene in vaspenes:
                # if we cannot afford to build a ASSIMILATOR, we break this loop, do not assign anythin
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vaspene.position)
                if worker is None:
                    break
                # using closer_than to decide distance and from who, which means how far away from reference object
                # in this sentcen, we judge ASSIMILATOR should locate in one unit distance from vaspens(geyser)
                if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists:
                    # this vaspene is location info
                    await self.do(worker.build(ASSIMILATOR, vaspene))

    # expand NEXUS(base)
    async def manual_expand(self):
        """
        If we have less than 3 NEXUS and we have enough money, we will expand
        Check expand_now() for more detail
        :return:
        """
        if self.units(NEXUS).amount < 3 and self.can_afford(NEXUS):
            await self.expand_now()

    async def build_offensive_force(self):
        """
        This is build function, we use it to build CYBER primaryl in this function
        :return:
        """
        # try to say iteration process
        # print(self.iteration / self.ITERATIONS_PER_MINUTS)
        if self.units(PYLON).ready.exists:
            # random pick one of pylon
            pylon = self.units(PYLON).ready.random
            # ***********************Build GATWAY and CYBERNETICSCOR**************************************
            # GATEWAY is level one Barracks, if we want to build CYBER we need to build GATEWAY first
            # we need GATEWAY to train ZELATR and STALKER
            # IF we don't have cyberneticscore, which is prerequisite for STALKER
            # if we have enough money for CYBER and don't have building CYBER, then we start build CYBER
            # 1.We have a GATEWAY, which is the prerequsite for CYBER
            # 2.We don't have a CYBER, CYBER is technology building we only need one
            # 3.We have enough monty to build a CYBER
            # 4.We don't have under constrcaion CYBER
            if self.units(GATEWAY).ready.exists and \
                    not self.units(CYBERNETICSCORE) and \
                    self.can_afford(CYBERNETICSCORE) and \
                    not self.already_pending(CYBERNETICSCORE):
                    await self.build(CYBERNETICSCORE, near=pylon)
                    print("Build a CYBERNETICSCORE")
            # if we don't have GATEWAY, we need build GATEWAY first
            # when we involve iteration, we mean that number of GATEWAY will be limit through time.
            # for instance, GATEWAY will allow 3 in first three minutes. GATEWAY will allow 5 in first five minutes
            # 165/165 = 1
            elif len(self.units(GATEWAY)) <= ((self.iteration/self.ITERATIONS_PER_MINUTS)/2) and \
                    self.can_afford(GATEWAY) and \
                    not self.already_pending(GATEWAY):
                    await self.build(GATEWAY, near=pylon)
            # ***********************Build GATWAY and CYBERNETICSCOR**************************************

            # ***********************Build STARGATE**************************************
            # CYBER is the prerequist for building STARGATE
            if self.units(CYBERNETICSCORE).ready.exists and \
                len(self.units(STARGATE)) < ((self.iteration / self.ITERATIONS_PER_MINUTS)/2) and \
                self.can_afford(STARGATE) and \
                not self.already_pending(STARGATE):
                await self.build(STARGATE, near=pylon)
            # ***********************Build STARGATE**************************************

    # function to train army
    async def train_offensive_force(self):
        """
        all the units are train in this function
        :return:
        """
        # GATEWAY is producing construction and can train STALKER
        # pick one of GATEWAY to produce STALKER, and VOIDRAY have priority to produce
        for gw in self.units(GATEWAY).ready.idle:
            # we want the number of VOIDRAY is always smaller than STALKER
            if not self.units(STALKER).amount > self.units(VOIDRAY).amount \
                    and self.can_afford(STALKER) \
                    and self.supply_left > 0:
                await self.do(gw.train(STALKER))

        for sg in self.units(STARGATE).ready.idle:
            if self.can_afford(STARGATE) and self.supply_left > 0:
                await self.do(sg.train(VOIDRAY))


    # return a taget (enemy or structure) for
    def find_target(self, state):
        """
        This is not
        :param state:
        :return:
        -------
        return will be a target from enemy or structure
        """
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    # this is attach function
    async def attack_enemy(self):
        """
        There is a BotAI attribution named (attack), try to not use duplication name
        You don't want to send every unit into battle immeditaly,
        Instead, we want to sent them when they accumulate some amount and send together
        :return:
        """
        # {UNIT : [n to fight , n to defend]}
        aggressive_units = {STALKER:[15,3],
                            VOIDRAY:[8,3]}
        for UNIT in aggressive_units:
            # if we have more than 15/8 STALKER/VOIDRAY, we will attack
            if self.units(UNIT).amount > aggressive_units[UNIT][0]:
                # and self.units(UNIT).amount > aggressive_units[UNIT][1]
                for s in self.units(UNIT).idle:
                    await self.do(s.attack(self.find_target(self.state)))
            elif self.units(UNIT).amount > aggressive_units[UNIT][1] \
                and len(self.known_enemy_units) > 0:
                for s in self.units(UNIT).idle:
                    await self.do(s.attack(random.choice(self.known_enemy_units)))



        # # **********************************OLD ATTACK VERSION*******************************************
        # if self.units(STALKER).amount > 15:
        #     for s in self.units(STALKER).idle:
        #         await self.do(s.attack(self.find_target(self.state)))
        #
        # if self.units(STALKER).amount > 3:
        #     # add this to avoid
        #     if len(self.known_enemy_units) > 0:
        #         # chooes each idle STALKER to attack
        #         for s in self.units(STALKER).idle:
        #             # attach list of known enemy and structures
        #             await self.do(s.attack(random.choice(self.known_enemy_units)))
        # # **********************************OLD ATTACK VERSION*******************************************


#*********************************Variets of main()****************************************
def main():
    """
    Basic run_game only change on_step() and provide workers to mining automatically
    :return:
    """
    # run speed = Faluse = ultul fast
    # second list is the list of players, first is default AI
    # when this part running, we will have two windows, First is Bot, which is
    run_game(
        maps.get("AbyssalReefLE"),
        [Bot(Race.Protoss, SentdeBot()),
        Computer(Race.Terran, Difficulty.Easy)]
        ,realtime=True
        )

def test_two_computer_main():
    """
    Can't let two built-in computerAI to combat
    :return:
    """
    run_game(
        maps.get("AbyssalReefLE"), \
        [Bot(Race.Protoss, SentdeBot()), \
        Computer(Race.Terran, Difficulty.Easy)], \
        realtime=True \
        )

def two_windows():
    """
    Runing two games windows, Bot() is our AI. Human() is human control
    :return:
    """
    run_game(maps.get("AbyssalReefLE"), \
             [Human(Race.Terran), \
              Bot(Race.Zerg, SentdeBot())], \
              realtime=True)

def probe_build_main():
    run_game(
        maps.get("AbyssalReefLE"),
        [
            # Bot is my AI control and we call SentdeBot to destribute workers
            Bot(Race.Protoss, Bot1()),
            # Computer is build-in BOT with easy difficulty
            Computer(Race.Protoss, Difficulty.Easy)
        ],
        realtime=False
    )
#*********************************Variets of main()****************************************


if __name__=='__main__':
    # main()
    # test_two_computer_main()
    # two_windows()
    probe_build_main()










