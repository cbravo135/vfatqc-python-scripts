from optparse import OptionParser
from array import array
from fitScanData import *
from ROOT import TFile,TTree,TH2D,TCanvas,TPad,gROOT,gStyle

parser = OptionParser()

parser.add_option("-f", "--filename", type="string", dest="filename", default="SCurveData.root",
                  help="Specify Input Filename", metavar="filename")
parser.add_option("-o", "--outfilename", type="string", dest="outfilename", default="SCurveFitData.root",
                  help="Specify Output Filename", metavar="outfilename")


(options, args) = parser.parse_args()
filename = options.filename
print filename
outfilename = options.outfilename
gROOT.SetBatch(True)
gStyle.SetOptStat(0)

inF = TFile(filename)

outF = TFile(outfilename, 'recreate')

myT = TTree('scurveFitTree','Tree Holding FitData')

vcal = array( 'i', [ 0 ] )
myT.Branch( 'vcal', vcal, 'vcal/I' )
vfatN = array( 'i', [ 0 ] )
myT.Branch( 'vfatN', vfatN, 'vfatN/I' )
vfatCH = array( 'i', [ 0 ] )
myT.Branch( 'vfatCH', vfatCH, 'vfatCH/I' )
trimRange = array( 'i', [ 0 ] )
myT.Branch( 'trimRange', trimRange, 'trimRange/I' )
vthr = array( 'i', [ 0 ] )
myT.Branch( 'vthr', vthr, 'vthr/I' )
trimDAC = array( 'i', [ 0 ] )
myT.Branch( 'trimDAC', trimDAC, 'trimDAC/I' )
threshold = array( 'f', [ 0 ] )
myT.Branch( 'threshold', threshold, 'threshold/F')
noise = array( 'f', [ 0 ] )
myT.Branch( 'noise', noise, 'noise/F')

scanFits = fitScanData(filename)


for event in inF.scurveTree:
    vcal[0] = event.vcal
    vfatN[0] = event.vfatN
    vfatCH[0] = event.vfatCH
    trimRange[0] = event.trimRange
    vthr[0] = event.vthr
    trimDAC[0] = event.trimDAC
    threshold[0] = scanFits[0][event.vfatN][event.vfatCH]
    noise[0] = scanFits[1][event.vfatN][event.vfatCH]
    myT.Fill()
    pass

outF.cd()
outF.Write()
outF.Close()
