#
# Python script to report on active showers
#

import sys
import datetime
import os
import glob
import shutil

from utils.getActiveShowers import getActiveShowers
from analysis.showerAnalysis import showerAnalysis
from reports.findFireballs import findFireballs


def createShowerIndexPage(dtstr, shwr, shwrname, outdir, datadir):
    templdir = os.getenv('TEMPLATES', default='/home/ec2-user/prod/website/templates')
    idxfile = os.path.join(outdir, 'index.html')
    shutil.copyfile(os.path.join(templdir,'header.html'), idxfile)
    with open(idxfile, 'a') as outf:
        # header info
        outf.write(f'<h2>{shwrname}</h2>\n')
        outf.write('<a href="/reports/index.html">Back to report index</a><br>\n')
        #outf.write('</tr></table>')

        # add the shower information file, if present
        shwrinfofile = os.path.join(datadir, 'shwrinfo', f'{shwr}.txt')
        if os.path.isfile(shwrinfofile):
            outf.write('<pre>/\n')
            with open(shwrinfofile, 'r') as inf:
                for line in inf:
                    outf.write(f'{line}\n')
            outf.write('</pre>\n')

        # shower stats
        shwrinfofile = os.path.join(outdir, 'statistics.txt')
        if os.path.isfile(shwrinfofile):
            outf.write('<pre>\n')
            with open(shwrinfofile, 'r') as inf:
                for line in inf:
                    outf.write(f'{line}')
            if shwr == 'ALL':
                outf.write(f'Click <a href="/browse/annual/matches-{dtstr}.csv">here</a> to download the matched data.\n')
            else:
                outf.write(f'Click <a href="/browse/showers/{dtstr}-{shwr}-matches.csv">here</a> to download the matched data.\n')
            outf.write('</pre>\n')
        outf.write('<br>\n')
        # brightest event list
        fbinfofile = os.path.join(outdir, 'fblist.txt')
        if os.path.isfile(fbinfofile):
            with open(os.path.join(outdir, 'reportindex.js'), 'w') as jsout:
                jsout.write('$(function() {\n')
                jsout.write('var table = document.createElement("table");\n')
                jsout.write('table.className = \"table table-striped table-bordered table-hover table-condensed\";\n')
                jsout.write('var header = table.createTHead();\n')
                jsout.write('header.className = \"h4\";\n')
                jsout.write('var row = table.insertRow(-1);\n')
                jsout.write('var cell = row.insertCell(0);\n')
                jsout.write('cell.innerHTML = "Brightest Ten Events";\n')
                with open(fbinfofile, 'r') as fbf:
                    fblis = fbf.readlines()
                for li in fblis:
                    jsout.write('var row = table.insertRow(-1);\n')
                    jsout.write('var cell = row.insertCell(0);\n')
                    fldr, mag, shwr, bn = li.split(',')
                    jsout.write(f'cell.innerHTML = "<a href="{fldr}">{bn}</a>";\n')
                    jsout.write('var cell = row.insertCell(1);\n')
                    jsout.write(f'cell.innerHTML = "{mag}";n')
                    jsout.write('var cell = row.insertCell(2);\n')
                    jsout.write(f'cell.innerHTML = "{shwr}";\n')

                jsout.write('var outer_div = document.getElementById("summary");\n')
                jsout.write('outer_div.appendChild(table);\n')
                jsout.write('})\n')

            outf.write('<div class="row">\n')
            outf.write('<div class="col-lg-12">\n')
            outf.write('    <div id="summary" class="table-responsive"></div>\n')
            outf.write('    <div id="reportindex"></div>\n')
            outf.write('</div>\n')
            outf.write('</div>\n')
            outf.write('<script src="./reportindex.js"></script>\n')

        # additional information
        outf.write('<h3>Additional Information</h3>\n')
        outf.write('The graphs and histograms below show more information about the velocity, magnitude \n')
        outf.write('start and end altitude and other parameters. Click for larger view. \n')
        # add the charts and stuff
        jpglist = glob.glob(os.path.join(outdir, '*.jpg'))
        pnglist = glob.glob(os.path.join(outdir, '*.png'))
        outf.write('div class="top-img-container">\n')
        for j in jpglist:
            outf.write(f'<a href="./{j}"><img src="./{j}" width="20%"></a>\n')
        for j in pnglist:
            outf.write(f'<a href="./{j}"><img src="./{j}" width="20%"></a>\n')
        outf.write('</div>\n')

        outf.write("<script> $('.top-img-container').magnificPopup({ \n")
        outf.write("delegate: 'a', type: 'image', image:{verticalFit:false}, gallery:{enabled:true} }); \n")
        outf.write('</script>\n')

        # page footer
        with open(os.path.join(templdir, 'footer.html')) as ftr:
            lis = ftr.readlines()
            for li in lis:
                outf.write(f'{li}\n')

    return


def findRelevantPngs(dtstr, shwr, trajdir, outdir):
    pngs = f'{trajdir}/{dtstr}/plots/*{shwr}.png'
    plts = glob.glob(pngs)
    if len(plts) > 0:
        _, fnam = os.path.split(plts[0])
        shutil.copyfile(plts[0], os.path.join(outdir, fnam))
    return


def reportActiveShowers(ymd):
    shwrlist = getActiveShowers(ymd, retlist=True)
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    trajdir = os.getenv('MATCHDIR', default='/home/ec2-user/ukmon-shared/matches/RMSCorrelate/trajectories')
    print(shwrlist)
    dtstr = ymd.strftime('%Y')
    for shwr in shwrlist:
        print(shwr)
        shwrname = showerAnalysis(shwr, int(dtstr))
        findFireballs(int(dtstr), shwr, 999)
        outdir=os.path.join(datadir, 'reports', dtstr, shwr)
        findRelevantPngs(dtstr, shwr, trajdir, outdir)
        createShowerIndexPage(dtstr, shwr, shwrname, outdir, datadir)
    return 


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ymd = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')
    else:
        ymd = datetime.datetime.now()
    reportActiveShowers(ymd)
