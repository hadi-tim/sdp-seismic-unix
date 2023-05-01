# Table of contents
* [How to install Seismic Unix on Windows](#how-to-install-seismic-unix-on-windows)
* [Ubuntu on Windows](#ubuntu-on-windows)
* [Installing Xming Server](#installing-xming-server)
* [Installing Seismic Unix](#installing-seismic-unix)
* [Seismic processing of 2D line](#seismic-processing-of-2D-line)
  * [Reading and viewing seismic data](#reading-and-viewing-seismic-data)
  * [Setting geometry](#setting-geometry)
  * [Python code for geometry headers update](#python-code-for-geometry-headers-update)
  * [Viewing shot gathers QC](#viewing-shot-gathers-(QC))
  * [CMP locations QC and binning](#cmp-locations-qc-and-binning)
  * [Sort data to CMP](#sort-data-to-cmp)

 


## How to install Seismic Unix on Windows
This tutorial will illustrate step by step on how to process seismic data using Seismic Unix. Before starting our Seismic Data Processing journey, some installations need to be made. We will go through all**
## Ubuntu on Windows

The perfect thing to do is to install a Linux partition in your machine (laptop or desktop). In my case I installed Ubuntu [WSL](https://ubuntu.com/wsl) which is a complete Ubuntu terminal environment in on Windows, which is called Windows Subsystem for Linux (WSL)

## Installing Xming Server
In order to run SU modules, an X window server will be needed. in our case I used Xming, which need to be launched after installing Seismic Unix. Here is the [Xming server website for download](http://www.straightrunning.com/XmingNotes/)

## Installing Seismic Unix
Before installing SU, we need to set some environment variables. Add following commands to your profile like .zshrc or .bashrc.

```Shell
export CWPROOT=$HOME
```
```Shell
export PATH=$PATH:$HOME/bin
```
Get SU files from [Seismic-unix.org](https://wiki.seismic-unix.org/doku.php). Here we download the latest version of SU cwp_su_all_44R23.tgz.

Copy the file to $HOME and unzip it by:

```Shell
mv /mnt/c/Users/lzhao/Downloads/cwp_su_all_44R26.tgz ~
```
```Shell
tar xvf cwp_su_all_44R26.tgz
```
After extracting the folder of SU a correction need to be made to the config file:
```Shell
cd src
```
```Shell 
mv Makefile.config Makefile.config.old
```
```Shell
cp ./configs/Makefile.config_Linux_x86_64 ./Makefile.config
```
Installing some packages necessary for Seismic Unix.

```Shell
sudo apt install build-essential
```

```Shell
sudo apt install gfortran
sudo apt install libx11-dev
sudo apt install libxt-dev
sudo apt install freeglut3-dev
sudo apt install libxmu-dev libxi-dev
sudo apt install libc6
sudo apt install libuil4
sudo apt install x11proto-print-dev
sudo apt install libmotif-dev
```
Finally we will install Seismic Unix:
```Shell
make install make xtinstall
make finstall
```
Seismic Unix Should be installed successfully without errors, please ignore the warning messages.
In order to check run the command below:
```Shell
suplane | suximage title="test"
```
**CONGRATULATIONS ON YOUR FIRST SEISMIC UNIX DISPLAY!!!** :satisfied:
## Seismic processing of 2D line
For this tutorial we are going to explain step by step on how to process 2D seismic data using Seismic Unix. The data for this document can be accessed for free [here!](https://dataunderground.org/dataset/poland-vibroseis/resource/96dfd0be-61c8-4edb-9d04-c7d2aeb16d27).
Below is the proposed processing flow chart that we will follow.

```mermaid
graph TD;
    A(SEGY Input)-->B(Coonvert to SU format);
    B-->C(Geometry update);
    C-->D(Shot gathers QC);
    C-->E(Elevation Statics);
    D-->E;
    E-->F(Trace Editing);
    F-->G(Ground roll removal, F-K filter);
    G-->H(Deconvolution);
    H-->I(Band Pass Filter);
    I-->J(CMP Sort);
    J-->K(Velocity Analysis);
    K-->L(NMO Correction);
    J-->L;
    L-->M(Mute)
    M-->N(Stack)
    N-->O(Migration)

```
### Reading and viewing seismic data
As mentionned before at the beginning of thes notes, our data is in SEGY format and need to be converted to SU format. This is done via:
```Shell
segyread tape=Line_001.sgy endian=0 |suwind key="trid" min="1" > data.su
```
In addition to conversion the code above removes the Auxilliary channels,using key `trid` and `min=1`\

trid: Trace identification\
-1 = Aux data\
1 = Seismic data\

We may use **`surange`** to see if the header settings are correct as shown below:
```Shell
surange < data.su
```
<img src="https://user-images.githubusercontent.com/124686555/234352239-7417ed65-2d3a-45f2-b294-3b718d3454d6.png" width="700" height="500">

#### Windowing and viewing data
As an example, the code below run a display in wiggles for one shot gather `shot gather FFID#231`. It is always a good idea to look at some small part of the data to check if data exists. 

```Shell
suwind key=fldr min=231 max=231 < seismic.su | suximage perc=99 &
```

<img src="https://user-images.githubusercontent.com/124686555/234355282-6d04788f-ac47-47b7-8a4b-7281738021de.png" width="700">

### Setting geometry
Geometry definition is one of the most time consuming in processing especially for 2D data. This process is for converting the observed field parameters recorded in observer logs into trace headers.
I wrote the Python code below `sps_check.ipynb` to check the SPS information regarding, total number of shots, total number of receivers...etc.\
The program output the following information:

```sh
============= SPS FILE=============
First Shot Point:       701
Last Shot Point:      1201
Total number of shots:  251 VPs
============= RPS FILE=============
First Receiver Point:       561
Last Shot Point:      1342
Total number of receivers:  782 Receiver
============= XPS FILE=============
First Field File ID:   231
Last Field File ID:   481
Total number of traces:  70782
```
I worked on another Python script which uses the SPS information as input and outputs a text file containig the geometry information (the X, Y coordinates for source and receiver, the offset, and the static information.



### Python code for geometry headers update
Below is the code to run in a Python environment.

```Python
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
```
Before proceeding to the geometry, we need to convert the geometry information from the text file into a binary format, then load the binary information into data to apply the geometry.

```Shell
a2b < geometry.txt n1=9 > myheaders.bin
```
n1=9 indicates number of columns in the geometry text file. After appying the geometry we can notice that headers are correctly updated including the offset and X 1 Y coordinates.

![surange_after_geom](https://user-images.githubusercontent.com/124686555/234369239-5789a888-ba74-4da9-87cf-50555bc8823d.png)

### Viewing shot gathers QC

```Shell
suwind key=ep min=100 max=100 < data_geom2.su | suximage key=offset cmap=hsv4 perc=90\
                title="shot100 after geometry" label1="Time(s)" label2="Offsset(m)"  &
```
<img src="https://user-images.githubusercontent.com/124686555/234378605-c5f9ecbd-3bc4-4eb0-a441-a1bebe0e785f.png" width="700">

Another QC we can look at the source and receiver locations, first thing to do is to create the binary files that contain the coordinates information (X and Y) for both source and receiver.

```Gawk
gawk '{print $1,$2}' < geometry.txt |sort|uniq|a2b > srcloc.bin
gawk '{print $5,$6}' < geometry.txt |sort|uniq|a2b > rcvloc.bin
```
Now we have the binary information of the source and receiver locations in those two files, we concatenate them and we plot data  using psgraph. The process is described in a bash script `04_geom_qc1.job`

```sh
#!/bin/bash

cat srcloc.bin rcvloc.bin |
	psgraph n=251,782 linecolor=red,blue wbox=16 hbox=3.5 \
	d1num=1000 d2num=1000 \
	labelsize=9 grid1=solid grid2=solid gridcolor=gray marksize=1,1 \
	gridwidth=0 linewidth=0,0 title="Source & Receiver Locations" \
	label1=Easting label2=Northing > SrcRcv_loc_map.ps
```
The generated post graph file .ps can be viewed using line command:

```sh
gv SrcRcv_loc_map.ps
```


<img src="https://user-images.githubusercontent.com/124686555/234381419-9f76a478-76a2-4482-9c09-303f75a0cece.png" >

### CMP locations QC and binning

It is well known that a straight 2D line, a CMP location is defined as the midpoint between the source and the receiver locations. On a crooked line (our case), CMPs may do not lie on the line of source and receiver.\
So, let’s plot the CMPs locations using same script as before. But this time calculating the midpoint locations of CMPs using the provided information in the geometry text file.

```gawk
#!/bin/bash

gawk '{print ($1+$5)/2,($2+$6)/2}'<myheaders_new.txt |a2b > cmploc.bin
	cat cmploc.bin srcloc.bin rcvloc.bin |
	psgraph n=70782,251,782 linecolor=green,red,blue wbox=16 hbox=3.5 \
	d1num=1000 d2num=1000 \
	labelsize=9 grid1=solid grid2=solid gridcolor=gray marksize=0.5,1,1 \
	gridwidth=0 linewidth=0,0 title="Source Receiver and CMPs locations"\
	label1=Easting label2=Northing > SrcRcvCmp_loc_map.ps
```
Let's plot via the command:
```sh
gv SrcRcvCmp_loc_map.ps
```
<img src="https://user-images.githubusercontent.com/124686555/234388018-59f9db96-d83f-4769-adca-c2d6a4014f6e.png">

It is well noticed in the graph that we are dealing with a crooked line, CMPs are not falling between source and receiver, so a a possible solution to this is to do binning. let's tak teh receiver line, then we can project all actual CMP locations to the nearest point on the receiver line.\
In order to choose the best parameter for the maximum offset distance between a cmp location and the cmp line which is supposed to be the `receiver line`. After several tests as described int the shell script, the Maximum offline distance that we choose is 200m.

```sh
#!/bin/bash

# Set up a command to concatenate some plot files for comparing off-line distances accepted
convert="cat "

# Set the CMP interval
dcdp=12.5

# Loop through several offline distances and compare results.
for distmax in 12.5 25 50 100 200 500
do
	echo Running crooked line binning for maximimum offline distance $distmax into $dcdp m bins

	sucdpbin <data_geom2.su xline=684590.2,697315.1,703807.7 yline=3837867.6,3839748.8,3841277.2 verbose=2 dcdp=$dcdp distmax=$distmax 2>cdp.log |suwind key=cdp min=1 > geomdata_cmps_$distmax.su

	echo Creating chart data
	suchart < geomdata_cmps_$distmax.su key1=cdp key2=offset >plotdata outpar=par

	echo Running Postscript graphing routine
	psgraph <plotdata par=par linewidth=0 mark=0 marksize=1 labelsize=6 titlesize=12 linecolor=blue wbox=13 hbox=10 >plot$distmax.ps title="Maximum offline distance $distmax m  - $dcdp m Bins"

	convert="$convert plot$distmax.ps"
done

# Now concatenate the Postscript files in the same order they were created, so the resulting multipage file can be opened and the effects of changing the offline distance parameter
$convert > crookedLine_bining.ps
```
Let's plot the stacking chart, which is a plot of the header CDP field versus the offset field. We can notice the white stripes indicating missing shots.

```sh
gv crookedLine_bining.ps
```

<img src="https://user-images.githubusercontent.com/124686555/234390895-f5e2a4c2-3ec3-402f-88e7-be505b4c15d8.png" height="500" width="800">


### Sort data to CMP
To sort the data from shot to cmp domain we use `susort`:
```sh
susort cdp offset < data.su
```
### Gain testing
```sh
#!/bin/sh

suwind < data_geom2.su key=ep min=32 max=32 > data_geom_ep32.su

suxwigb < data_geom_ep32.su title="Ungained Data" &
sugain < data_geom_ep32.su scale=5.0 | suxwigb title="Scaled data" &
sugain < data_geom_ep32.su agc=1 wagc=.01 | suxwigb title="AGC=1 WAGC=.01 sec &
sugain < data_geom_ep32.su agc=1 wagc=.2 | suxwigb title="AGC=1 WAGC=.2 sec &
sugain < data_geom_ep32.su pbal=1 | suxwigb title="traces balanced by rms" &
sugain < data_geom_ep32.su qbal=1 | suxwigb title="traces balanced by quantile" &
sugain < data_geom_ep32.su mbal=1 | suxwigb title="traces balanced by mean" &
sugain < data_geom_ep32.su tpow=2 | suxwigb title="t squared factor applied" &
sugain < data_geom_ep32.su tpow=.5 | suxwigb title="square root t factor applied" &
```
<img src="https://user-images.githubusercontent.com/124686555/235467240-7bed593a-7e4a-4dcc-a476-0f54fa93c1c9.png" height="600">

### NMO Correction and brute stack
As a preliminary step, we can run the brute stack flow in this stage as a QC and in order to compare with further stacks as we move forward in our processing.
the stack has an AGC applied.
```sh
sunmo < data.cdp vnmo=1700,2750,3000 tnmo=0.1,1.0,2.0 \
	| sugain \
	    agc=1 \
	    wagc=.2 \
	| sustack > stack.su
suximage < stack.su cmp=hsv5 title="Brute stack V0" perc=90 &
```
<img src="https://user-images.githubusercontent.com/124686555/235463368-c08ac25d-0cd4-4f99-a4e9-4220a88b4b7a.png" height="400" width="800">

### Filtering in the (F,k) domain
To attenuate the coherent noise such as ground roll, we used (f, k) filetering as a first step as it targets the linear noise taking into consideration the slope or the dip of the event.\
For this purpose I did numerous tests on one shot gather. Once you are satisfied with the result, you can run the (f;k) filter on the whole data as showed in the script below.\
```sh
#!/bin/bash

indata=geomdata_bin200_d2.su

sudipfilt < $indata dt=0.002 dx=0.025\
	slopes=-0.5,-0.3,0.3,0.5 amps=0,1,1,0 bias=0 > geomdata_bin200_fk.su
```
With: 
 - amps=1,1,1,1 (do nothing)
 - amps=1,0,0,1 (The reject zone)
 - amps=0,1,1,0 (The pass zone)

The images below shows the shots before, after and the rejected data, respectively with their corresponding (f,k) spectrums.

<img src="https://user-images.githubusercontent.com/124686555/235468292-92120233-3f91-4e93-a56f-3cba79737945.png" height="400" width="800">
<img src="https://user-images.githubusercontent.com/124686555/235469828-6052f000-58e3-46a6-88d2-eb789e0b2415.png" height="400" width="800">
<img src="https://user-images.githubusercontent.com/124686555/235469868-c81c34d3-13f5-4aa0-8e85-9227603dcdfb.png" height="400" width="800">

### Band Pass Filter testing
before proceeding to BPF, it is important to know the frequency content of our data byt transfromfing our data from (x,t) domain to (x,f) domain, where Frequency is on the vertical scale, and trace number is on the horizontal.
```sh
suspecfx < stk_fk.su | suximage key=cdp title="F-X SPECTRUM" label2="CMP" label1="Frequency (Hz)" cmap="hsv2" bclip=45
```
<img src="https://user-images.githubusercontent.com/124686555/235475595-7689b376-387b-4f2d-a24b-ba6c1acbaff8.png" height="400" width="800">

Zooming in our data, we can notice that the energy is mainly concentrated is the frequency band between 15 and 45 Hz.\

For the BPF testing, I did several Band Pass Filter panels, below is the result of one test using a combination of frequencies from, 10,15,55,60. The spectrum is obtained after transforming the prestack data from time domain to frequency domain using Gabor Transform.

The [Gabor transform](https://en.wikipedia.org/wiki/Gabor_transform), as explained in wikipidia is named after Dennis Gabor, is a special case of the short-time Fourier transform. It is used to determine the sinusoidal frequency and phase content of local sections of a signal as it changes over time. 

<img src="https://user-images.githubusercontent.com/124686555/235477896-6dede5ba-ce87-4359-a6b5-bdda739f435d.png" height="800" width="800">

Compare the two frequency spectrums. Notice how the sub-20Hz sections is subdued by the filter applied.
Now we apply the BPF to all the data via the command:
```sh
sufilter < geomshots_bin200_fk.su f=10,15,55,60 > geomshots_bin200_fk_bpf.su
```
In order to QC the output before and after the BPF, let’s check the stacks before and after. Notice, there is a better continuity in the shallow part of the stack.

<img src="https://user-images.githubusercontent.com/124686555/235498044-2d40b80d-c7ba-4224-896f-47054254cb55.png" height="450" width="800">

<img src="https://user-images.githubusercontent.com/124686555/235498056-bacdef8a-0f93-4050-ac6f-031c779a0c3b.png" height="450" width="800">

### Deconvolution
Deconvolution in an inverse process which consists of removing the effect of the waveform. Basically we  process of removing the
effect of a waveform, to produce a desired output. In practice the objectif is to achieve a better estimate of the gelogical layers in term of increasing the temporal resolution of the reflector.\
Before proceeding to deconvolution, first we need to perfoem the autocorrelation to have a better estimate of the deconvolution parameters and undestanding the the multiple energy behavior.

The code below is the code to perform the autocorrelation and deconvolution test. The main parameters that we should pay attention to are minlag and maxlag, while ntout is the number of autocorrelation samples that will be produced. You can test with different pnoise.

```sh
#!/bin/sh

minlag=0.02
maxlag=0.1
pnoise=0.001
ntout=120
indata=geomdata_bin200_fk_bpf.su

rm -f tmp*

# Data selection you will probably need to use sugain to remove any decay in amplitudes with time that may result from geometric spreading
suwind < $indata key=ep min=120 max=120 > tmp0
sugain < tmp0 agc=1 wagc=0.2 > tmp1

# One Shot display
suximage < tmp1 perc=90 title="Before deconvolution" \
                        label1="Time(s)" \
                        lebel2="Trace" &

# Autocorrelation before deconvolution
suacor < tmp1 suacor ntout=$ntout | suximage perc=90 title="Autocorrelation before deconvolution" \
                        label1="Time(s)" \
                        lebel2="Trace" &

# Deconvolution
supef < tmp1 > tmp2 minlag=$minlag maxlag=$maxlag pnoise=$pnoise 

# After Deconvolution

suximage < tmp2 perc=90 title="After deconvolution" \
                        label1="Time(s)" \
                        lebel2="Trace" &

# Autocorrelation after deconvolution
suacor < tmp2 suacor ntout=$ntout | suximage perc=90 title="Autocorrelation after deconvolution" \
                        label1="Time(s)" \
                        lebel2="Trace" &

# Apply deconvolution to al the data
supef < geomdata_bin200_fk_bpf.su > geomdata_bin200_fk_bpf_decon.su minlag=0.02 maxlag=0.1 pnoise=0.001 

rm -f tmp*
```
<img src="https://user-images.githubusercontent.com/124686555/235521740-79a87306-648f-4188-bca4-dfb0225f8252.png">
<img src="https://user-images.githubusercontent.com/124686555/235521754-e5bc59a2-bd8c-44f8-9891-9370f68cfeb9.png">

### Velocity Analysis
A script made by John W. Stockwell, a Copyright (c) Colorado School of Mines. This script provide an interactive velocity picking session. It will first ask the user to input number of picks. You are then asked to state the CMP number for the first pick, then it will diplay three plots:
* Semblance plot of the selected CMP number
* Plot of the selected CMP gather
* Constant Velocity Stack of the selected CMP number



</details>

<!--
  <<< Author notes: Footer >>>
  Add a link to get support, GitHub status page, code of conduct, license link.
-->

---

Get help: [Post in our discussion board](https://github.com/skills/.github/discussions) &bull; [Review the GitHub status page](https://www.githubstatus.com/)

&copy; 2022 GitHub &bull; [Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md) &bull; [CC-BY-4.0 License](https://creativecommons.org/licenses/by/4.0/legalcode)
