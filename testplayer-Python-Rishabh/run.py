import battlecode as bc
import random
import sys
import traceback
import pdb
import os
print(os.getcwd())

print("pystarting")
rally_loc=None
# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
team_karbonite=0

directions = list(bc.Direction)

print("pystarted")

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
random.seed(6137)
rocketLocation=[0,0]
# let's start off with some research!
# we can queue as much as we want.

gc.queue_research(bc.UnitType.Rocket)#100
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Knight)#200
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Ranger)#325
gc.queue_research(bc.UnitType.Mage)#350
gc.queue_research(bc.UnitType.Worker)#375

my_team = gc.team()
other_team=bc.Team.Blue
if my_team==bc.Team.Blue:
    other_team=bc.Team.Red
earth=gc.starting_map(bc.Planet.Earth)
x_opp_center=0
y_opp_center=0

for un in earth.initial_units:
    if un.team==other_team:
        x_opp_center+=un.location.map_location().x/2
        y_opp_center+=un.location.map_location().y/2
x_opp_center=int(x_opp_center)
y_opp_center=int(y_opp_center)

def factory(unit):
    garrison = unit.structure_garrison()
    if len(garrison) > 0:
        d = random.choice(directions)
        if gc.can_unload(unit.id, d):
            #print('unloaded a {}}!'.format(garrison[-1].unit_type))
            gc.unload(unit.id, d)

    x = random.random()
    if x<0.3:
        if gc.can_produce_robot(unit.id, bc.UnitType.Knight):
            gc.produce_robot(unit.id, bc.UnitType.Knight)
            print('produced a Knight!')
    elif x<0.7:
        if gc.can_produce_robot(unit.id, bc.UnitType.Ranger):
            gc.produce_robot(unit.id, bc.UnitType.Ranger)
            print('produced a Ranger!')
    elif x<0.9:
        if gc.can_produce_robot(unit.id, bc.UnitType.Worker):
            gc.produce_robot(unit.id, bc.UnitType.Worker)
            print('produced a Worker!')
    elif x<1:
        if gc.can_produce_robot(unit.id, bc.UnitType.Mage):
            gc.produce_robot(unit.id, bc.UnitType.Mage)
            print('produced a Mage!')
    return

def rocket(unit, location, my_planet):
    #Spots 0 and 1 in the array represent x and y coordinates of potential mars launch coordinates.
    if(my_planet==bc.Planet.Mars):
        for d in directions:
           #d=random.choice(directions)
            if gc.can_unload(unit.id,d):
                print("unloaded on mars")
                gc.unload(unit.id,d)
                return
        return
    x=rocketLocation[0]
    y=rocketLocation[1]
    if len(unit.structure_garrison())==unit.structure_max_capacity() or (
        len(gc.sense_nearby_units_by_team(location.map_location(),50,other_team))!=0 and
        len(unit.structure_garrison())>=1) or gc.round()>=749:
        print("{}: {}".format(x,y))

        while gc.starting_map(bc.Planet.Mars).is_passable_terrain_at(bc.MapLocation(bc.Planet.Mars,x,y))==False:
            x+=2
            if(x>=(gc.starting_map(bc.Planet.Mars).width)):
                x=x%(gc.starting_map(bc.Planet.Mars).width)
                y+=1
        if gc.can_launch_rocket(unit.id, bc.MapLocation(bc.Planet.Mars, x,y)):
            gc.launch_rocket(unit.id, bc.MapLocation(bc.Planet.Mars, x,y))
            x+=2
            if(x>=(gc.starting_map(bc.Planet.Mars).width)):
                x=x%(gc.starting_map(bc.Planet.Mars).width)
                y+=1
            rocketLocation[0]=x
            rocketLocation[1]=y
            return
    nearby=gc.sense_nearby_units_by_team(location.map_location(),2,my_team)
    d={}
    for un in unit.structure_garrison():
        typ=gc.unit(un).unit_type
        if typ in d.keys():
            d[typ]+=1
        else:
            d[typ]=1
    if(len(nearby)!=0):
        for rob in nearby:
            if (bc.UnitType.Worker not in d or not rob.unit_type==bc.UnitType.Worker):
                if(gc.can_load(unit.id,rob.id)):
                    gc.load(unit.id,rob.id)
    return

