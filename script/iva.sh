#!/bin/bash

#set -x

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++         W A R N I N G    --    W A R N I N G                   +++++++++
#+++++++++++                                                                +++++++++
#+++++++++++    Script will crash  - see comments in line 142               +++++++++
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if [ ! -f cdps_after_decon.su ]
then    echo "Sort to CMP first!"
        pause EXIT
        exit 
fi

echo "Velocity Analysis"

rm -f panel.* picks.* par.* tmp*

#------------------------------------------------
# Defining Variables etc...
#------------------------------------------------

indata=cdps_after_decon.su
outdata=vpick.data

nt=1501
dt=0.002

nv=50   # Number of Velocities
dv=40    # Interval
fv=1200  # First Velocity

>$outdata   # Write an empty file
>par.cmp    # Write an empty file

#------------------------------------------------
# Interactive Velocity Analysis...
#------------------------------------------------

echo "How many Picks? (typical 4)" >/dev/tty 
read nrpicks

i=1	
while [ $i -le $nrpicks ]
do
    echo "Specify CMP Pick Location (CMP gather number) $i" >/dev/tty 
    read picknow
    echo "Preparing Location $i of $nrpicks for Picking "
    echo "Location is CMP $picknow "

#------------------------------------------------
# CMP Gather Plot...
#------------------------------------------------

    suwind <$indata key=cdp min=$picknow \
            max=$picknow >panel.$picknow 
    suximage <panel.$picknow xbox=422 ybox=10 \
             wbox=400 hbox=600 \
             title="CMP gather $picknow" \
             perc=90 key=offset verbose=0 &

#------------------------------------------------
# Constant Velocity Stack (please wait)...
#------------------------------------------------

    >tmp1			# Create empty file
    j=1
    k=`expr $picknow + 10`
    l=`echo "$dv * $nv / 120" | bc -l`

	suwind < $indata key=cdp min=$picknow \
			max=$k > tmp0

    while [ $j -le 10 ]
    do
		vel=`echo "$fv + $dv * $j * $nv / 10" | bc -l`

		sunmo < tmp0 vnmo=$vel |
			sustack >> tmp1
		sunull ntr=2 nt=$nt dt=$dt >> tmp1
		j=`expr $j + 1`
    done

	suximage <tmp1 xbox=834 ybox=10 wbox=400 hbox=600 \
			title="Constant Velocity Stack CMP $picknow" \
			label1="Time [s]" label2="Velocity [m/s]" \
			f2=$fv d2=$l verbose=0 mpicks=picks.$picknow \
			perc=90 n2tic=5 cmap=hsv5  &		

#------------------------------------------------
# Semblance Plot...
#------------------------------------------------

	echo "  Place the cursor over the semblance plot or the"
	echo "  constant velocity stack and type 's' to pick velocities."
	echo "  For each suitable cursor position, press 's' to pick."
	echo "  Type 'q' in the semblance plot when all picks are made."
	echo "  A NMO corrected gather will be plotted after picking"

	suvelan < panel.$picknow nv=$nv dv=$dv fv=$fv |
		suximage xbox=10 ybox=10 wbox=400 hbox=600 \
			units="semblance" f2=$fv d2=$dv \
			label1="Time [s]" label2="Velocity [m/s]" \
			title="Semblance Plot CMP $picknow" cmap=hsv2 \
			legend=1 units=Semblance verbose=0  gridcolor=black bclip=0.3\
			grid1=solid grid2=solid mpicks=picks.$picknow

	# Sort, using -n option -> "compare according to string numerical value"
	# Generate PAR file

	sort < picks.$picknow -n | mkparfile string1="tnmo" string2="vnmo" > par.$i

	cat par.$i
	echo "Completed listing of mkparfile output ..."


#------------------------------------------------
# NMO Plot and Velocity Profile...
#------------------------------------------------

	>tmp2				# Create empty file
	echo "cdp=$picknow" >> tmp2
	cat par.$i >> tmp2
	sunmo <panel.$picknow par=tmp2 |
		suximage title="CMP gather after NMO" xbox=10 ybox=10 \
				wbox=400 hbox=600 verbose=0 key=offset perc=90 &

	# SED info: http://www.grymoire.com/Unix/Sed.html
	cat par.$i | sed -e 's/tnmo/xin/' -e 's/vnmo/yin/' > par.uni.$i

	cat par.$i
	echo "Completed listing of par file A ..."
	cat par.uni.$i
	echo "Completed listing of par file B ..."

	# ------------  UNIformly SAMple a function y(x) specified as x,y pairs
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	#+++++++++++   W A R N I N G    ++++++    W A R N I N G    ++++++++++++++++++++++++++
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	# The UNISAM program does not seem to accept file of x,y in "par.uni" format.
	# It has probably been changed since the script was written several years ago.
	# So input to the UNISAM program must be corrected!
	# It will not generate an output file - so the next command will crash the script!!
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	unisam nout=$nt fxout=0.0 dxout=$dt par=par.uni.$i method=mono > tmp.unisam

	echo "Completed unisam command ..."

	cat tmp.unisam |
		 xgraph n=$nt nplot=1 d1=$dt f1=0.0 \
			label1="Time [s]" label2="Velocity [m/s]" \
			title="---> Stacking Velocity Function CMP $picknow" \
			-geometry 400x600+422+10 style=seismic \
			grid1=solid grid2=solid linecolor=3 marksize=1 mark=0 \
			titleColor=red axesColor=blue &

	echo "Picks OK? (y/n) " >  /dev/tty
	read response

	rm tmp*

	case $response in
		n*)
			i=$i
			echo "Picks removed"
			;;
		*)
			i=`expr $i + 1`
			echo "$picknow  $i" >> par.cmp
			;;
    esac
done

echo "Completed picking ..."

#------------------------------------------------
# Create Velocity Output File...
#------------------------------------------------

mkparfile < par.cmp string1=cdp string2=# > par.0

i=0
while [ $i -le $nrpicks ]
do
	cat par.$i >>$outdata
	i=`expr $i + 1`
done

rm -f panel.* picks.* par.* tmp*

exit
