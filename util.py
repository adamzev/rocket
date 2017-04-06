def printTable(table_data, cols):
	maxWidth = 170
	maxCellWidth = maxWidth / cols
	for row in table_data:
		rowString = "{: >"+str(maxCellWidth)+"}"
		rowString = rowString * len(row)
		print(rowString.format(*row))

def edRow(big_G, V_vert_inc, time,totalWeight, totalA, V_horiz, V_as, A_v, A_h, V_vert, alt, thrust):
	print("                                                        G={:.8f}\n+{:.2f}           \x1b[6;30;42m{:.1f}\x1b[0m WT={:.2f}->{:.6f}                   Vh= {:.2f} Vas {:.3f}          {:.6f}-{:.8f}\n{:.6f}        ALT={:.1f} T={:.4f}".format(big_G, V_vert_inc, time,totalWeight, totalA, V_horiz, V_as, A_v, A_h, V_vert, alt, thrust))