def worker(unit, location, my_planet):
    global team_karbonite
    if(my_planet==bc.Planet.Mars):
            x=random.random()
            if (x>0.6 and team_karbonite>300) or gc.round()>=900:
                print("karbonite")
                for d in directions:
                    if gc.can_replicate(unit.id,d):
                        gc.replicate(unit.id,d)
                        team_karbonite-=30
                        break
            for d in directions:
                if gc.can_harvest(unit.id,d):
                    gc.harvest(unit.id,d)
                    print("Karbonite: {}".format(gc.karbonite()))
            direc=random.choice(directions)
            if gc.is_move_ready(unit.id) and gc.can_move(unit.id, direc):
                gc.move_robot(unit.id, direc)
    
    d = random.choice(directions)

    nearby = gc.sense_nearby_units(location.map_location(), 2)
    for other in nearby:
        if gc.can_build(unit.id, other.id):
            gc.build(unit.id, other.id)
            #print('built a factory!')
            if gc.can_replicate(unit.id,d):
                gc.replicate(unit.id,d)
            return
    # okay, there weren't any dudes around
    # pick a random direction:
    
    x=random.random()
    if x>0.99 or (gc.round()<15 and location.map_location().distance_squared_to(bc.MapLocation(my_planet,x_opp_center,y_opp_center))>30):
        if gc.can_replicate(unit.id,d):
            gc.replicate(unit.id,d)
    n=random.randint(0,1)

    # or, try to build a factory:

    if(n>0.5):
        if len(gc.sense_nearby_units_by_team(location.map_location(),30,other_team))==0 and gc.can_blueprint(unit.id,bc.UnitType.Rocket,d) and gc.karbonite()>bc.UnitType.Rocket.blueprint_cost():
            gc.blueprint(unit.id,bc.UnitType.Rocket,d)
        else:
            for direc in directions:
                if gc.can_harvest(unit.id,direc):
                    gc.harvest(unit.id,direc)
                    return
            if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                gc.move_robot(unit.id, d)
    else:
        if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
            gc.blueprint(unit.id, bc.UnitType.Factory, d)
        else:
            for direc in directions:
                if gc.can_harvest(unit.id,direc):
                    gc.harvest(unit.id,direc)
                    return
            if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                gc.move_robot(unit.id, d)

       

def knight(unit, location, my_planet):
    nearby = gc.sense_nearby_units_by_team(location.map_location(),30,other_team);
    minDistance=0
    minUnit=None
    attacked=False
    for other in nearby:
        if gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
            print('knight attacked a thing!')
            gc.attack(unit.id, other.id)
            attacked=True
            return
        else:
            tempDistance=location.map_location().distance_squared_to(other.location.map_location())
            if tempDistance<minDistance or minDistance==0 and gc.can_move(unit.id,location.map_location().direction_to(other.location.map_location())):
            #if ((tempDistance<minDistance or minDistance==0) and (minUnit is None or gc.can_move(unit.id,location.map_location().direction_to(minUnit.location.map_location()))):
                minDistance=tempDistance
                minUnit=other
    if(minUnit is not None):
        tempDir=location.map_location().direction_to(minUnit.location.map_location())
        if gc.is_move_ready(unit.id) and gc.can_move(unit.id,tempDir):
            gc.move_robot(unit.id,tempDir)
    else:
        nearby_rockets=gc.sense_nearby_units_by_type(location.map_location(), 10, bc.UnitType.Rocket)
        minRocket=None
        minDistance=0
        if my_planet==bc.Planet.Earth:
            for rocket in nearby_rockets:
                tempDist=location.map_location().distance_squared_to(rocket.location.map_location())
                if rocket.team==my_team and (tempDist<minDistance or minDistance==0) and len(rocket.structure_garrison())<8 and not rocket.rocket_is_used():
                    minRocket=rocket
                    minDistance=tempDist
        if minRocket is not None:
            tempDir=location.map_location().direction_to(minRocket.location.map_location())
            if gc.is_move_ready(unit.id) and gc.can_move(unit.id,tempDir):
                gc.move_robot(unit.id,tempDir)
        elif gc.is_move_ready(unit.id):
            """"
            if (not rally_loc==None):
                direc=location.map_location().direction_to(rally_loc)
                if gc.can_move(unit.id,direc):
                    gc.move(unit.id,direc)
            """
            rally=False
            if my_planet==bc.Planet.Earth and gc.round()>150:
                tempDirect=location.map_location().direction_to(bc.MapLocation(bc.Planet.Earth,x_opp_center,y_opp_center))
                if gc.can_move(unit.id,tempDirect):
                    gc.move_robot(unit.id,tempDirect)
                    rally=True
            if not rally:
                d=random.choice(directions)
                if gc.is_move_ready(unit.id) and gc.can_move(unit.id,d):
                    gc.move_robot(unit.id,d)

