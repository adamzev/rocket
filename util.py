def printTable(table_data, cols):
	maxWidth = 170
	maxCellWidth = maxWidth / cols
	for row in table_data:
		rowString = "{: >"+str(maxCellWidth)+"}"
		rowString = rowString * len(row)
		print(rowString.format(*row))

def edRow(big_G, V_vert_inc, time,totalWeight, totalA, V_horiz, V_as, A_v, A_h, V_vert, alt, thrust, ADC_guess = 0.0, ADC_actual = 0.0, ADC_adj = 0.0, A_total_eff = 0.0):
	row1 = "-"*140 + "\n"
	row2 = "{:>50.6} {:>10.6} {:>3}{:.8f}\n".format(A_total_eff, ADC_actual, 'G=', big_G)
	row3 = "+{:<15.2f} \x1b[6;30;42m{:.1f}\x1b[0m WT={:<12.2f}->{:<10.6f} {:.8} Vh= {:.6f} Vas {:.3f}          {:.6f}-{:.8f}\n".format(
		V_vert_inc, time, totalWeight, totalA, ADC_adj, V_horiz, V_as, A_v, A_h
	)
	row4 = "{:<18.6f} ALT={:.1f} T={:.4f}   {:.4}\n".format(V_vert, alt, thrust, ADC_guess)
	print(row1+row2+row3+row4)


def current(myArray):
	n = len(myArray) -1
	return myArray[n]

def prev(myArray):
	n = len(myArray) -1
	return myArray[n-1]

def get_value(myArray, when="current"):
	if when == "current":
		return current(myArray)
	else:
		return prev(myArray)

''' SET BREAKPOINTS BY '''
# import pdb; pdb.set_trace()
