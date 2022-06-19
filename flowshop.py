from json.encoder import INFINITY
import xml.etree.ElementTree as ET

class Instance:
    def __init__(
            self,njobs = 0,nops = 0, flowVector=[],start = [],processing = [],setup = [],due = [],defaultSetup = 0, defaultDue = INFINITY,root=None
    ):
        self.njobs = njobs
        self.nops = nops
        self.flowVector = flowVector
        self.start = start
        self.processing = processing
        self.setup = setup
        self.due = due
        self.defaultSetup = defaultSetup
        self.defaultDue = defaultDue
        self.root = root
        self.graphIndex = {}

    def extract_sequence(self):
        sequence = {m:{} for m in set(self.flowVector)}
        for job in range(self.njobs):
            for op in range(self.nops):
                sequence[self.flowVector[op]][(job,op)] = self.start[job][op]
        return sequence



def convert_asapst(asapst):
    result = []
    with open(asapst) as f:
        for line in f:
            # start_times = [int(x.split('.')[0].strip()) for x in line.split('\t')]
            line = line.strip("\n")
            start_times = [int(x.split('.')[0].strip()) for x in [line[i:i+15] for i in range(0, len(line), 15)]]
            result.append(start_times)
    return result




def extract_instance(input,sched):
    root = ET.parse(input).getroot()
    flowVector = [int(child.attrib['value']) for child in root.find('flowVector')] # which operation is mapped onto which machine
    pTimesNode = root.find('processingTimes')
    sTimesNode = root.find('setupTimes')
    dTimesNode = root.find('relativeDueDates')

    # build up explicit representation of processingtimes, setuptimes and duedates
    defaultProcTime = int(pTimesNode.attrib['default'])
    defaultSetupTime = int(sTimesNode.attrib['default'])
    defaultDueDate = int(dTimesNode.attrib['default']) if dTimesNode.attrib['default'] != 'inf' else float('inf')

    nOps = int(root.find('jobs').find('operations').attrib['count'])
    nJobs = int(root.find('jobs').attrib['count'])

    processingTimes = [[defaultProcTime for i in range(nOps)] for x in range(nJobs)]
    setupTimes = {}
    dueDates = {}

    # potentially use maps instead of arrays for this, as the matrix is sparse
    for child in pTimesNode:
        j = int(child.attrib['j'])
        op = int(child.attrib['op'])
        t = int(float(child.attrib['value']))
        processingTimes[j][op] = t
    
    for child in sTimesNode:
        j1 = int(child.attrib['j1'])
        op1 = int(child.attrib['op1'])
        j2 = int(child.attrib['j2'])
        op2 = int(child.attrib['op2'])
        t = int(float(child.attrib['value']))
        if (j1,op1) not in setupTimes:
            setupTimes[(j1, op1)] = {}
        setupTimes[(j1,op1)][(j2,op2)] = t
    
    for child in dTimesNode:
        j1 = int(child.attrib['j1'])
        op1 = int(child.attrib['op1'])
        j2 = int(child.attrib['j2'])
        op2 = int(child.attrib['op2'])
        t = int(float(child.attrib['value']))
        if (j1,op1) not in dueDates:
            dueDates[(j1, op1)] = {}
        dueDates[(j1,op1)][(j2,op2)] = t

    schedule = convert_asapst(sched)
    instance = Instance(nJobs,
                        nOps,
                        flowVector,
                        schedule,
                        processingTimes,
                        setupTimes,
                        dueDates,
                        defaultSetupTime,
                        defaultDueDate,
                        root)
    return instance
    # return processingTimes, setupTimes, dueDates, defaultSetupTime, defaultDueDate 