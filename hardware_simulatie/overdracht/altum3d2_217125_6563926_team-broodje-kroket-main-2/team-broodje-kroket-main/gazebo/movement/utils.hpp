
/**
 * @brief Print the name and current value of a variable to stdout.
 * @param val The variable to inspect. The macro stringifies the name automatically.
 */
#define DEBUG_PRINT(val) std::cout<<"variable: " << #val << "=" <<val <<std::endl

/**
 * @brief Clamp a double value to the closed interval [min, max].
 * @param val The value to clamp.
 * @param min The lower bound (inclusive).
 * @param max The upper bound (inclusive).
 * @return @p val clamped to [@p min, @p max].
 */
double clampd(double val,double min,double max){
	if (val < min){
		val = min;
	}
	else if (val > max){
		val = max;
	}
	return val;
}

