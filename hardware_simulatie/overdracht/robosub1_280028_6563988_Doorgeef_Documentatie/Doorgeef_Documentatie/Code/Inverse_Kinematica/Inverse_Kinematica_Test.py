import math

def IK_test(x,y, x1,y1, x2,y2, x3,y3, l1,l2,l3):
    angle1 = math.atan2((y1-y),(x1-x)) 
    angle1 = math.degrees(angle1) + 180

    across = math.sqrt( (x - x2)**2 + (y - y2)**2 )
    devide = (2*l1*l2)
    angle = ( (l1**2 + l2**2 - across**2)/devide )                                          
    angle2 = math.acos(angle)
    angle2 = math.degrees(angle2)   

    angelfirst = math.atan2( (y1 - y2), (x1 - x2) )
    angelsecond = math.atan2( (y3 - y2), (x3 - x2) )
    angle3 = math.degrees(abs(-angelfirst + angelsecond))

    return angle1, angle2, angle3


