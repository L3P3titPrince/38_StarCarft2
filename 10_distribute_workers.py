"""
Sources
YouTube:https://www.youtube.com/watch?v=v3LJ6VvpfgI&list=PLQVvvaa0QuDcT3tPehHdisGMc8TInNqdq&index=2&t=0s&ab_channel=sentdex
zhihu.com:https://zhuanlan.zhihu.com/p/33897686
zhihu.com:https://zhuanlan.zhihu.com/p/100032133
SC2AI_github:https://github.com/ClausewitzCPU0/SC2AI
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

import sc2
# Race = Terran, Zerg, Protoss
# run_game used to lanuch game and assign launch parameters
# maps to denote which map will be used
# Difficuly to choose computer level
from sc2 import run_game, maps, Race, Difficulty
# Bot is our AI algorithm and Computer is build-in computerAI, Human is player control
from sc2.player import Bot, Computer, Human
# NEXUS is the base of Protoss, PROBE is the worker of Protoss, PYLON is the population state fo Protoss
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR

class SentdeBot(sc2.BotAI):
    """
    Inherit CLASS sc2.BotAI, some method will be involoved
    """
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

class Bot1(sc2.BotAI):
    """
    build workers and pylons
    """
    async def on_step(self, iteration: int):
        # distribute_workers() is build in function which can inherited from sc2.BotAI
        await self.distribute_workers()
        # this is my self-def function, need declare in this on_step() function
        await self.build_workers()
        # this is my self-def function, need declare in this on_step() function
        await self.build_pylons()
        # build assimilators
        await self.build_assimilator()
        # we have self.expand_now, but we still build our own expand function
        # await self.manual_expand()

    async def build_workers(self):
        """
        Select idel base and build workers
        noqueue means current building sequence is empty
        :return:
        """
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
            vaspenes = self.state.vespene_geyser.closer_than(25.0, nexus)
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

    # async def manual_expand(self):
    #     """
    #
    #     :return:
    #     """
    #     if self.units(NEXUS).amount < 3 and self.can_afford(NEXUS):
    #         await self.expand_now()


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
        realtime=True
    )
#*********************************Variets of main()****************************************


if __name__=='__main__':
    # main()
    # test_two_computer_main()
    # two_windows()
    probe_build_main()