#Ranger Code
def ranger_dot(rang, our_knight, their_unit):
    res=0 
    res+=((their_unit.x-rang.x)*(our_knight.x-rang.x))
    res+=((their_unit.y-rang.y)*(our_knight.y-rang.y))
    return res
    
def ranger(unit,location):# This should be the final version. 
    nearby = gc.sense_nearby_units_by_team(location.map_location(),unit.vision_range,other_team);
    minDistance=0
    minUnitDistance=None
    minUnitAttack=None
    minAttackQuotient=None
    attacked=False
    attack_possible=False
    minFriendlyDistance=0
    minFriendlyUnit=None
    for other in nearby:
        
#We need to check which of robots in range has lowest health. Attack that one.
#We also need to move away from knights that are close.
#We should target rockets.
        
        if other.unit_type==bc.UnitType.Knight and location.map_location().is_adjacent_to(other.location.map_location()):
            #print("fjksd")
            tempDirKnight=other.location.map_location().direction_to(location.map_location())
            if gc.is_move_ready(unit.id) and gc.can_move(unit.id,tempDirKnight):
                gc.move_robot(unit.id,tempDirKnight)
        if gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
            testQuot=(location.map_location().distance_squared_to(other.location.map_location())
                /unit.vision_range) * (other.health/other.max_health)
            if(minAttackQuotient is None or testQuot<minAttackQuotient ):
                minAttackQuotient=testQuot
                minUnitAttack=other
            attack_possible=True
            # print('attacked a thing!')
            # gc.attack(unit.id, other.id)
            # attacked=True
            # return
        else:
            if not attack_possible:
                tempDistance=location.map_location().distance_squared_to(other.location.map_location())
                if tempDistance<minDistance or minDistance==0:
                    minDistance=tempDistance
                    minUnitDistance=other

    if minUnitAttack is not None:
        gc.attack(unit.id,minUnitAttack.id)
        attacked=True
    elif minUnitDistance is not None:
        tempDir=location.map_location().direction_to(minUnitDistance.location.map_location())
        nearby_friendly=gc.sense_nearby_units_by_team(location.map_location(),unit.vision_range,my_team)
        closest=True
        for u in nearby:
            if minUnitDistance.location.map_location().distance_squared_to(u.location.map_location())<minDistance:
                closest=False


        if gc.is_move_ready(unit.id) and gc.can_move(unit.id,tempDir) and not closest:
            gc.move_robot(unit.id,tempDir)

    elif gc.is_move_ready(unit.id):
        nearby_rockets=gc.sense_nearby_units_by_type(location.map_location(), 10, bc.UnitType.Rocket)
        minRocket=None
        minDistance=0
        if location.map_location().planet==bc.Planet.Earth:
            for rocket in nearby_rockets:
                tempDist=location.map_location().distance_squared_to(rocket.location.map_location())
                if rocket.team==my_team and (tempDist<minDistance or minDistance==0) and len(rocket.structure_garrison())<8 and not rocket.rocket_is_used():
                    minRocket=rocket
                    minDistance=tempDist
        if minRocket is not None:
            tempDir=location.map_location().direction_to(minRocket.location.map_location())
            if gc.is_move_ready(unit.id) and gc.can_move(unit.id,tempDir):
                gc.move_robot(unit.id,tempDir)
        elif len(gc.sense_nearby_units_by_team(location.map_location(),location.map_location().distance_squared_to(bc.MapLocation(bc.Planet.Earth,x_opp_center,y_opp_center)),my_team))>0:
            rally=False
            if location.map_location().planet==bc.Planet.Earth and gc.round()>150:
                tempDirect=location.map_location().direction_to(bc.MapLocation(bc.Planet.Earth,x_opp_center,y_opp_center))
                if gc.can_move(unit.id,tempDirect):
                    gc.move_robot(unit.id,tempDirect)
                    rally=True
            if rally is not True:
                for d in directions:
                    if gc.is_move_ready(unit.id) and gc.can_move(unit.id,d) :
                        gc.move_robot(unit.id,d) 
                        break

