##Rally point code
rally_loc=None

####More Factory Code
nearby = gc.sense_nearby_units_by_team(location.map_location(),30,other_team);
minDistance=0
minUnit=Unit()
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
    if gc.can_move(unit.id,tempDir):
        gc.move(unit.id,tempDir)
else:
	nearby_rockets=gc.sense_nearby_units_by_type(location.map_location(), 10, gc.UnitType.Rocket)
	minRocket=None
	minDistance=0
	for rocket in nearby_rockets:
		tempDist=location.map_location().distance_squared_to(rocket.location.map_location())
		if rocket.team==my_team and tempDist<minDistance and len(rocket.structure_garrison()<8):
			minRocket=rocket
			minDistance=tempDist
	if len(nearby_rockets)>0:
		tempDir=location.map_location().direction_to(minRocket.location.map_location())
	    if gc.can_move(unit.id,tempDir):
	        gc.move(unit.id,tempDir)
	else:
		if (not rally_loc==None):
			direc=location.map_location().direction_to(rally_loc)
			if gc.can_move(unit.id,direc):
				gc.move(unit.id,direc)
		else:
			d=random.choice(directions)
			if gc.can_move(unit.id,d):
				gc.move(unit.id,d)


	                   