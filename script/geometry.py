import os
os.chdir(r'C:\Seismic Processing\Seismic_data\2D_Land_vibro_data_2ms')
import math
import csv
fname1 = 'Line_001.SPS'
fname2 = 'Line_001.RPS'
fname3 = 'Line_001.XPS'

nrcv = int(input('Enter total number of Shots: '))
nsrc = int(input('Enter total number of Receivers: '))

# Read each SPS file separately, create lists
fhand = open(fname1)
sp=[]; sx=[]; sy=[]; selev=[];sstat=[]
for line in fhand:
    if not line.startswith('H26'):
        sp.append(line[17:25]); sx.append(line[46:55]); sy.append(line[55:65]); selev.append(line[65:71]); sstat.append(line[28:32])

# Strip all white spaces in sp, sx and sy
sp1 = [i.strip(' ') for i in sp]; sx1 = [i.strip(' ') for i in sx]; sy1 = [i.strip(' ') for i in sy]; selev1 = [i.strip(' ') for i in selev]
sstat1 = [i.strip(' ') for i in sstat]

#Convert rp1, rx1 and ry1 elements to integer
sp1_int=[];sx1_int=[];sy1_int=[];selev1_int=[];sstat1_int=[]
for i in sp1:
    x = int(i); sp1_int.append(x)
for i in sx1:
    x = float(i); sx1_int.append(x)
for i in sy1:
    x = float(i); sy1_int.append(x)
for i in selev1:
    x = float(i); selev1_int.append(x)
for i in sstat1:
    x = float(i); sstat1_int.append(x)

#============================ WORK ON RPS ==========================================================
fhand = open(fname2)
rp=[];rx=[];ry=[];relev=[];rstat=[]
for line in fhand:
    if not line.startswith('H26'):
        line = line.strip()
        rp.append(line[17:25]); rx.append(line[46:55]); ry.append(line[55:65]); relev.append(line[65:71]); rstat.append(line[28:32])

# Strip all white spaces in rp, rx and ry
rp1 = [i.strip(' ') for i in rp]; rx1 = [i.strip(' ') for i in rx]; ry1 = [i.strip(' ') for i in ry]; relev1 = [i.strip(' ') for i in relev]
rstat1 = [i.strip(' ') for i in rstat]

# Convert rp1, rx1 and ry1 elements to integer
rp1_int=[];rx1_int=[];ry1_int=[];relev1_int=[];rstat1_int=[]
for i in rp1:
    x = int(i); rp1_int.append(x)
for i in rx1:
    x = float(i); rx1_int.append(x)
for i in ry1:
    x = float(i); ry1_int.append(x)
for i in relev1:
    x = float(i); relev1_int.append(x)
for i in rstat1:
    x = float(i); rstat1_int.append(x)

dict_selev={sp1_int[i]:selev1_int[i] for i in range(0,251)}
dict_sstat={sp1_int[i]:sstat1_int[i] for i in range(0,251)}
dict_relev={rp1_int[i]:relev1_int[i] for i in range(0,782)}
dict_rstat={rp1_int[i]:rstat1_int[i] for i in range(0,782)}

dict_rps = {'rp': rp1_int, 'rx': rx1, 'ry': ry1}

#============================ WORK ON XPS ==========================================================
fhand=open(fname3)
xp=[];r1=[];r2=[]
for line in fhand:
    if not line.startswith('H26'):
        line = line.strip()
        xp.append(line[29:37]); r1.append(line[63:71]); r2.append(line[71:79])

# Strip all white spaces in xps files
xp1 = [i.strip(' ') for i in xp]; r11 = [i.strip(' ') for i in r1]; r22 = [i.strip(' ') for i in r2]

#Convert xp1, r11(from channel) and r22(to channel) elements to integer
xp1_int=[];r11_int=[];r22_int=[]
for i in xp1:
    x = int(i); xp1_int.append(x)
for i in r11:
    x = int(i); r11_int.append(x)
for i in r22:
    x = float(i); r22_int.append(x)
dict_xps = {'vp': xp1, 'ch_from': r11, 'ch_to': r22} 

dict_sps = {'sp': sp1_int, 'sx': sx1_int, 'sy': sy1_int}
dict_sx={sp1_int[i]:sx1_int[i] for i in range(0,251)}
dict_sy={sp1_int[i]:sy1_int[i] for i in range(0,251)}

dict_rx={rp1_int[i]:rx1_int[i] for i in range(0,782)}
dict_ry={rp1_int[i]:ry1_int[i] for i in range(0,782)}

dict_xps2={int(xp1[i]):[*range(int(r11[i]),int(r22[i])+1)] for i in range(0,251)}

#INDEX of VP 701 (dict_xps2[int(dict_xps['vp'][i])][0])
'''
=====================================================================
Calculate the offset matrix for each VP corresponding to all traces 
collaborated to that particular VP
=====================================================================
'''
offset=[];xcord_s=[];ycord_s=[];xcord_r=[];ycord_r=[];src_elev=[];src_stat=[];rcv_elev=[];rcv_stat=[]
for i in range(0,251):
    for j in range(0,282):
        if int(dict_xps['vp'][i]) in sp1_int and int(dict_xps['ch_from'][i]) in rp1_int and int(dict_xps['ch_to'][i]) in rp1_int:
            xcor_r = float(dict_rx[dict_xps2[int(dict_xps['vp'][i])][j]])
            ycor_r = float(dict_ry[dict_xps2[int(dict_xps['vp'][i])][j]])
            r_elev = float(dict_relev[dict_xps2[int(dict_xps['vp'][i])][j]])
            r_stat = float(dict_rstat[dict_xps2[int(dict_xps['vp'][i])][j]])

            xcor_s = float(dict_sx[float(dict_xps['vp'][i])])  
            ycor_s = float(dict_sy[float(dict_xps['vp'][i])])
            s_elev = float(dict_selev[float(dict_xps['vp'][i])])
            s_stat = float(dict_sstat[float(dict_xps['vp'][i])])

            ox = xcor_r - xcor_s; oy = ycor_r - ycor_s; offs = math.sqrt(ox*ox + oy*oy)
            
            if int(dict_xps['vp'][i]) > int(dict_xps2[int(dict_xps['vp'][i])][j]):
                offs = offs * (-1)

            offset.append(offs)
            xcord_s.append(xcor_s)
            ycord_s.append(ycor_s)
            xcord_r.append(xcor_r)
            ycord_r.append(ycor_r)
            src_elev.append(s_elev)
            src_stat.append(s_stat)
            rcv_elev.append(r_elev)
            rcv_stat.append(r_stat)

with open('geometry.txt', 'w', newline='\n') as f:
    writer = csv.writer(f, delimiter=' ')
    for data in zip(xcord_s, ycord_s, src_elev, src_stat, xcord_r, ycord_r, rcv_elev, rcv_stat, offset):
        writer.writerow(data)
    f.write('\n')









   