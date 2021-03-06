#############################################################################
# Generated by PAGE version 4.25.1
#  in conjunction with Tcl version 8.6
#  Mar 02, 2021 11:57:12 AM CET  platform: Windows NT
set vTcl(timestamp) ""


if {!$vTcl(borrow) && !$vTcl(template)} {

set vTcl(actual_gui_bg) #d9d9d9
set vTcl(actual_gui_fg) #000000
set vTcl(actual_gui_analog) #ececec
set vTcl(actual_gui_menu_analog) #ececec
set vTcl(actual_gui_menu_bg) #d9d9d9
set vTcl(actual_gui_menu_fg) #000000
set vTcl(complement_color) #d9d9d9
set vTcl(analog_color_p) #d9d9d9
set vTcl(analog_color_m) #d9d9d9
set vTcl(active_fg) #111111
set vTcl(actual_gui_menu_active_bg)  #ececec
set vTcl(active_menu_fg) #000000
}




proc vTclWindow.top37 {base} {
    global vTcl
    if {$base == ""} {
        set base .top37
    }
    if {[winfo exists $base]} {
        wm deiconify $base; return
    }
    set top $base
    ###################
    # CREATING WIDGETS
    ###################
    vTcl::widgets::core::toplevel::createCmd $top -class Toplevel \
        -background $vTcl(actual_gui_bg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black 
    wm focusmodel $top passive
    wm geometry $top 657x655+302+131
    update
    # set in toplevel.wgt.
    global vTcl
    global img_list
    set vTcl(save,dflt,origin) 0
    wm maxsize $top 1684 1032
    wm minsize $top 148 10
    wm overrideredirect $top 0
    wm resizable $top 0 0
    wm deiconify $top
    wm title $top "New Toplevel 1"
    vTcl:DefineAlias "$top" "GUI" vTcl:Toplevel:WidgetProc "" 1
    ttk::style configure TNotebook -background $vTcl(actual_gui_bg)
    ttk::style configure TNotebook.Tab -background $vTcl(actual_gui_bg)
    ttk::style configure TNotebook.Tab -foreground $vTcl(actual_gui_fg)
    ttk::style configure TNotebook.Tab -font "$vTcl(actual_gui_font_dft_desc)"
    ttk::style map TNotebook.Tab -background [list disabled $vTcl(actual_gui_bg) selected $vTcl(pr,guicomplement_color)]
    ttk::notebook $top.tNo38 \
        -width 619 -height 561 -takefocus {} 
    vTcl:DefineAlias "$top.tNo38" "TNotebook1" vTcl:WidgetProc "GUI" 1
    frame $top.tNo38.pg0 \
        -background $vTcl(actual_gui_bg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black 
    vTcl:DefineAlias "$top.tNo38.pg0" "TNotebook1_t0" vTcl:WidgetProc "GUI" 1
    $top.tNo38 add $top.tNo38.pg0 \
        -padding 0 -sticky nsew -state normal -text ??? -image {} \
        -compound none -underline -1 
    set site_4_0  $top.tNo38.pg0
    label $top.lab39 \
        -activebackground #f9f9f9 -activeforeground black \
        -background $vTcl(actual_gui_bg) -disabledforeground #a3a3a3 \
        -font TkDefaultFont -foreground $vTcl(actual_gui_fg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -textvariable Messaggio 
    vTcl:DefineAlias "$top.lab39" "Label1" vTcl:WidgetProc "GUI" 1
    ###################
    # SETTING GEOMETRY
    ###################
    place $top.tNo38 \
        -in $top -x 15 -y 65 -width 619 -relwidth 0 -height 561 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.lab39 \
        -in $top -x 25 -y 15 -width 600 -relwidth 0 -height 30 -relheight 0 \
        -anchor nw -bordermode ignore 

    vTcl:FireEvent $base <<Ready>>
}

set btop ""
if {$vTcl(borrow)} {
    set btop .bor[expr int([expr rand() * 100])]
    while {[lsearch $btop $vTcl(tops)] != -1} {
        set btop .bor[expr int([expr rand() * 100])]
    }
}
set vTcl(btop) $btop
Window show .
Window show .top37 $btop
if {$vTcl(borrow)} {
    $btop configure -background plum
}

