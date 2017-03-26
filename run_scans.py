#!/bin/env python

def launchTests(args):
  return launchTestsArgs(*args)

def launchTestsArgs(tool, slot, link, chamber,vt1=None,vt2=0,perchannel=False,trkdata=False,ztrim=4.0):
  import datetime,os,sys
  import subprocess
  from subprocess import CalledProcessError
  from chamberInfo import chamber_config

  if os.getenv('DATA_PATH') == None or os.getenv('DATA_PATH') == '':
    print 'You must source the environment properly!'
    exit(0)
  if os.getenv('BUILD_HOME') == None or os.getenv('BUILD_HOME') == '':
    print 'You must source the environment properly!'
    exit(0)

  startTime = datetime.datetime.now().strftime("%Y.%m.%d.%H.%M")
  dataPath = os.getenv('DATA_PATH')

  scanType = "vt1"
  dataType = "VT1Threshold"

  #Build Commands
  setupCmds = []
  preCmd = None
  cmd = ["%s"%(tool),"-s%d"%(slot),"-g%d"%(link)]
  if tool == "ultraScurve.py":
    scanType = "scurve"
    dataType = "SCurve"
    dirPath = "%s/%s/%s/"%(dataPath,chamber_config[link],scanType)
    setupCmds.append( ["mkdir","-p",dirPath+startTime] )
    setupCmds.append( ["unlink",dirPath+"current"] )
    setupCmds.append( ["ln","-s",dirPath+startTime,dirPath+"current"] )
    dirPath = dirPath+startTime
    cmd.append( "--filename=%s/SCurveData.root"%dirPath )
    #preCmd = ["confChamber.py","-s%d"%(slot),"-g%d"%(link)]
    #if vt1 in range(256):
    #  preCmd.append("--vt1=%d"%(vt1))
    #  pass
    pass
  elif tool == "trimChamber.py":
    scanType = "trim"
    dataType = None
    dirPath = "%s/%s/%s/"%(dataPath,chamber_config[link],scanType)
    setupCmds.append( ["mkdir","-p",dirPath+startTime] )
    setupCmds.append( ["unlink",dirPath+"current"] )
    setupCmds.append( ["ln","-s",dirPath+startTime,dirPath+"current"] )
    dirPath = dirPath+startTime
    cmd.append("--ztrim=%f"%(ztrim))
    if vt1 in range(256):
      cmd.append("--vt1=%d"%(vt1))
      pass
    cmd.append( "--dirPath=%s"%dirPath )
    pass
  elif tool == "ultraThreshold.py":
    scanType = "threshold"
    if vt2 in range(256):
      cmd.append("--vt2=%d"%(vt2))
      pass
    if perchannel:
      cmd.append("--perchannel")
      scanType = scanType + "/channel"
      pass
    else:
      scanType = scanType + "/vfat"
      pass
    if trkdata:
      cmd.append("--trkdata")
      scanType = scanType + "/trk"
      pass
    else:
      scanType = scanType + "/trig"
      pass
    dirPath = "%s/%s/%s/"%(dataPath,chamber_config[link],scanType)
    setupCmds.append( ["mkdir","-p",dirPath+startTime] )
    setupCmds.append( ["unlink",dirPath+"current"] )
    setupCmds.append( ["ln","-s",dirPath+startTime,dirPath+"current"] )
    dirPath = dirPath+startTime
    cmd.append( "--filename=%s/ThresholdScanData.root"%dirPath )
    pass

  log = file("%s/scanLog.log"%(dirPath),"w")

  #Execute Commands
  try:
    for setupCmd in setupCmds:
      try:
        print "executing", setupCmd
        sys.stdout.flush()
        returncode = subprocess.call(setupCmd,stdout=log)
        print "%s had return code %d"%(setupCmd,returncode)
      except CalledProcessError as e:
        print "Caught exception",e
        pass
      pass
    if preCmd:
      try:
        print "executing", preCmd
        sys.stdout.flush()
        returncode = subprocess.call(preCmd,stdout=log)
        print "%s had return code %d"%(preCmd,returncode)
      except CalledProcessError as e:
        print "Caught exception",e
        pass
      pass
    print "executing", cmd
    sys.stdout.flush()
    returncode = subprocess.call(cmd,stdout=log)
    print "%s had return code %d"%(cmd,returncode)
  except CalledProcessError as e:
    print "Caught exception",e
    pass
  return

