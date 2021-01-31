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



class Bot2(sc2.BotAI):


    async def build_assimilator(self):
        """

        :return:
        """
        for nexus in self.unit(NEXUS).ready:
            # looking for any vespense_geyser are colse to nexus in 25 unit distance
            vaspenses = self.state.vespene_geyser.closer_than(25.0, nexus)
        return vaspenses


vas = Bot2()
print(vas)