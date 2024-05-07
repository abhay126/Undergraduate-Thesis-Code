import MMC_PyLibrary as pyMMC
# For serial Connection On ComPort : COM6 #pyMMC.openComPortMMC("COM6")
# For Ethernet Connection for default Port and Server Address
cnt = pyMMC.connectEthMMC("192.168.0.20", "5000")
print(cnt)
# For Querying response from the MMC Controller
# Using the format of Axis and Command
# Please refer to the MMC Manual for the Command List
poll1 = pyMMC.pollValues("1", "ver")
print(poll1)

poll2 = pyMMC.pollValues("2", "ver")
print(poll2)
# Allows to write Command without waiting for response
pyMMC.writeCommandToMMC("2", "enc50.20")
# Close connection will close depending on serial or ethernet
pyMMC.closeConnectionMMC()
