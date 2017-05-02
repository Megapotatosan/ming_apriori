#usage : only be tested on pyhton2.7  "python ming_apriori.py -s support -c confidence -i datafile"
import sys
import optparse
import time


def dataFromFile(file_name):
    """Function which reads from the file and yields a generator"""
    try:
        with open(file_name) as f:
            content = f.readlines()
            f.close()
    except IOError as e:
        print ('I/O error({0}): {1}')
        exit()
    except:
        print ('Unexpected error: ')
        exit()
    transactions = []
    for line in content:
        transactions.append(frozenset(line.strip().split()))
    return transactions


def createC1(dataset):
    ##Create the first candidate
    c1 = []
    process = 0

    for transaction in dataset:
        for item in transaction:
            if not [item] in c1:
                c1.append([item])
    #if item is first time, appear before,add it
    c1.sort()
    return map(frozenset, c1)
def scan(dataset, candidates, minSup):
    sscnt = {}
    for tid in dataset:
        for can in candidates:
            if can.issubset(tid):
                sscnt.setdefault(can, 0)
                sscnt[can] += 1

    number_of_item = len(dataset)
    print (number_of_item)
    retlist = []
    support_dat = {}
    for key in sscnt:
        support = sscnt[key] / float(number_of_item) #of tx containing all items in AUB/total # of tx
        if sscnt[key] >= round(minSup*number_of_item):   #if minsup*len(dataset) is decimal number,it should be round to do calculation
            retlist.insert(0, key)
        support_dat[key] = support
    return retlist, support_dat

def aprioriGen(Lk, k):
    "Generate the joint transactions from candidate sets"
    retList = []
    lenLk = len(Lk)
    for i in range(lenLk):
        for j in range(i + 1, lenLk):
            L1 = list(Lk[i])[:k - 2]
            L2 = list(Lk[j])[:k - 2]
            L1.sort()
            L2.sort()
            if L1 == L2:
                retList.append(Lk[i] | Lk[j])
    return retList

def apriori(dataset ,minSupport):

    C1 = createC1(dataset)
    D = map(set, dataset)
    L1, support_data = scan(D, C1 ,minSupport)
    L = [L1]
    k = 2
    while (len(L[k - 2]) > 0):
        Ck = aprioriGen(L[k - 2], k)
        Lk, supK = scan(D, Ck, minSupport)
        support_data.update(supK)
        L.append(Lk)
        k += 1

    return L, support_data


def calcConf( freqSet, H, supportData, brl, minConf):
    prunedH = []
    for conseq in H:
        print"doing calcConf"
        conf = supportData[freqSet] / supportData[freqSet - conseq]
        print conf
        if conf >= minConf:
            print freqSet - conseq, '-->', conseq, 'conf:', conf
            brl.append((freqSet - conseq, conseq, conf))
            prunedH.append(conseq)
    return prunedH


def rulesFromConseq( freqSet, H, supportData, brl, minConf):
    m = len(H[0])
    if len(freqSet) > (m + 1):
        print"doing rulesfromConseq"
        Hmp1 = aprioriGen(H, m + 1)
        Hmp = calcConf(freqSet, Hmp1, supportData, brl, minConf)
        if len(Hmp) > 1:
            rulesFromConseq(freqSet, Hmp, supportData, brl, minConf)


def generateRules( L, supportData, minConf):
    bigRuleList = []
    for i in range(1, len(L)):
        for freqSet in L[i]:
            print("doing")
            H1 = [frozenset([item]) for item in freqSet]
            if i > 1:
                rulesFromConseq(freqSet, H1, supportData, bigRuleList, minConf)
            else:
                calcConf(freqSet, H1, supportData, bigRuleList, minConf)
    return bigRuleList

if __name__ == "__main__":
    start = time.time()

    optparser = optparse.OptionParser()
    optparser.add_option('-i', '--input',
                         dest='input',
                         help='filename containing csv',
                         default=None)
    optparser.add_option('-s', '--minSupport',
                         dest='minS',
                         help='minimum support value',
                         default=0.05,
                         type='float')
    optparser.add_option('-c', '--minConfidence',
                         dest='minC',
                         help='minimum confidence value',
                         default=0.6,
                         type='float')

    (options, args) = optparser.parse_args()

    inFile = None
    if options.input is None:
            inFile = sys.stdin
    elif options.input is not None:
            inFile = dataFromFile(options.input)
    else:
            print ('No dataset filename specified, system with exit\n')
            sys.exit('System will exit')

    minSupport = options.minS
    minConfidence = options.minC
    print(minSupport)
    print(minConfidence)
    L, support_data = apriori(inFile, minSupport)
    print(L)
    print(support_data)

    rules = generateRules(L,support_data,minConfidence)
    print("rule")
    print(len(rules))
    print(rules)

    end = time.time()
    print(end-start)
    #items, rules = runApriori(inFile, minSupport, minConfidence)

    #printResults(items, rules)
