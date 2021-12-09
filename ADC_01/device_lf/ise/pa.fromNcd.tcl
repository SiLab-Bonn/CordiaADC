
# PlanAhead Launch Script for Post PAR Floorplanning, created by Project Navigator

create_project -name adc01 -dir "/faust/user/lhafiane/cordia/ADC_01/device/ise/planAhead_run_1" -part xc3s1000fg320-5
set srcset [get_property srcset [current_run -impl]]
set_property design_mode GateLvl $srcset
set_property edif_top_file "/faust/user/lhafiane/cordia/ADC_01/device/ise/adc01.ngc" [ get_property srcset [ current_run ] ]
add_files -norecurse { {/faust/user/lhafiane/cordia/ADC_01/device/ise} }
set_property target_constrs_file "/faust/user/lhafiane/cordia/ADC_01/device/src/adc01.ucf" [current_fileset -constrset]
add_files [list {/faust/user/lhafiane/cordia/ADC_01/device/src/adc01.ucf}] -fileset [get_property constrset [current_run]]
link_design
read_xdl -file "/faust/user/lhafiane/cordia/ADC_01/device/ise/adc01.ncd"
if {[catch {read_twx -name results_1 -file "/faust/user/lhafiane/cordia/ADC_01/device/ise/adc01.twx"} eInfo]} {
   puts "WARNING: there was a problem importing \"/faust/user/lhafiane/cordia/ADC_01/device/ise/adc01.twx\": $eInfo"
}
