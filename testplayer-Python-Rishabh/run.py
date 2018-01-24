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
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)

my_team = gc.team()
other_team=bc.Team.Blue
if my_team==bc.Team.Blue:
    other_team=bc.Team.Red

def factory(unit):
    garrison = unit.structure_garrison()
    if len(garrison) > 0:
        d = random.choice(directions)
        if gc.can_unload(unit.id, d):
            #print('unloaded a {}}!'.format(garrison[-1].unit_type))
            gc.unload(unit.id, d)
            return
    elif gc.can_produce_robot(unit.id, bc.UnitType.Knight):
        gc.produce_robot(unit.id, bc.UnitType.Knight)
        print('produced a knight!')
        return

def rocket(unit, location, my_planet):
    #Spots 0 and 1 in the array represent x and y coordinates of potential mars launch coordinates.
    if(my_planet==bc.Planet.Mars):
        d=random.choice(directions)
        if gc.can_unload(unit.id,d):
            print("unloaded on mars")
            gc.unload(unit.id,d)
            return
        return
    x=rocketLocation[0]
    y=rocketLocation[1]
    if len(unit.structure_garrison())==8 or (
        len(gc.sense_nearby_units_by_team(location.map_location(),2,other_team))!=0 and
        len(unit.structure_garrison())>=1):
        while gc.starting_map(my_planet.other()).is_passable_terrain_at(bc.MapLocation(my_planet.other(),x,y))==False:
            x+=1
            if(x%(gc.starting_map(my_planet.other()).width)==0):
                x=0
                y+=1
        if gc.can_launch_rocket(unit.id, bc.MapLocation(my_planet.other(), x,y)):
            gc.launch_rocket(unit.id, bc.MapLocation(my_planet.other(), x,y))
            x+=1
            if(x%(gc.starting_map(my_planet.other()).width)==0):
                x=0
                y+=1
            rocketLocation[0]=x
            rocketLocation[1]=y
            return
    nearby=gc.sense_nearby_units_by_team(location.map_location(),1,my_team)
    if(len(nearby)!=0):
        for rob in nearby:
            if(gc.can_load(unit.id,rob.id)):
                gc.load(unit.id,rob.id)
    return

def worker(unit, location, my_planet):
    if(my_planet==bc.Planet.Mars):

            x=random.random()

            if x>0.6 and team_karbonite>200:
                
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
    if location.is_on_map() and not location.is_in_garrison():
        nearby = gc.sense_nearby_units(location.map_location(), 2)
        for other in nearby:
            if gc.can_build(unit.id, other.id):
                gc.build(unit.id, other.id)
                #print('built a factory!')
                return
    # okay, there weren't any dudes around
    # pick a random direction:
    d = random.choice(directions)
    x=random.random()
    if x>0.99:
        if gc.can_replicate(unit.id,d):
            gc.replicate(unit.id,d)
    n=random.randint(0,1)

    # or, try to build a factory:
    if(n>0.5):
        if len(gc.sense_nearby_units_by_team(location.map_location(),30,other_team))==0 and gc.can_blueprint(unit.id,bc.UnitType.Rocket,d) and gc.karbonite()>bc.UnitType.Rocket.blueprint_cost():
            gc.blueprint(unit.id,bc.UnitType.Rocket,d)
        elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
            gc.move_robot(unit.id, d)
    else:
        if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
            gc.blueprint(unit.id, bc.UnitType.Factory, d)
        elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
            gc.move_robot(unit.id, d)

        if(unit.unit_type==bc.UnitType.Knight):
            nearby = gc.sense_nearby_units_by_team(location.map_location(), 70, other_team);
            for other in nearby:
                if gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                    print('attacked a thing!')
                    gc.attack(unit.id, other.id)
                    return
        ######################## end of knight code
def knight(unit, location, my_planet):
    nearby = gc.sense_nearby_units_by_team(location.map_location(),30,other_team);
    minDistance=0
    minUnit=None
    attacked=False
    for other in nearby:
        if gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
            print('attacked a thing!')
            gc.attack(unit.id, other.id)
            attacked=True
            return
        else:
            tempDistance=location.map_location().distance_squared_to(other.location.map_location())
            if tempDistance<minDistance or minDistance==0:
                minDistance=tempDistance
                minUnit=other
    if(len(nearby)>0):
        tempDir=location.map_location().direction_to(minUnit.location.map_location())
        if gc.is_move_ready(unit.id) and gc.can_move(unit.id,tempDir):
            gc.move_robot(unit.id,tempDir)
    else:
        nearby_rockets=gc.sense_nearby_units_by_type(location.map_location(), 10, bc.UnitType.Rocket)
        minRocket=None
        minDistance=0
        for rocket in nearby_rockets:
            tempDist=location.map_location().distance_squared_to(rocket.location.map_location())
            if rocket.team==my_team and (tempDist<minDistance or minDistance==0) and len(rocket.structure_garrison())<8 and not rocket.rocket_is_used():
                minRocket=rocket
                minDistance=tempDist
        if minRocket is not None:
            tempDir=location.map_location().direction_to(minRocket.location.map_location())
            if gc.is_move_ready(unit.id) and gc.can_move(unit.id,tempDir):
                gc.move_robot(unit.id,tempDir)
        else:
            if (not rally_loc==None):
                direc=location.map_location().direction_to(rally_loc)
                if gc.can_move(unit.id,direc):
                    gc.move(unit.id,direc)
            else:
                d=random.choice(directions)
                if gc.is_move_ready(unit.id) and gc.can_move(unit.id,d):
                    gc.move_robot(unit.id,d)

def main():
    team_karbonite=gc.karbonite()
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
