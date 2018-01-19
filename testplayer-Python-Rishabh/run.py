import battlecode as bc
import random
import sys
import traceback
import pdb
import os
print(os.getcwd())

print("pystarting")
#i am just testing if i can push
# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()

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

while True:
    # We only support Python 3, which means brackets around print()
    #print('pyround:', gc.round())

    # frequent try/catches are a good idea
    try:
        # walk through our units:
        for unit in gc.my_units():

            if location.is_in_space():
                continue

            # first, factory logic
            ######################## factory code
            if unit.unit_type == bc.UnitType.Factory:
                garrison = unit.structure_garrison()
                if len(garrison) > 0:
                    d = random.choice(directions)
                    if gc.can_unload(unit.id, d):
                        print('unloaded a {}}!'.format(garrison[-1].unit_type))
                        gc.unload(unit.id, d)
                        continue
                elif gc.can_produce_robot(unit.id, bc.UnitType.Knight):
                    gc.produce_robot(unit.id, bc.UnitType.Knight)
                    print('produced a knight!')
                    continue
            ######################## end of factory code

            location = unit.location
            my_planet=location.map_location().planet

            ######################## rocket code
            if unit.unit_type==bc.UnitType.Rocket:
                #print(my_planet)
                #Spots 0 and 1 in the array represent x and y coordinates of potential mars launch coordinates.
                #team_array=gc.get_team_array(location.map_location().planet)
                if(my_planet==bc.Planet.Mars):
                    d=random.choice(directions)
                    if gc.can_unload(unit.id,d):
                        print("unloaded on mars")
                        gc.unload(unit.id,d)
                        continue


                    # for i in range(100):
                    #     print("I'm on mars!!!!!")
                    #     print(location)
                    #     print(str(team_array[0])+"  "+str(team_array[1]))
                    continue

                #x=team_array[0]
                #y=team_array[1]
                x=rocketLocation[0]
                y=rocketLocation[1]
                if len(unit.structure_garrison())==8 or (
                    len(gc.sense_nearby_units_by_team(location.map_location(),2,other_team))!=0 and
                    len(unit.structure_garrison())>=1):
                    # print("Starting launch sequence")
                    while gc.starting_map(my_planet.other()).is_passable_terrain_at(bc.MapLocation(my_planet.other(),x,y))==False:
                        # print("fkfsdlkd")
                        x+=1
                        if(x%(gc.starting_map(my_planet.other()).width)==0):
                            x=0
                            y+=1

                    if gc.can_launch_rocket(unit.id, bc.MapLocation(my_planet.other(), x,y)):

                        gc.launch_rocket(unit.id, bc.MapLocation(my_planet.other(), x,y))
                        #print("Temp Array Values: {} {}".format(team_array[0],team_array[1]))
                        #print("Destination: {} {}".format(x,y))
                        x+=1
                        #pdb.set_trace()
                        if(x%(gc.starting_map(my_planet.other()).width)==0):
                            x=0
                            y+=1

                        rocketLocation[0]=x
                        rocketLocation[1]=y

                        continue;
                nearby=gc.sense_nearby_units_by_team(location.map_location(),1,my_team)
                if(len(nearby)!=0):
                    for rob in nearby:
                        if(gc.can_load(unit.id,rob.id)):
                            gc.load(unit.id,rob.id)
                continue
                #Improvements: Selectively load units into the rocket.
            ######################## end of rocket code


            ######################## worker code
            if(unit.unit_type==bc.UnitType.Worker):
                if(my_planet==bc.Planet.Mars):
                        # Mining Code
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
                        if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                            gc.build(unit.id, other.id)
                            #print('built a factory!')
                            # move onto the next unit
                            continue

                # okay, there weren't any dudes around
                # pick a random direction:
                d = random.choice(directions)
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
                    # and if that fails, try to move
                    elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                        gc.move_robot(unit.id, d)
            ######################## worker code

            ######################## knight code
            if(unit.unit_type==bc.UnitType.Knight):
                nearby = gc.sense_nearby_units_by_team(location.map_location(),30,other_team);
                for other in nearby:
                    if gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                        print('attacked a thing!')
                        gc.attack(unit.id, other.id)
                        continue
            ######################## end of knight code

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