"""
def ranger(unit, location):
    nearby = gc.sense_nearby_units_by_team(location.map_location(),unit.vision_range,other_team);
    minDistance=0
    minUnitDistance=None
    minUnitAttack=None
    minAttackQuotient=None
    attacked=False
    attack_possible=False
    for other in nearby:
        escaped=False
    #We need to check which of robots in range has lowest health. Attack that one.
    #We also need to move away from knights that are close.
    #We should target rockets.
        if (other.unit_type==bc.UnitType.Knight and location.map_location().distance_squared_to(other.location.map_location())<=1):
            tempDirKnight=location.map_location().direction_to(other.location.map_location())
            if gc.is_move_ready(unit.id) and gc.can_move(unit.id,tempDirKnight):
                gc.move_robot(unit.id,tempDirKnight)
        if gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
            testQuot=(location.map_location().distance_squared_to(other.location.map_location())
                /unit.vision_range) * (other.health/other.max_health)
            if(minAttackQuotient is None or testQuot<minAttackQuotient):
                minAttackQuotient=testQuot
                minUnitAttack=other
            attack_possible=True
            # print('attacked a thing!')
            # gc.attack(unit.id, other.id)
            # attacked=True
            # return
        else:
            if not attack_possible:
                tempDistance=location.map_location().distance_squared_to(other.location.map_location())
                if tempDistance<minDistance or minDistance==0:
                    minDistance=tempDistance
                    minUnitDistance=other
    if minUnitAttack is not None:
        gc.attack(unit.id,minUnitAttack.id)
        attacked=True
    elif minUnitDistance is not None:
        tempDir=location.map_location().direction_to(minUnitDistance.location.map_location())
        if gc.is_move_ready(unit.id) and gc.can_move(unit.id,tempDir):
            gc.move_robot(unit.id,tempDir)
"""
"""
def ranger(unit, location):
    nearby = gc.sense_nearby_units_by_team(location.map_location(),unit.vision_range,other_team);
    minDistance=0
    minUnitDistance=None
    minUnitAttack=None
    minAttackQuotient=None
    attacked=False
    attack_possible=False
    for other in nearby:
        escaped=False
    #We need to check which of robots in range has lowest health. Attack that one.
    #We also need to move away from knights that are close.
    #We should target rockets.
        if gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
            testQuot=(location.map_location().distance_squared_to(other.location.map_location())
                /unit.vision_range) * (other.health/other.max_health)
            if(minAttackQuotient is None or testQuot<minAttackQuotient):
                minAttackQuotient=testQuot
                minUnitAttack=other
            attack_possible=True
            # print('attacked a thing!')
            # gc.attack(unit.id, other.id)
            # attacked=True
            # return
        else:
            if not attack_possible:
                tempDistance=location.map_location().distance_squared_to(other.location.map_location())
                if tempDistance<minDistance or minDistance==0:
                    minDistance=tempDistance
                    minUnitDistance=other
    if minUnitAttack is not None:
        gc.attack(unit.id,minUnit.id)
        attacked=True
    elif minUnitDistance is not None:
        tempDir=location.map_location().direction_to(minUnit.location.map_location())
        if gc.is_move_ready(unit.id) and gc.can_move(unit.id,tempDir):
            gc.move_robot(unit.id,tempDir)
"""

def things_that_need_to_be_done_each_turn():
    random.shuffle(directions)
    global team_karbonite
    team_karbonite = gc.karbonite()
    units_on_team = gc.my_units()
    num_units = len([i for i in units_on_team if i.unit_type == bc.UnitType.Worker])

def main():

    #print(bc.MapLocation(bc.Planet.Earth,1,2).is_adjacent_to(bc.MapLocation(bc.Planet.Earth,2,3)))
    things_that_need_to_be_done_each_turn()
    for unit in gc.my_units():
        if(unit.unit_type==bc.UnitType.Factory):
            factory(unit)

        location = unit.location
        if (location.is_in_space() or location.is_in_garrison()):
            continue
        my_planet=location.map_location().planet

        if(unit.unit_type==bc.UnitType.Rocket):
            rocket(unit, location, my_planet)

        elif(unit.unit_type==bc.UnitType.Worker):
            worker(unit, location, my_planet)

        elif(unit.unit_type==bc.UnitType.Knight):
            knight(unit, location, my_planet)

        elif(unit.unit_type==bc.UnitType.Ranger):
            ranger(unit, location)
        elif(unit.unit_type==bc.UnitType.Mage):
            ranger(unit,location)

while True:
    # We only support Python 3, which means brackets around print()
    #print('pyround:', gc.round())

    # frequent try/catches are a good idea
    try:
        # walk through our units:
        main()

    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()
