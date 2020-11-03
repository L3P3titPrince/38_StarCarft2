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
from sc2 import run_game, maps, Race, Difficulty
# bot is us and computer is computerAI
from sc2.player import Bot, Computer

class SentdeBot(sc2.BotAI):
    async def on_step(self, iteration):
        """
        Every step we goona to do
        :param iteration:
        :return:
        """
        # you start with 12 workers and tell them what to do
        # intellgience distribute workders for gas no more than three
        await self.distribute_workers()

# run speed = Faluse = ultul fast
# second list is the list of players, first is default AI
run_game(maps.get("AbyssalReefLE"), \
         [Bot(Race.Protoss, SentdeBot()), \
          Computer(Race.Terran, Difficulty.Easy)] \
         ,realtime=True \
         )














