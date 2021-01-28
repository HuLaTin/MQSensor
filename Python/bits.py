import random
bitMinValue = 0
bitMaxValue = 1
def genRandomBits(K):
    bits = dict()
    for i in range(K):
        if random.random() > 0.5:
            bits[i] = 1
        else:
            bits[i] = 0
    return(bits)

def getNeighbors(bits):
    # Returns a dict where the key is the bit of bits that was flipped, the value is the cost of the resulting dict (from the flipped bit)
    neighborBitsCost = bits.copy()
    x = int()
    for i in neighborBitsCost:
        if neighborBitsCost[i] == 1:
            neighborBitsCost[i] = 0
        else:
            neighborBitsCost[i] = 1
        x = getValueOfBits(neighborBitsCost,bitMinValue, bitMaxValue)
        neighborBitsCost[i] = x
    bestScore = 0
    bestBits = dict()
    for j in neighborBitsCost:
        if neighborBitsCost[j] > bestScore:
            bestScore = neighborBitsCost[j]
            bestBits = bits.copy()
            if bestBits[j] == 1:
                bestBits[j] = 0
            else:
                bestBits[j] = 1
            print(bestBits)
            print(bestScore)
    getNeighbors(bestBits)

def getValueOfBits(bits,min,max):
    x = 0
    for i in bits:
        x += (2**i)*bits[i]
    # Gets the percentage of 0-1023, converts to a %, and returns the number equal to the percent between min and max
    return((((x/1023)*100) * (max - min) / 100) + min)


bits = genRandomBits(10)
print(bits)
print(getValueOfBits(bits,bitMinValue,bitMaxValue))
getNeighbors(bits)

