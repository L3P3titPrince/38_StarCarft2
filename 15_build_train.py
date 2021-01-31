"""
Env and package initial 
conda create 10_starcraft2
conda activate 10_starcraft2
# using pip without --user will only install in conda env when special envirnemnt is activate
pip install --upgrade sc2

"""

import random
import cv2
import sc2
import numpy as np
# Race = Terran, Zerg, Protoss
# run_game used to lanuch game and assign launch parameters
# maps to denote which map will be used
# Difficulty to choose computer level
from sc2 import run_game, maps, Race, Difficulty, position, Result
# NEXUS is the base of Protoss, PROBE is the worker of Protoss, PYLON is the population state fo Protoss
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, CYBERNETICSCORE, \
    STARGATE, VOIDRAY, OBSERVER, ROBOTICSFACILITY
# Bot is our AI algorithm and Computer is build-in computerAI, Human is player control
from sc2.player import Bot, Computer, Human


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
        # set the max limitation of workers
        self.MAX_WORKERS = 80
        self.do_somethin_after = 0
        # train_data
        self.train_data = []

    # can not find a better way to get game result?
    def on_end(self, game_result):
        print("----on_end called-----")
        print(game_result)
        # we only save data when we win
        if game_result == Result.Victory:
            np.save("train_data/{}.npy".format(str(int(time.time()))), np.array(self.train_data))

    # 165 iterations per minute (not sure its right)
    async def on_step(self, iteration):
        self.iteration = iteration
        # declare scout() as primary function
        await self.scout()
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
        # visulization with opencv
        await self.open_cv()

    def random_location_variance(self, enemy_start_location):
        """

        :param enemy_start_location: Enenmy initial set up base postion
        :return:
        """
        x = enemy_start_location[0]
        y = enemy_start_location[1]

        x += ((random.randrange(-30,30))/100) * enemy_start_location[0]
        y += ((random.randrange(-30,30))/100) * enemy_start_location[1]

        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x > self.game_info.map_size[0]:
            x = self.game_info.map_size[0]
        if y > self.game_info.map_size[1]:
            y = self.game_info.map_size[1]

        go_to = position.Point2(position.Pointlike((x,y)))
        return go_to


    # scout part
    async def scout(self):
        """

        :return:
        """
        if len(self.units(OBSERVER)) > 0:
            # due to unit is a list, so when we assign the first one to scout, next unit will be idle.
            # so this function will assign socout task like a sequence
            scout_unit = self.units(OBSERVER)[0]
            if scout_unit.is_idle:
                enemy_location = self.enemy_start_locations[0]
                # it's like a move around
                move_to = self.random_location_variance(enemy_location)
                print(move_to)
                await self.do(scout_unit.move(move_to))
        else:
            # if we don't have observer, we need let ROBOTICSFACLIFTY to train one
            for rf in self.units(ROBOTICSFACILITY).ready.idle:
                if self.can_afford(OBSERVER) and self.supply_left > 0:
                    await self.do(rf.train(OBSERVER))


    # visulization minimap with opencv
    async def open_cv(self):
        """

        :return:
        """
        # # get all help and info
        # print('dir:', dir)
        # provide map length and width.
        # For starcraft2, map_info is width by height, which means column by rows.
        # When we describe a image, we always use width (长) and height(宽) to describe
        # For numppy.array, order is height by width, rows by column
        # Because starcraft map is color, so we build a (h,w,3) dimension matrix, each element is (255,255,255)
        # Basically, we got a empty zero matrix with shape(176, 200, 3), height=row=176, weight=columns=200
        game_map = np.zeros((self.game_info.map_size[1], self.game_info.map_size[0], 3), dtype=np.uint8)
        # print(f"height is {self.game_info.map_size[1]}")
        # print(f"width is {self.game_info.map_size[0]}")

        # UNIT: [SIZE, (BGR COLOR)]
        # try to use different shape and color to distinguish every unit and sturctures
        # So it will be more easy for CNN to recognize
        draw_dict = {
            NEXUS:[15, (0,255,0)],
            PYLON:[3, (20,235,0)],
            PROBE:[1, (55,200,0)],
            ASSIMILATOR:[2, (55,200,0)],
            GATEWAY:[3, (200,100,0)],
            CYBERNETICSCORE:[3, (150,150,0)],
            STARGATE:[5, (255,0,0)],
            VOIDRAY:[3,(255,100,0)]
        }
        # draw my every unit and structure by dictionary
        for unit_type in draw_dict:
            for unit in self.units(unit_type).ready:
                pos = unit.position
                cv2.circle(game_map, (int(pos[0]), int(pos[1])), \
                           draw_dict[unit_type][0], draw_dict[unit_type][1], -1)

        #*****************************ENEMY BUILDING*********************************
        # draw enemy's units and structure by dictionary
        main_base_names = ['nexus', 'commandcenter', 'hatchery']
        # maybe we can use different color to counter. That will be more relativity
        # maybe we can change structure, my untis are all circle, enemy are all square
        # use color to distinguish importance
        for enemy_building in self.known_enemy_structures:
            pos = enemy_building.position
            if enemy_building.name.lower() not in main_base_names:
                cv2.circle(game_map, (int(pos[0]),int(pos[1])), 5, (200,50,212), -1)
        for enemy_building in self.known_enemy_structures:
            pos = enemy_building.position
            if enemy_building.name.lower() in main_base_names:
                cv2.circle(game_map, (int(pos[0]),int(pos[1])), 5, (0,0,255), -1)
        # *****************************ENEMY BUILDING*********************************

        # *****************************ENEMY UNITS*********************************
        for enemy_unit in self.known_enemy_units:
            # if this one is unit, not structure
            if not enemy_unit.is_structure:
                worker_name = ['probe', 'scv', 'drone']
                # if that unit is a PROBE / SCV / DRONE, that's is a worker
                pos = enemy_unit.position
                if enemy_unit.name.lower() not in worker_name:
                    cv2.circle(game_map, (int(pos[0]),int(pos[1])), 1, (55,0,155), -1)
                if enemy_unit.name.lower() in worker_name:
                    cv2.circle(game_map, (int(pos[0]),int(pos[1])), 3, (55,0,215), -1)
        # *****************************ENEMY UNITS*********************************


        # draw OBERVER, as small as possible to emphasize the scout importance
        for obs in self.units(OBSERVER).ready:
            pos = obs.position
            cv2.circle(game_map, (int(pos[0]), int(pos[1])), 1 , (255,255,255), -1)


        # flip horizontally to make our final fix in visual representation:
        flipped = cv2.flip(game_map, 0)
        resized = cv2.resize(flipped, dsize=None, fx=3, fy=3)
        cv2.imshow("OpenCV", resized)
        # 1 ms
        cv2.waitKey(1)

        # #********************************OLD VERSION*********************************************
        # # Only draw circle from NEXUS on game_map
        # for nexus in self.units(NEXUS):
        #     nex_pos = nexus.position
        #     # draw circle on any image
        #     # draw nexus as a yellow (0,255,0) circle with filled color(thickness=-1) without line
        #     # image=game_data, center_coordinates=(h/row,w/column,3), radius=10, color=(0,255,0), thickness=-1
        #     cv2.circle(game_map, (int(nex_pos[0]), int(nex_pos[1])),10, (0,255,0),-1)
        # # opencv consider (0,0) as top left, but cooridinates consider (0,0) as bottom left,
        # # so we need to flip/roll-over image
        # flipped = cv2.flip(game_map, 0)
        # # depend on you resulstion
        # # mutiply coodinates x by 2 and coodinates y by 2
        # resized = cv2.resize(flipped, dsize=None, fx=2, fy=2)
        # cv2.imshow("OpenCV", resized)
        # # 1 ms
        # cv2.waitKey(1)
        # # self.game_info.map_size
        # # ********************************OLD VERSION*********************************************



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
            # maybe this colomn can omit this line
            nexuses = self.units(NEXUS).ready
            # gold can buy a py
            if nexuses.exists and self.can_afford(PYLON):
                # near is building location, we can use deep learning to optimize
                # our PYLON will bulid near NEXUES
                await self.build(PYLON, near=nexuses.first)

    async def build_assimilator(self):
        """
        This function is not well code organized, need to optimize
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

    # expand NEXUS(base) simple version
    async def manual_expand(self):
        """
        If we have less than 3 NEXUS and we have enough money, we will expand
        Check expand_now() for more detail
        :return:
        """
        if self.units(NEXUS).amount < 3 and self.can_afford(NEXUS):
            await self.expand_now()

    # build GATEWAY, CYBERNETICSOR, STARGATE
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
            elif len(self.units(GATEWAY)) < 1 \
                    and self.can_afford(GATEWAY) \
                    and not self.already_pending(GATEWAY):
                    await self.build(GATEWAY, near=pylon)
            # ***********************Build GATWAY and CYBERNETICSCOR**************************************

            # ***********************Build STARGATE**************************************
            # CYBER is the prerequist for building STARGATE
            if self.units(CYBERNETICSCORE).ready.exists and \
                len(self.units(STARGATE)) < (self.iteration / self.ITERATIONS_PER_MINUTS) and \
                self.can_afford(STARGATE) and \
                not self.already_pending(STARGATE):
                await self.build(STARGATE, near=pylon)
            # ***********************Build STARGATE**************************************


            #*************************Build ROBOTICSFACILTY********************************
            # In this version AI, ROBOTICSFACILITY is primarly to train observer
            if self.units(CYBERNETICSCORE).ready.exists \
                and len(self.units(ROBOTICSFACILITY)) < 1 \
                and self.can_afford(ROBOTICSFACILITY) \
                and not self.already_pending(ROBOTICSFACILITY):
                await self.build(ROBOTICSFACILITY, near=pylon)
            # *************************Build ROBOTICSFACILTY********************************
    # function to train army
    async def train_offensive_force(self):
        """
        all the units are train in this function
        :return:
        """
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
        aggressive_units = {VOIDRAY:[8,3]}
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










