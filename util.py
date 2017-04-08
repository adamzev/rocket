def printTable(table_data, cols):
	maxWidth = 170
	maxCellWidth = maxWidth / cols
	for row in table_data:
		rowString = "{: >"+str(maxCellWidth)+"}"
		rowString = rowString * len(row)
		print(rowString.format(*row))

def edRow(big_G, V_vert_inc, time,totalWeight, totalA, V_horiz, V_as, A_v, A_h, V_vert, alt, thrust):
	print ("-"*120)
	print("                                                          G={:.8f}\n+{:<15.2f} \x1b[6;30;42m{:.1f}\x1b[0m WT={:<12.2f}->{:<20.6f} Vh= {:.2f} Vas {:.3f}          {:.6f}-{:.8f}\n {:<18.6f} ALT={:.1f} T={:.4f}\n".format(big_G, V_vert_inc, time,totalWeight, totalA, V_horiz, V_as, A_v, A_h,V_vert, alt, thrust))


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
