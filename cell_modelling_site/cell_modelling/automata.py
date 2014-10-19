import generate_automata
import boolfunction
import state

import sys



from debug import log
from state import State

#automataStructure
#automataStates
#automataAnalysis

class NK_Automata(object):
    def __init__(self,p_N=0,p_K=0,p_functionsList=[],p_linksList=[]):
        self.N=p_N
        self.K=p_K
        self.functionsList=p_functionsList
        self.linksList=p_linksList
        self.ordinalNumber=-1

        self.stateSpan={} #dict: {currentStateNumber: nextStateNumber,...}
        self.stateList=[]
        self.attractorDict={} # {attractorNumber:[size,basinSize],...}

        self.basinAmount=0
        self.stability=0

        self.expectedReturnTime=100500



    def __sizeof__(self):
        return sys.getsizeof(self.N) + sys.getsizeof(self.K) + sys.getsizeof(self.functionsList) + sys.getsizeof(self.linksList)+ sys.getsizeof(self.stateSpan)+ sys.getsizeof(self.basinAmount) + sys.getsizeof(self.stability)+ sys.getsizeof(self.attractorDict)

    def __str__(self):
        #return "N = " + str(self.N)+ " K = " + str(self.K) +"\n"+"functionsList: "+str(self.functionsList)+"\n"+"linksList: " + str(self.linksList)
        return "N = " + str(self.N)+ " K = " + str(self.K) +"functionsList: "+str(self.functionsList)+"linksList: " + str(self.linksList)

    def __repr__(self):
        return self.__str__()

    def generateRandomAutomata(self):
        self.functionsList=[]
        self.linksList=[]
        generate_automata.generateNKAutomata(self.N,self.K,self.functionsList,self.linksList)

    def stepAutomata(self,state):

        newStateString=""
        for boolFunNumber in range(self.N):

            boolFunInputs=""
            for stateElementNumber in range(self.K):
                boolFunInputs+=state.asString()[self.linksList[boolFunNumber][stateElementNumber]]


            newStateString+=self.functionsList[boolFunNumber].evaluate(boolFunInputs)

        return State(newStateString)


    def spanAutomata(self):

        if self.stateSpan:
            self.stateSpan={}

        print "Iterating automata states:"
        currentState=State(0,self.N)
        nextState=State(0,self.N)
        for stateNumber in range(2**self.N):


            #print "Current state:", stateNumber
            currentState.setState(stateNumber)

            nextState=self.stepAutomata(currentState)

            #self.stateSpan[currentState.asInt()]=nextState.asInt()
            self.stateSpan[currentState.asString()[::]]=nextState.asString()[::]

    def createStateList(self):
        for stateNumber in range(2**self.N):
            self.stateList.append(State(stateNumber,self.N))
#
    def processSample(self,seed):
        currentStateNumber=seed
        sampleList=[]
        while not (currentStateNumber in sampleList):

            if self.stateList[currentStateNumber].inAttractor:

                for sampleStateNumber in sampleList:
                    self.stateList[sampleStateNumber].inBasin=True
                    self.stateList[sampleStateNumber].basinNumber=self.stateList[currentStateNumber].basinNumber
                    self.stateList[sampleStateNumber].firstAttractorStateNumber=currentStateNumber
                self.stateList[currentStateNumber].weight+=len(sampleList)
                return

            if self.stateList[currentStateNumber].inBasin:
                firstAttractorStateNumber = self.stateList[currentStateNumber].firstAttractorStateNumber
                for sampleStateNumber in sampleList:
                    self.stateList[sampleStateNumber].inBasin=True
                    self.stateList[sampleStateNumber].basinNumber=self.stateList[currentStateNumber].basinNumber
                    self.stateList[sampleStateNumber].firstAttractorStateNumber=firstAttractorStateNumber
                self.stateList[firstAttractorStateNumber].weight+=len(sampleList)
                return

            sampleList.append(currentStateNumber)
            currentStateNumber=(self.stepAutomata(State(currentStateNumber,self.N))).asInt()


        attractorStartStateNumber=currentStateNumber

        attractorStartIndex=sampleList.index(attractorStartStateNumber)
        basinList=sampleList[:attractorStartIndex]
        attractorList=sampleList[attractorStartIndex:]

        for stateNumber in basinList:
            self.stateList[stateNumber].inBasin=True
            self.stateList[stateNumber].basinNumber=self.basinAmount+1
            self.stateList[stateNumber].firstAttractorStateNumber=attractorStartStateNumber

        for stateNumber in attractorList:
            self.stateList[stateNumber].inAttractor=True
            self.stateList[stateNumber].basinNumber=self.basinAmount+1

        self.stateList[attractorStartStateNumber].weight=len(basinList)

        self.basinAmount+=1
    ###

    #next state object

    def nextState(self,state):
        nextStateString=self.stateSpan[state.asString()]
        nextStateNumber=State(nextStateString).stateNumber
        nextStateObject=self.stateList[nextStateNumber]
        return nextStateObject
    ###

    def analyseAutomata(self):
        print "starting analysis:"
        self.createStateList()
        sampleNumber=0
        for stateNumber in range(2**self.N):
            if self.stateList[stateNumber].inBasin==False and self.stateList[stateNumber].inAttractor==False:
                #print "  takingSample:", sampleNumber
                self.processSample(stateNumber)
            sampleNumber+=1

    def initializeAttractorDict(self):
        for attractorNumber in range(1,self.basinAmount+1):
            self.attractorDict[attractorNumber]=[0,0] # {attractorNumber:[size,basinSize],...}

    def makeAttractorStatDictionary(self):
        print "-->"
        self.initializeAttractorDict()
        for state in self.stateList:
            if state.inAttractor==True:
                self.attractorDict[state.basinNumber][0]+=1
            if state.inBasin==True:
                self.attractorDict[state.basinNumber][1]+=1

    def countStability(self):
        basinSizeSquareSum=0
        for attractorNumber in self.attractorDict:
            basinSizeSquareSum+=(self.attractorDict[attractorNumber][0]+self.attractorDict[attractorNumber][1])**2
        self.stability=float(basinSizeSquareSum)/(2**(self.N))**2

    def distanceBetweenStates(self,fromState,toState):

        currentState=fromState
        distance=0
        while currentState!=toState:
            distance+=1
            currentState=self.nextState(currentState)

           # print "      CurrentState:", currentState
            if distance>100500:
                print "err"
                return -1
        #print "FromState:", fromState, "ToState:", toState, "distance:", distance

        return distance


    def countExpectedReturnTime(self):
        # average timesteps needed to reach some cycle in case of random state change i.e. average distance to the nearest cycle
        averageReturnTime=0
        basinStatesAmount=0
        for currentState in self.stateList:

            if currentState.inBasin==True:
                basinStatesAmount+=1
                firstAttractorState=self.stateList[currentState.firstAttractorStateNumber]

                averageReturnTime+=self.distanceBetweenStates(currentState,firstAttractorState)
        if basinStatesAmount==0:
            self.expectedReturnTime=0
            return 0
        averageReturnTime=float(averageReturnTime)/basinStatesAmount
        self.expectedReturnTime=averageReturnTime
        return averageReturnTime


    #outdated method. Never used

    def makeAttractorsDictionary(self):
        attractorDict={}
        for state in self.stateList:
            if state.inAttractor==True:
                print state
                attractorDict[state.asInt()]=[(self.stepAutomata(state)).asInt(),state.weight]
        return attractorDict
