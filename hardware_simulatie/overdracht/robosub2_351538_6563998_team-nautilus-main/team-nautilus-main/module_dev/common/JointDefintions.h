#ifndef IKTEST_JOINTDEFINTIONS_H
#define IKTEST_JOINTDEFINTIONS_H

#include "JointSpec.h"

const std::vector<JointSpec> inline JOINT_DEFINITIONS = {
    { "subToBase",          "/subToBaseTopic",         -M_PI/4, M_PI/4,  3.0,  0.015,  0.038, {0,0,-0.1206},      {0,0,1},  true,  false },
    { "baseToUpperarm",     "/baseToUpperarmTopic",    -1.831,  0.0,    2.95, 0.0146, 0.037, {0,0,-0.0206},      {0,1,0},  true,  false },
    { "upperarmToForearm",  "/upperarmToForearmTopic", -1.649,  0.0,    3.5, 0.015, 0.034, {-0.208,0,-0.0292}, {0,-1,0}, true,  true  },
    { "forearmToWrist",     "/forearmToWristTopic",    -0.349,  1.752,    3.0, 0.013, 0.030, {0.235,0,0},        {0,1,0},  true,  false },
    { "wristToHand",        "/wristToHandTopic",        0.0,    4.712,    2.55, 0.0127, 0.028, {0.1601,0,0},       {1,0,0},  true,  false },
    { "handToFirstfinger",  "/handToFirstfingerTopic",  0.0,    M_PI/4,   2.5,  0.0125, 0.027, {0.01,0,0},         {0,1,0},  false, false },
    { "handToSecondfinger", "/handToSecondfingerTopic", -M_PI/4,0.0,     2.5,  0.0125,  0.027, {0.01,0,0},         {0,-1,0}, false, false },
};

#endif //IKTEST_JOINTDEFINTIONS_H