if __name__ == '__main__':

  import sys,os,signal
  import subprocess
  import itertools
  from multiprocessing import Pool, freeze_support
  from chamberInfo import chamber_config

  from qcoptions import parser

  parser.add_option("--parallel", action="store_true", dest="parallel",
                    help="Run tests in parllel (default is false)", metavar="parallel")
  parser.add_option("--tool", type="string", dest="tool",default="ultraThreshold.py",
                    help="Tool to run (scan or analyze", metavar="tool")
  parser.add_option("--vt1", type="int", dest="vt1", default=100,
                    help="Specify VT1 to use", metavar="vt1")
  parser.add_option("--vt2", type="int", dest="vt2", default=0,
                    help="Specify VT2 to use", metavar="vt2")
  parser.add_option("--perchannel", action="store_true", dest="perchannel",
                    help="Run a per-channel VT1 scan", metavar="perchannel")
  parser.add_option("--trkdata", action="store_true", dest="trkdata",
                    help="Run a per-VFAT VT1 scan using tracking data (default is to use trigger data)", metavar="trkdata")
  parser.add_option("--ztrim", type="float", dest="ztrim", default=4.0,
                  help="Specify the p value of the trim", metavar="ztrim")

  (options, args) = parser.parse_args()

  if options.tool not in ["trimChamber.py","ultraThreshold.py","ultraScurve.py"]:
    print "Invalid tool specified"
    exit(1)

  if options.debug:
    print itertools.izip([options.tool for x in range(len(chamber_config))],
                         [options.slot for x in range(len(chamber_config))],
                         chamber_config.keys(),
                         chamber_config.values(),
                         [options.vt1 for x in range(len(chamber_config))],
                         [options.vt2 for x in range(len(chamber_config))],
                         [options.perchannel for x in range(len(chamber_config))],
                         [options.trkdata for x in range(len(chamber_config))],
                         [options.ztrim for x in range(len(chamber_config))]
                         )

  if options.parallel:
    print "Running jobs in parallel mode (using Pool(8))"
    freeze_support()
    # from: https://stackoverflow.com/questions/11312525/catch-ctrlc-sigint-and-exit-multiprocesses-gracefully-in-python
    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    pool = Pool(8)
    signal.signal(signal.SIGINT, original_sigint_handler)
    try:
      res = pool.map_async(launchTests,
                           itertools.izip([options.tool for x in range(len(chamber_config))],
                                          [options.slot for x in range(len(chamber_config))],
                                          chamber_config.keys(),
                                          chamber_config.values(),
                                          [options.vt1 for x in range(len(chamber_config))],
                                          [options.vt2 for x in range(len(chamber_config))],
                                          [options.perchannel for x in range(len(chamber_config))],
                                          [options.trkdata for x in range(len(chamber_config))],
                                          [options.ztrim for x in range(len(chamber_config))]
                                          )
                           )
      # timeout must be properly set, otherwise tasks will crash
      print res.get(999999999)
      print("Normal termination")
      pool.close()
      pool.join()
    except KeyboardInterrupt:
      print("Caught KeyboardInterrupt, terminating workers")
      pool.terminate()
    except Exception as e:
      print("Caught Exception %s, terminating workers"%(str(e)))
      pool.terminate()
    except: # catch *all* exceptions
      e = sys.exc_info()[0]
      print("Caught non-Python Exception %s"%(e))
      pool.terminate()
  else:
    print "Running jobs in serial mode"
    for link in chamber_config.keys():
      chamber = chamber_config[link]
      launchTests([options.tool,options.slot,link,chamber,options.vt2,options.perchannel,options.trkdata,options.ztrim])
      pass
    pass
