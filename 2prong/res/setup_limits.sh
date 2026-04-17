region=sideband
sigtype=eta
wmasspoints=(1 2 3) # first last npoints
pmasspoints=(1000 2500 3) # first last npoints
debug="0" # -1 = very quiet, 0 = quiet, 1 = verbose, 2+ = debug

input="/home/chiarito/work/stats/condor/input"
signal="signal_10percent_eta"
#signal="signal_10percent_etaprime"
#signal="signal_original_box"

masses=(0)
#masses=(0 7 32 39 96 103)
#masses=($(seq 0 49))
#masses=($(seq 0 $(( ${wmasspoints[2]} * ${pmasspoints[2]} - 1 ))))

sed -i "s|input_top_level = '.*'|input_top_level = '$input'|" files.py
sed -i "s|signal_input = '.*'|signal_input = '$signal'|" files.py
sed -i "s/^wmasspoints = numpy\.linspace(.*)$/wmasspoints = numpy.linspace(${wmasspoints[0]}, ${wmasspoints[1]}, ${wmasspoints[2]})/" files.py
sed -i "s/^pmasspoints = numpy\.linspace(.*)$/pmasspoints = numpy.linspace(${pmasspoints[0]}, ${pmasspoints[1]}, ${pmasspoints[2]})/" files.py
./files.py
