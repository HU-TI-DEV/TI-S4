import math

def ik(x, y, x3, y3, l1, l2, l3, A1, A2):
    '''
    x: Het x-coördinaat van de base-joint.
    y: Het y-coördinaat van de base-joint.
    x3: Het x-coördinaat van de eindeffector.
    y3: Het y-coördinaat van de eindeffector.
    l1: De lengte van segment 1.
    l2: De lengte van segment 2.
    l3: De lengte van segment 3.
    A1: Voorafgaande hoek tussen base en segment 1. 
    A2: Voorafgaande hoek tussen segment 1 en segment 2.
    '''

    '''Als het y-coördinaat hoger ligt dan het y-coördinaat van de base-joint is de eindeffector niet bereikbaar.'''
    if y3 >= y: 
        return None
    

    '''Bereken de omtrek-coördinaten van een cirkel met een radius van L3 vanuit oorsprong (x3, y3) in stappen van 0.1'''
    cordinates = []
    i = 0.0  
    while i <= 360.0:
        cor = []
        cor.append(x3 + l3 * math.cos(math.radians(i)))
        cor.append(y3 + l3 * math.sin(math.radians(i)))
        cordinates.append(cor)
        i += 0.1

    '''Zolang hoek 1 kleiner is dan zijn maximale hoek (90°)'''
    angle1 = 0 + A1
    while angle1 < 90.0:

        '''Berken de nieuwe effector van de tweede joint met hoek angle1'''
        new_x = x + l1 * math.cos(math.radians( 180 + angle1 ))
        new_y = y + l1 * math.sin(math.radians( 180 + angle1 ))

        '''Kijk naar ieder coördinaat van de cirkel'''
        for c in cordinates:

            '''berken de euclidische afstand tussen de het coördinaat van de cirkel en joint 2'''
            distance = math.sqrt(abs(new_x - c[0])**2 + abs(new_y - c[1])**2  )    

            '''Controleer of de euclidische afstand tussen de punten gelijk is aan L3 met een error marge van 0.05'''   
            if (abs(distance - l2) <= 0.05) and (y > c[1]):

                '''Bereken de hoek tussen segment 1 en segement twee met de cosinusregel'''   
                across = math.sqrt( abs(x - c[0])**2 + abs(y - c[1])**2 )
                devide = (2*l1*l2)
                angle = ( (l1**2 + l2**2 - across**2)/devide )       
                angle = max(-1.0, min(1.0, angle))                                          
                angle2 = math.acos(angle)
                angle2 = math.degrees(angle2)

                '''Controleer of de hoek tussen segment 1 en 2 tussen niet kleiner is dan de al bestaande hoek (basisstand).'''   
                if angle2 > A2:               

                    '''Controleer of de hoek tussen segment 1 en 2 kleiner is dan de maximale hoek.'''                    
                    if angle2 <= 85:  

                        '''Berken de rotatie van joint 2'''   
                        xb = c[0] - new_x
                        yb = c[1] - new_y
                        rotation = math.atan2(yb,xb)
                        
                        '''verander de maximale en minimale hoek met de roatie van joint 2.'''    
                        minangle = 20.5 + math.degrees(rotation)
                        maxangle = - 99.3 + math.degrees(rotation)
                                            
                        '''Bereken de hoek van de eineffector in de roatie van joint 2, waarbij joint 2 dezelfde rotatie heeft als de base.'''   
                        angleEndeffectorr = math.atan2(y3 - c[1], x3 - c[0]) 

                        '''Controleer of de hoek tussen de min en max valt.'''   
                        if math.degrees(angleEndeffectorr) <= minangle and math.degrees(angleEndeffectorr) >= maxangle:   

                            '''Bereken de hoek tussen segment 2 en 3'''   
                            xIN3 = new_x - c[0]
                            yIN3 = new_y - c[1]                 
                            thetaNEW = math.atan2(yIN3, xIN3)
                            
                            if (math.degrees(thetaNEW) < 0):
                                degrees = 360 - math.degrees(thetaNEW) 
                                
                                angle3 = abs(-degrees + math.degrees(angleEndeffectorr))
                            angle3 = abs(-math.degrees(thetaNEW) + math.degrees(angleEndeffectorr)) 
                            
                            return angle1, angle2, angle3
        '''Verhoog doe hoek van joint2 met een stapgrootte van 0.1'''     
        angle1 += 0.1
    print("Not reachable!")
    return None