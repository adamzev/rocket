def printTable(table_data):
	maxWidth = 170
	maxCellWidth = maxWidth / len(table_data[0])
	for row in table_data:
		rowString = "{: >"+str(maxCellWidth)+"}"
		rowString = rowString * len(row)
		print(rowString.format(*row))
