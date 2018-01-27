#Ranger Code
def ranger(unit,location):
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
		if other.unit_type==bc.UnitType.Knight and location.map_location().distance_squared_to(other.location.map_location())<=1:
			tempDirKnight=other.map_location().direction_to(location.map_location())
	        if gc.is_move_ready(unit.id) and gc.can_move(unit.id,tempDirKnight):
	            gc.move_robot(unit.id,tempDir)
	    if gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
	    	testQuot=(location.map_location().distance_squared_to(other.location.map_location())
	    		/unit.vision_range) * (other.health/other.max_health)
	    	if(testQuot<minAttackQuotient or minAttackQuotient is None):
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

