import classes.Team as Team, classes.CalendarizedTeam as CalendarizedTeam
import libs.football_randomizer_api as frapi
import libs.run_transfermarkt_api as rtapi
import random
import tkinter as tk
from tkinter import ttk, filedialog, font
import io
from PIL import ImageTk as itk, Image
import threading

# dims for img canvas
CANVAS_DIMS = 100

# app version
# 0 . (functionalities implemented, general) . (code polish level) . (GUI level) . (quality of match simulation, randomness, etc)
VER = '0.6.5z.5y.4c'

#TODO change output when season is starting with odd amount of teams! no real feedback


class RootWindow:

    def set_mouse_y_scrolling_match_info(self, canvas: tk.Canvas):

        ############### Scroll Using Mouse Wheel ###############
        canvas1 = self.widgets_new["canvas_match_info_left"]
        canvas2 = self.widgets_new["canvas_match_info_right"]
        canvas1.configure(scrollregion=canvas1.bbox(tk.ALL))
        canvas2.configure(scrollregion=canvas2.bbox(tk.ALL))

        def scroll(event):
            canvas1.yview_scroll(int(-1 * (event.delta / 120)), "units")
            canvas2.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def final_scroll(event, func):
            canvas1.bind_all("<MouseWheel>", func)
            canvas2.bind_all("<MouseWheel>", func)

        def stop_scroll(event):
            canvas1.unbind_all("<MouseWheel>")
            canvas2.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", lambda event: final_scroll(event, lambda event: scroll(event)))
        canvas.bind("<Leave>", lambda event: stop_scroll(event))
        ################### code for scrolling match canvases #####################

        return
    
    def __init__(self, master):

        self.intro_text = "START SIMULATING USING THE MENU ABOVE"
        # mode: 0 for init, 1 for single match, 2 for season
        self.mode = 0

        # old badges: 0 for current, 1 for oldest, 2 for random
        self.old_badges = 0

        # "pots" for randomized teams (a list of which files to use), default just the strongest one
        self.selected_pot = 0
        self.select_nat_teams = False

        # small advantage for teams playing home (1) or not (0)
        self.home_adv = 1

        # match colours for frames, canvas and labels during matches
        self.match_colours = [None]*2

        # colours for light/dark theme (WIP)
        self.colour_themes = {
            "dark_bg": "#222222",
            "dark_fg": "#ffffff"
        }
        

        self.master = master
        
        main_menu = tk.Menu(self.master)
        season_menu = tk.Menu(main_menu, tearoff=0)
        options_menu = tk.Menu(main_menu, tearoff=0)
        friendly_menu = tk.Menu(main_menu, tearoff=0)

        friendly_menu.add_command(label = "Select two teams", command=self.search_clubs)
        friendly_menu.add_command(label = "Random Match", command=self.random_friendly)

        season_menu.add_command(label = "Custom Season", command=self.season_handler)
        season_menu.add_separator()
        season_menu.add_command(label = "Real Season", command=self.real_season_handler)
        season_menu.add_separator()
        season_menu.add_command(label = "Random Season", command=self.random_season_handler)
        season_menu.add_separator()
        season_menu.add_command(label = "Save Current Season", command=self.save_current_season)
        season_menu.add_command(label = "Load Season from File", command=self.load_season_file)

        options_menu.add_command(label = "Preferences", command=self.prefs_page)
        options_menu.add_command(label='Clear All', command=self.clear_all_teams)
        options_menu.add_separator()
        options_menu.add_command(label = "About", command=self.about_page)

        main_menu.add_cascade(label = "Friendly Match", menu=friendly_menu)
        main_menu.add_cascade(label = "Season", menu=season_menu)
        main_menu.add_cascade(label = "Options", menu=options_menu)

        self.master.configure(menu=main_menu)

        #main_menu.add_command(label = "Season Tournament", command=self.season_handler)
        #main_menu.add_command(label = "Season Tournament", command=self.season_handler)
        #main_menu.add_command(label = "Clear All", command=self.clear_all_teams)
        #main_menu.add_command(label = "About", command=self.about_page)

        # first instantiation of 2 teams min 
        self.teams = [Team.Team]
        self.teams.append(None)
        self.teams.append(None)

        # first instantiation of calendarized teams for rankings
        self.rankteams = [CalendarizedTeam.CalendarizedTeam] * 2

        self.calendar = []
        self.cur_day = 0
        self.cur_match = 0
        self.next_match = (0, 1)

        self.widgets_new: dict[str, tk.Widget] = {}

        frames_dims = {
            "left" : (750,700),
            "right" : (350,700),
            "top_left" : (700,150),
            "bottom_left" : (700,550),
            "top_right" : (400,400),
            "bottom_right" : (400,300),
        }

        font_groups = ["main", "secondary", "match_live_comment"]
        font_families = {
            font_groups[0] : ["Segoe UI", "Calibri", "System"],
            font_groups[1] : ["Arial", "System"],
            font_groups[2] : ["MS Sans Serif", "Small Fonts", "System"]
        }
        self.fonts : dict[str, str] = {}

        def assign_fonts(which_in_dict: str, font_list: list):
            font_iter = iter(font_list)
            self.fonts[which_in_dict] = None
            while self.fonts[which_in_dict] not in font.families():
                try:
                    self.fonts[which_in_dict] = next(font_iter)
                except:
                    self.fonts[which_in_dict] = "System"
                    break

        for font_group in font_groups:
            assign_fonts(font_group, font_families[font_group])

        print(font.families())

        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=1)

        self.frame.columnconfigure(index=0, weight=2)
        self.frame.columnconfigure(index=1, weight=1)
        self.frame.rowconfigure(index=0, weight=1)

        self.widgets_new["frame_left"] = tk.Frame(self.frame, highlightthickness=0)
        self.widgets_new["frame_left"].grid(row=0, column=0, sticky=tk.NSEW)

        self.widgets_new["frame_right"] = tk.Frame(self.frame, highlightthickness=0)
        self.widgets_new["frame_right"].grid(row=0, column=1, sticky=tk.NSEW)

        self.widgets_new["frame_left"].rowconfigure(index=0, minsize=frames_dims["top_left"][1], weight=0)
        self.widgets_new["frame_left"].rowconfigure(index=1, minsize=frames_dims["bottom_left"][1], weight=1)
        self.widgets_new["frame_left"].columnconfigure(index=0, minsize=frames_dims["left"][0], weight=1)
        self.widgets_new["frame_right"].rowconfigure(index=0, minsize=frames_dims["top_right"][1], weight=1)
        self.widgets_new["frame_right"].rowconfigure(index=1, minsize=frames_dims["bottom_right"][1], weight=0)
        self.widgets_new["frame_right"].columnconfigure(index=0, minsize=frames_dims["right"][0], weight=1)

        self.widgets_new["frame_top_info"] = tk.Frame(self.widgets_new["frame_left"], highlightthickness=0)
        self.widgets_new["frame_top_info"].grid(row=0, column=0, sticky=tk.NSEW)

        self.widgets_new["frame_match_info"] = tk.Frame(self.widgets_new["frame_left"], highlightthickness=0)
        self.widgets_new["frame_match_info"].grid(row=1, column=0, sticky=tk.NSEW)

        self.widgets_new["frame_table"] = tk.Frame(self.widgets_new["frame_right"], highlightthickness=2, highlightbackground='Black')
        self.widgets_new["frame_table"].grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)

        self.widgets_new["frame_pastmatches"] = tk.Frame(self.widgets_new["frame_right"], highlightthickness=2, highlightbackground='Black')
        self.widgets_new["frame_pastmatches"].grid(row=1, column=0, sticky=tk.NSEW, padx=10, pady=10)

        # top left frame 
        sizes = [frames_dims["left"][0]*0.33, 0, 0]
        sizes[2] = sizes[0]
        sizes[1] = frames_dims["left"][0]-sizes[0]-sizes[2]
        self.widgets_new["frame_top_info"].columnconfigure(index=0, minsize=sizes[0], weight=1)
        self.widgets_new["frame_top_info"].columnconfigure(index=1, minsize=sizes[1], weight=1)
        self.widgets_new["frame_top_info"].columnconfigure(index=2, minsize=sizes[2], weight=1)

        self.widgets_new["frame_top_info_left"] = tk.Frame(self.widgets_new["frame_top_info"], highlightthickness=0)
        self.widgets_new["frame_top_info_left"].grid(row=0, column=0, sticky=tk.NSEW)

        self.widgets_new["frame_top_info_center"] = tk.Frame(self.widgets_new["frame_top_info"], highlightthickness=0)
        self.widgets_new["frame_top_info_center"].grid(row=0, column=1, sticky=tk.NSEW)

        self.widgets_new["frame_top_info_right"] = tk.Frame(self.widgets_new["frame_top_info"], highlightthickness=0)
        self.widgets_new["frame_top_info_right"].grid(row=0, column=2, sticky=tk.NSEW)

        self.widgets_new["label_team1name"] = tk.Label(self.widgets_new["frame_top_info_left"], anchor=tk.CENTER, font=(self.fonts["main"], 10, 'bold')) 
        self.widgets_new["label_team1name"].pack()
        self.widgets_new["label_team1name"].pack_propagate(False)
        
        self.widgets_new["label_team2name"] = tk.Label(self.widgets_new["frame_top_info_right"], anchor=tk.CENTER, font=(self.fonts["main"], 10, 'bold')) 
        self.widgets_new["label_team2name"].pack()
        self.widgets_new["label_team2name"].pack_propagate(False)

        self.widgets_new["label_team1country"] = tk.Label(self.widgets_new["frame_top_info_left"], anchor=tk.CENTER, font=(self.fonts["main"], 8)) 
        self.widgets_new["label_team1country"].pack()
        
        self.widgets_new["label_team2country"] = tk.Label(self.widgets_new["frame_top_info_right"], anchor=tk.CENTER, font=(self.fonts["main"], 8)) 
        self.widgets_new["label_team2country"].pack()

        self.widgets_new["canvas_team1img"] = tk.Canvas(self.widgets_new["frame_top_info_left"], width=CANVAS_DIMS, height=CANVAS_DIMS, highlightthickness=0)
        self.widgets_new["canvas_team1img"].pack()

        self.widgets_new["canvas_team2img"] = tk.Canvas(self.widgets_new["frame_top_info_right"], width=CANVAS_DIMS, height=CANVAS_DIMS, highlightthickness=0)
        self.widgets_new["canvas_team2img"].pack()

        for i in range(3):
            self.widgets_new["frame_top_info_center"].columnconfigure(index=i, weight=1)
            self.widgets_new["frame_top_info_center"].rowconfigure(index=i, weight=1)

        self.widgets_new["label_matchstadium"] = tk.Label(self.widgets_new["frame_top_info_center"], anchor=tk.CENTER, font=(self.fonts["main"], 8), wraplength=sizes[1])
        self.widgets_new["label_matchstadium"].grid(row=0, columnspan=3, sticky=tk.NSEW)

        self.widgets_new["label_info_match"] = tk.Label(self.widgets_new["frame_top_info_center"], width=1, anchor=tk.CENTER, font=(self.fonts["main"], 15, "bold"), text=self.intro_text, wraplength=sizes[1])
        self.widgets_new["label_info_match"].grid(row=2, columnspan=3, sticky=tk.NSEW)

        self.widgets_new["label_team1goals"] = tk.Label(self.widgets_new["frame_top_info_center"], width=2, anchor=tk.CENTER, font=(self.fonts["main"], 28, "bold"))
        self.widgets_new["label_team1goals"].grid(row=1, column=0, sticky=tk.NSEW)
        self.widgets_new["label_goal_separator"] = tk.Label(self.widgets_new["frame_top_info_center"], anchor=tk.CENTER, font=(self.fonts["main"], 28, "bold"), text="-")
        self.widgets_new["label_goal_separator"].grid(row=1, column=1, sticky=tk.NSEW)
        self.widgets_new["label_team2goals"] = tk.Label(self.widgets_new["frame_top_info_center"], width=2, anchor=tk.CENTER, font=(self.fonts["main"], 28, "bold"))
        self.widgets_new["label_team2goals"].grid(row=1, column=2, sticky=tk.NSEW)

        
        # ----------------------

        tags = {
            "left_box": "frame1",
            "right_box": "frame2"
        }
        def onCanvasConfigure(e, tag: str):
            if tag==tags["left_box"]:
                self.widgets_new["canvas_match_info_left"].itemconfig(tag, width=self.widgets_new["canvas_match_info_left"].winfo_width()-10)
                #self.widgets_new["frame_match_info_left"].configure(width=self.widgets_new["canvas_match_info_left"].winfo_width())
            else:
                self.widgets_new["canvas_match_info_right"].itemconfig(tag, width=self.widgets_new["canvas_match_info_right"].winfo_width()-10)
                #self.widgets_new["frame_match_info_right"].configure(width=self.widgets_new["canvas_match_info_right"].winfo_width())

            # configs on frames mess up the bbox calculations!!
            bbox_dims = self.widgets_new["canvas_match_info_left"].bbox(tk.ALL)
            print(f"resize bbox= {bbox_dims}")
            self.widgets_new["canvas_match_info_left"].configure(scrollregion=bbox_dims)
            self.widgets_new["canvas_match_info_right"].configure(scrollregion=bbox_dims)


        # bottom left frame
        self.widgets_new["frame_match_info"].rowconfigure(index=0, minsize=frames_dims["bottom_left"][1], weight=1)
        proportions = [3,1,3]
        minsizes = [frames_dims["bottom_left"][0]*proportions[i]/(sum(proportions)) for i in range(3)]
        for i in [0, 2]:
            self.widgets_new["frame_match_info"].columnconfigure(index=i, minsize=minsizes[i], weight=10)
        self.widgets_new["frame_match_info"].columnconfigure(index=1, minsize=minsizes[1], weight=1)

        self.widgets_new["canvas_match_info_left"] = tk.Canvas(self.widgets_new["frame_match_info"], width=minsizes[0]-10-10, highlightthickness=5, highlightbackground="black", borderwidth=0)
        self.widgets_new["canvas_match_info_left"].grid(row=0, column=0, sticky=tk.NSEW, padx=(10,10), pady=(10,10))
        self.widgets_new["frame_match_info_left"] = tk.Frame(self.widgets_new["canvas_match_info_left"])
        self.widgets_new["canvas_match_info_left"].create_window(0,0,anchor=tk.S,window=self.widgets_new["frame_match_info_left"], tags=tags["left_box"])
        self.widgets_new["canvas_match_info_left"].bind("<Configure>", lambda e : onCanvasConfigure(e, tags["left_box"]))
        
        self.widgets_new["frame_match_info_center"] = tk.Frame(self.widgets_new["frame_match_info"], highlightthickness=0)
        self.widgets_new["frame_match_info_center"].grid(row=0, column=1, sticky=tk.NSEW)

        self.widgets_new["canvas_match_info_right"] = tk.Canvas(self.widgets_new["frame_match_info"], width=minsizes[0]-10-10, highlightthickness=5, highlightbackground="black", borderwidth=0)
        self.widgets_new["canvas_match_info_right"].grid(row=0, column=2, sticky=tk.NSEW, padx=(10,10), pady=(10,10))
        self.widgets_new["frame_match_info_right"] = tk.Frame(self.widgets_new["canvas_match_info_right"])
        self.widgets_new["canvas_match_info_right"].create_window(0,0,anchor=tk.S,window=self.widgets_new["frame_match_info_right"], tags=tags["right_box"])
        self.widgets_new["canvas_match_info_right"].bind("<Configure>", lambda e : onCanvasConfigure(e, tags["right_box"]))

        '''self.widgets_new["frame_match_info_right"] = tk.Frame(self.widgets_new["frame_match_info"], highlightthickness=0, bg='#345678')
        self.widgets_new["frame_match_info_right"].grid(row=0, column=2, sticky=tk.NSEW)'''

        '''def v_scroll(self, *args):
            self.widgets_new["canvas_match_info_left"].yview(*args)
            self.widgets_new["canvas_match_info_right"].yview(*args)'''

        self.set_mouse_y_scrolling_match_info(self.widgets_new["canvas_match_info_left"])
        self.set_mouse_y_scrolling_match_info(self.widgets_new["canvas_match_info_right"])

        self.widgets_new["frame_match_info_center"].columnconfigure(index=0, weight=1)
        weights = [1,1,0,0,0,1]
        for i in range(len(weights)):
            self.widgets_new["frame_match_info_center"].rowconfigure(index=i,  weight=weights[i])

        self.widgets_new["label_minute"] = tk.Label(self.widgets_new["frame_match_info_center"], anchor=tk.CENTER, font=(self.fonts["secondary"], 15)) 
        self.widgets_new["label_minute"].grid(row=0)

        self.widgets_new["button_start"] = tk.Button(self.widgets_new["frame_match_info_center"], text = "START\nMATCH", width=7, height=3, anchor=tk.CENTER, command=self.start_match, fg='darkgreen', font=(self.fonts["secondary"], 13, 'bold'), borderwidth=4)
        self.widgets_new["button_start"].grid(row=1)

        self.widgets_new["label_fast"] = tk.Label(self.widgets_new["frame_match_info_center"], text="FAST", anchor=tk.S, font=(self.fonts["secondary"], 7))
        self.widgets_new["label_fast"].grid(row=2)

        self.widgets_new["scale_speed"] = ttk.Scale(self.widgets_new["frame_match_info_center"], from_=10, to=1000, orient='vertical', length=200, value=500)
        self.widgets_new["scale_speed"].grid(row=3)

        self.widgets_new["label_slow"] = tk.Label(self.widgets_new["frame_match_info_center"], text="SLOW", anchor=tk.S, font=(self.fonts["secondary"], 7))
        self.widgets_new["label_slow"].grid(row=4)

        self.widgets_new["button_next"] = tk.Button(self.widgets_new["frame_match_info_center"], text = "NEXT\nMATCH", width=7, height=3, anchor=tk.CENTER, command=self.start_next_match, fg='darkgreen', font=(self.fonts["secondary"], 13, 'bold'), borderwidth=4, state='disabled')
        self.widgets_new["button_next"].grid(row=5)
        # ---------------------

        # top right frame
        self.widgets_new["label_all_ranks"] = tk.Label(self.widgets_new["frame_table"], text="#", anchor=tk.N, justify=tk.CENTER, font=(self.fonts["main"], 8))
        self.widgets_new["label_all_ranks"].pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.widgets_new["label_all_teams"] = tk.Label(self.widgets_new["frame_table"], text="TEAM", anchor=tk.N, justify=tk.CENTER, font=(self.fonts["main"], 8))
        self.widgets_new["label_all_teams"].pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.widgets_new["label_all_played"] = tk.Label(self.widgets_new["frame_table"], text="PLAYED", anchor=tk.N, justify=tk.CENTER, font=(self.fonts["main"], 8))
        self.widgets_new["label_all_played"].pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.widgets_new["label_all_goals"] = tk.Label(self.widgets_new["frame_table"], text="GOALS", anchor=tk.N, justify=tk.CENTER, font=(self.fonts["main"], 8))
        self.widgets_new["label_all_goals"].pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.widgets_new["label_all_points"] = tk.Label(self.widgets_new["frame_table"], text="PTS", anchor=tk.N, justify=tk.CENTER, font=(self.fonts["main"], 8))
        self.widgets_new["label_all_points"].pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # ----------------
        
        # bottom right frame

        for i in range(10):
            self.widgets_new[f"label_pastmatch{i}"] = tk.Label(self.widgets_new["frame_pastmatches"], bg="#f0f0f0" if i%2==0 else "#d2d2d2", font=(self.fonts["main"], 10, "bold" if i==0 else "normal"), text="")
            self.widgets_new[f"label_pastmatch{i}"].pack(fill=tk.BOTH, expand=1)


        # disabling button for match start and next
        self.widgets_new["button_start"].configure(state="disabled")
        self.widgets_new["button_next"].configure(state="disabled")

    def change_theme(self):
        self.widget_colour_change = list(self.widgets_new.keys())
        for x in ["frame_pastmatches"] + [f"label_pastmatch{i}" for i in range(10)]:
            self.widget_colour_change.remove(x)

        def change_theme_aux(widget_name: str):
            widget = self.widgets_new[widget_name]
            try:
                widget.configure(bg = self.colour_themes["dark_bg"])
                widget.configure(fg = self.colour_themes["dark_fg"])
                '''for w in widget.winfo_children():
                    change_theme(w)'''
            except:
                print("ecco", widget_name)
            try:
                widget.configure(highlightbackground = self.colour_themes["dark_fg"])
            except:
                print("ecco2", widget_name)
        for wn in self.widget_colour_change:
            change_theme_aux(wn)
    
    def save_current_season(self):
        # format: num teams / actual rankteam data (all rankteams) / current (or next, depends on next match) day / next match to be played
        dir = filedialog.asksaveasfilename()
        with open(dir, 'w') as f:
            f.write(str(len(self.rankteams)) + "\n")
            for t in self.rankteams:
                f.write(t.format_data_for_savefile() + "\n")
            f.write(str(self.cur_day) + "\n")
            f.write(str(self.cur_match))
        return
    
    def load_season_file(self):
        dir = filedialog.askopenfilename()
        self.clear_all_teams()
        self.rankteams.clear()
        self.teams.clear()
        self.widgets_new["label_info_match"].configure(text='Season loading, if not working try again...')
        self.mode = 2
        with open(dir, 'r') as f:
            num_teams = int(f.readline())
            for i in range(num_teams):
                data = f.readline().split()
                p = 3*int(data[3]) + int(data[4])
                self.rankteams.append(CalendarizedTeam.CalendarizedTeam(rtapi.get_team_from_id(int(data[0])), int(data[1]), int(data[2]), int(data[3]), int(data[4]), int(data[5]), p, int(data[6]), int(data[7])))
            self.calendar = frapi.circle_method(num_teams)
            self.cur_day = int(f.readline())
            self.cur_match = int(f.readline())
        
        self.update_ranking()
        self.next_match = self.calendar[self.cur_day][self.cur_match]
        #self.init_teams_for_match(self.next_match[0], self.next_match[1])
        
        self.start_next_match()
        
        self.widgets_new["label_info_match"].configure(text='Season loaded!')

        return
    
    def start_next_match(self):
        if self.mode == 1:
            self.invert_teams()
        elif self.mode == 2:
            ghost = self.init_teams_for_match(self.next_match[0], self.next_match[1])
            if ghost:
                self.widgets_new["button_next"].configure(state='normal')
            else:
                self.widgets_new["button_next"].configure(state='disabled')
            

    def start_match(self):
        
        self.rankteams.sort(key=lambda x: x.calendar_index)
        team1 = self.rankteams[self.next_match[0]]
        team2 = self.rankteams[self.next_match[1]]
        
        self.init_teams_for_match(self.next_match[0], self.next_match[1])

        # disabling button for match start
        self.widgets_new["button_start"].configure(state="disabled")
        self.widgets_new["button_next"].configure(state="disabled")

        self.widgets_new["label_info_match"].configure(text="LIVE MATCH")

        # match simulation
        self.simulate_match_handler(team1, team2)

    def format_table(self) -> tuple[str, str, str, str]:
        if len(self.rankteams) > 0:
            self.rankteams.sort(key=lambda x: (x.points, x.get_gd(), x.gf), reverse=True)
        
        str_rank = "#\n"
        str_teams = "TEAM\n"
        str_played = "PLAYED\n"
        str_goals = "GOALS\n"
        str_points = "PTS\n"
        pos=1
        for t in self.rankteams:
            str_rank = str_rank + str(pos) + "\n"
            str_teams = str_teams + t.get_name() + "\n"
            str_played = str_played + t.get_str_matches() + "\n"
            str_goals = str_goals + t.get_str_goals() + "\n"
            str_points = str_points + str(t.get_points()) + "\n"
            pos+=1
        return str_rank[:-1], str_teams[:-1], str_played[:-1], str_goals[:-1], str_points[:-1]
    
    def update_ranking(self):
        str_rank, str_teams, str_played, str_goals, str_points = self.format_table()
        self.widgets_new["label_all_ranks"].configure(text=str_rank)
        self.widgets_new["label_all_teams"].configure(text=str_teams)
        self.widgets_new["label_all_played"].configure(text=str_played)
        self.widgets_new["label_all_goals"].configure(text=str_goals)
        self.widgets_new["label_all_points"].configure(text=str_points)
        return
    
    def set_next_match(self):

        if self.mode == 2:
            self.cur_match += 1
            if self.cur_match >= len(self.calendar[self.cur_day]):
                self.cur_match = 0
                self.cur_day += 1
            if self.cur_day >= len(self.calendar):
                self.widgets_new["label_info_match"].configure(text="SEASON OVER")
                self.widgets_new["button_next"].configure(state="disabled")
            else:
                self.next_match = self.calendar[self.cur_day][self.cur_match]

    def clean_match_text_boxes(self):
            list_delete = self.widgets_new["frame_match_info_left"].winfo_children() + self.widgets_new["frame_match_info_right"].winfo_children()
            for x in list_delete:
                x.pack_forget()
            tk.Frame(self.widgets_new["frame_match_info_left"]).pack()
            tk.Frame(self.widgets_new["frame_match_info_right"]).pack()
            self.widgets_new["frame_match_info_left"].update_idletasks()
            self.widgets_new["frame_match_info_right"].update_idletasks()
            list_delete = self.widgets_new["frame_match_info_left"].winfo_children() + self.widgets_new["frame_match_info_right"].winfo_children()
            for x in list_delete:
                x.pack_forget()

    def init_teams_for_match(self, ind_1: int, ind_2: int) -> bool:

        if (self.calendar[self.cur_day][self.cur_match][0] == len(self.rankteams) or self.calendar[self.cur_day][self.cur_match][1] == len(self.rankteams)):
            self.set_next_match()

        try:
            self.rankteams.sort(key=lambda x: x.calendar_index)

            team1 : Team.Team = self.rankteams[ind_1].get_team()
            team2 : Team.Team = self.rankteams[ind_2].get_team()

            self.widgets_new["label_team1name"].configure(text=team1.get_name())
            self.widgets_new["label_team2name"].configure(text=team2.get_name())
            self.widgets_new["label_team1country"].configure(text=team1.get_country())
            self.widgets_new["label_team2country"].configure(text=team2.get_country())
            self.widgets_new["label_team1goals"].configure(text=str(0))
            self.widgets_new["label_team2goals"].configure(text=str(0))

            self.clean_match_text_boxes()

            self.match_colours[0] = team1.get_colours()
            self.match_colours[1] = team2.get_colours()

            self.widgets_new["frame_match_info_left"].configure(bg=f"{self.match_colours[0][0]}")
            self.widgets_new["frame_match_info_right"].configure(bg=f"{self.match_colours[1][0]}")
            self.widgets_new["canvas_match_info_left"].configure(bg=f"{self.match_colours[0][0]}", highlightbackground=f"{self.match_colours[0][1]}")
            self.widgets_new["canvas_match_info_right"].configure(bg=f"{self.match_colours[1][0]}", highlightbackground=f"{self.match_colours[1][1]}")

            if self.home_adv == 1:
                tmp = team1.get_stadium_name()
                if tmp == rtapi.DEFAULT_STADIUM_NAME:
                    tmp = team1.get_name() + " " + tmp
                self.widgets_new["label_matchstadium"].configure(text=tmp)
            else:
                self.widgets_new["label_matchstadium"].configure(text="Neutral location")

            self.set_team_img(ind_1, True)
            self.set_team_img(ind_2, False)

            self.widgets_new["label_info_match"].configure(text="PRE MATCH")
            #self.widgets_new["label_minute"].lower()

            str_rank, str_teams, str_played, str_goals, str_points = self.format_table()
            self.widgets_new["label_all_ranks"].configure(text=str_rank)
            self.widgets_new["label_all_teams"].configure(text=str_teams)
            self.widgets_new["label_all_played"].configure(text=str_played)
            self.widgets_new["label_all_goals"].configure(text=str_goals)
            self.widgets_new["label_all_points"].configure(text=str_points)

            # enabling the start button for the match to actually be played
            self.widgets_new["button_start"].configure(state="normal")

            return False
        except:
            print("Ghost...")
            # adding last result to box
            try:
                name = self.rankteams[ind_1].get_name()
            except:
                name = self.rankteams[ind_2].get_name()
            text = f"{name} resting for this round"
            self.update_past_matches(text)

            return True

        
    def update_past_matches(self, new_text: str):
        for i in reversed(range(1,10)):
            self.widgets_new[f"label_pastmatch{i}"].configure(text=self.widgets_new[f"label_pastmatch{i-1}"]["text"])
        self.widgets_new[f"label_pastmatch{0}"].configure(text=new_text)

    def update_bboxes(self):
        # this update is needed to not forget the first label inserted (otherwise not showing)
        self.widgets_new["frame_match_info_left"].update_idletasks()
        tmp_bbox = self.widgets_new["canvas_match_info_left"].bbox(tk.ALL)
        self.widgets_new["canvas_match_info_left"].configure(scrollregion=tmp_bbox)
        self.widgets_new["canvas_match_info_right"].configure(scrollregion=tmp_bbox)

                

    def min_event(self, team1: CalendarizedTeam.CalendarizedTeam, team2: CalendarizedTeam.CalendarizedTeam, ovr1: int, ovr2: int, g_coeff: int, subs_alr_1: int, subs_alr_2: int, slots_alr_1: int, slots_alr_2: int, goals_1: int, goals_2: int, f_time: list, s_time: list):

        speed = int(self.widgets_new["scale_speed"].get())
        
        is_first_half = True
        f_time_next = []
        s_time_next = []

        if len(f_time) > 0:
            min = f_time[0]
            f_time_next = f_time[1:]
            s_time_next = s_time
        elif len(s_time) > 0:
            min = s_time[0]
            is_first_half = False
            f_time_next = f_time
            s_time_next = s_time[1:]
        else:
            # means the match ended: NEED TO RE ENABLE AND HANDLE EVERYTHING HERE, AFTER THE AFTER METOD !!!
            tk.Label(self.widgets_new["frame_match_info_left"], anchor=tk.CENTER, text="- - - - - MATCH OVER - - - - -", font=(self.fonts["match_live_comment"], 10, "bold"), bg=self.match_colours[0][0], fg=self.match_colours[0][-1]).pack(fill=tk.X)
            tk.Label(self.widgets_new["frame_match_info_right"], anchor=tk.CENTER, text="- - - - - MATCH OVER - - - - -", font=(self.fonts["match_live_comment"], 10, "bold"), bg=self.match_colours[1][0], fg=self.match_colours[1][-1]).pack(fill=tk.X)
            self.update_bboxes()

            self.widgets_new["label_info_match"].configure(text="MATCH OVER")

            # re-enabling the start and next match button
            if self.mode != 2:
                self.widgets_new["button_start"].configure(state="normal")
            self.widgets_new["button_next"].configure(state="normal")

            # adding last result to box
            text = f"{team1.get_name()} {goals_1} - {goals_2} {team2.get_name()}"
            self.update_past_matches(text)

            # updating ranking in top right box
            self.rankteams.sort(key=lambda x:x.calendar_index)
            self.rankteams[team1.calendar_index].update_post_match(goals_1, goals_2)
            self.rankteams[team2.calendar_index].update_post_match(goals_2, goals_1)
            self.update_ranking()

            self.set_next_match()
            
            return

        # set current min in minute box in gui
        min_str = str(min) + "'"
        if is_first_half and min > 45:
            min_str = str(45) + "+" + str(min-45) + "'"
        elif not is_first_half and min > 90:
            min_str = str(90) + "+" + str(min-90) + "'"
        self.widgets_new["label_minute"].configure(text=min_str)

        tmp_subs_1, tmp_subs_2, tmp_slots_1, tmp_slots_2, tmp_less_1, tmp_less_2, num_goals_1, num_goals_2, ovr_change_1, ovr_change_2, str_event, which_team = frapi.minute_event(min, is_first_half, ovr1, ovr2, g_coeff, subs_alr_1, subs_alr_2, slots_alr_1, slots_alr_2, goals_1, goals_2)
        
        num_subs_1 = tmp_subs_1
        num_subs_2 = tmp_subs_2
        num_slots_1 = tmp_slots_1
        num_slots_2 = tmp_slots_2
        num_goals_1 += goals_1
        num_goals_2 += goals_2

        cur_ovr_1 = ovr_change_1 + ovr1
        cur_ovr_2 = ovr_change_2 + ovr2

        #print(min, cur_ovr_1, cur_ovr_2, num_subs_1, num_slots_1, num_subs_2, num_slots_2)

        if min==1:
            #tk.Label(self.widgets_new["frame_match_info_left"], anchor=tk.CENTER, text="", font=(self.fonts["main"], 10, "bold"), bg=self.match_colours[0][0], fg=self.match_colours[0][-1]).pack(fill=tk.X)
            #tk.Label(self.widgets_new["frame_match_info_right"], anchor=tk.CENTER, text="", font=(self.fonts["main"], 10, "bold"), bg=self.match_colours[1][0], fg=self.match_colours[1][-1]).pack(fill=tk.X)
            tk.Label(self.widgets_new["frame_match_info_left"], anchor=tk.CENTER, text="- - - - - MATCH START - - - - -", font=(self.fonts["match_live_comment"], 10, "bold"), bg=self.match_colours[0][0], fg=self.match_colours[0][-1]).pack(fill=tk.X)
            tk.Label(self.widgets_new["frame_match_info_right"], anchor=tk.CENTER, text="- - - - - MATCH START - - - - -", font=(self.fonts["match_live_comment"], 10, "bold"), bg=self.match_colours[1][0], fg=self.match_colours[1][-1]).pack(fill=tk.X)

        if min==46 and not is_first_half:
            tk.Label(self.widgets_new["frame_match_info_left"], anchor=tk.CENTER, text="- - - - - HALF TIME - - - - -", font=(self.fonts["match_live_comment"], 10, "bold"), bg=self.match_colours[0][0], fg=self.match_colours[0][-1]).pack(fill=tk.X)
            tk.Label(self.widgets_new["frame_match_info_right"], anchor=tk.CENTER, text="- - - - - HALF TIME - - - - -", font=(self.fonts["match_live_comment"], 10, "bold"), bg=self.match_colours[1][0], fg=self.match_colours[1][-1]).pack(fill=tk.X)

        if which_team!=0:
            
            bold_text = False
            if num_goals_1 != goals_1:
                    #time.sleep(1)
                    self.widgets_new["label_team1goals"].configure(text=f"{num_goals_1}")
                    bold_text = True
            if num_goals_2 != goals_2:
                    #time.sleep(1)
                    self.widgets_new["label_team2goals"].configure(text=f"{num_goals_2}")
                    bold_text = True
            tk.Label(self.widgets_new["frame_match_info_left"], anchor=tk.W, text=str_event if which_team==1 else "", font=(self.fonts["match_live_comment"], 7, "bold" if bold_text else ""), bg=self.match_colours[0][0], fg=self.match_colours[0][-1]).pack(padx=4, pady=2, fill=tk.X)
            tk.Label(self.widgets_new["frame_match_info_right"], anchor=tk.E, text=str_event if which_team==2 else "", font=(self.fonts["match_live_comment"], 7, "bold" if bold_text else ""), bg=self.match_colours[1][0], fg=self.match_colours[1][-1]).pack(padx=4, pady=2, fill=tk.X)

            self.update_bboxes()

            #print(f"increase bbox= {tmp}")
        
        # this line below: recursive call to itself with updated stuff in order to do everything the right moment!
        self.frame.after(speed, (lambda : self.min_event(team1, team2, cur_ovr_1, cur_ovr_2, g_coeff, num_subs_1, num_subs_2, num_slots_1, num_slots_2, num_goals_1, num_goals_2, f_time_next, s_time_next)))



    def simulate_match_handler(self, team1: CalendarizedTeam.CalendarizedTeam, team2: CalendarizedTeam.CalendarizedTeam):

        goals_1 = 0
        goals_1t = 0
        goals_2 = 0
        goals_2t = 0

        subs_alr_1 = 0
        subs_alr_2 = 0
        slots_alr_1 = 0
        slots_alr_2 = 0

        players_t1 = 11
        players_t2 = 11
        less_t1 = 0
        less_t2 = 0


        f_time = frapi.get_first_half_mins()
        s_time = frapi.get_second_half_mins()

        if self.home_adv == 1:
            ovr1 = frapi.calc_team_ovr(team1.get_team(), True)
        else:
            ovr1 = frapi.calc_team_ovr(team1.get_team(), False)
        ovr2 = frapi.calc_team_ovr(team2.get_team(), False)

        # higher the goal coeff, more difficult to score a goal (every match has its own for the whole match)
        goal_coeff = frapi.get_goal_coeff(ovr1, ovr2)
        print(f"goal coeff = {goal_coeff}")

        print(team1.get_name(), ovr1, team1.get_market_val(), team1.calendar_index)
        print(team2.get_name(), ovr2, team2.get_market_val(), team2.calendar_index)

        #min_label_index = "label_minute"
        #team1_widget_index = self.get_widget_index("team1text")
        #team2_widget_index = self.get_widget_index("team2text")
            
        # ------------------------ MATCH SIMULATION HERE -----------------

        self.min_event(team1, team2, ovr1, ovr2, goal_coeff, subs_alr_1, subs_alr_2, slots_alr_1, slots_alr_2, goals_1, goals_2,  f_time, s_time)
        
        # ------------------------ MATCH SIMULATION ABOVE ----------------
        #print("FULL TIME:", team1.get_name(), goals_1, "-", goals_2, team2.get_name())


    def set_team_img(self, team_index: int, is_left_canvas: bool):

        str_index = 1
        if not is_left_canvas:
            str_index = 2

        str_widget = "canvas_team" + str(str_index) + "img"
        
        bytes_img = self.rankteams[team_index].get_team().get_img()

        file_like=io.BytesIO(bytes_img)
        img = Image.open(file_like)
        if self.old_badges != 0:
            content = img.getbbox()
            img = img.crop(content)
            x, y = img.size
            if x > y:
                img = img.resize((CANVAS_DIMS,int(CANVAS_DIMS*y/x)))
            else:
                img = img.resize((int(CANVAS_DIMS*x/y),CANVAS_DIMS))
        else:
            img = img.resize((CANVAS_DIMS,CANVAS_DIMS))
        imgtk = itk.PhotoImage(img)
        
        self.widgets_new[str_widget].create_image(CANVAS_DIMS/2,CANVAS_DIMS/2,anchor=tk.CENTER,image=imgtk)
        self.widgets_new[str_widget].imagelist = []
        self.widgets_new[str_widget].imagelist.append(imgtk)

    def set_friendly_gui(self, t1: Team.Team, t2: Team.Team):

        self.mode = 1

        self.teams[0] = t1
        self.teams[1] = t2

        self.rankteams.clear()
        self.rankteams.append( CalendarizedTeam.CalendarizedTeam(t1, 0, 0, 0, 0, 0, 0, 0, 0) )
        self.rankteams.append( CalendarizedTeam.CalendarizedTeam(t2, 1, 0, 0, 0, 0, 0, 0, 0) )
        
        self.calendar.clear()
        self.cur_day = 0
        self.cur_match = 0

        match1 = (0,1)
        day1 = [match1]
        self.calendar.append(day1)
        self.next_match = self.calendar[0][0]

        self.init_teams_for_match(self.next_match[0], self.next_match[1])


    def search_clubs(self):
        t1, t2 = SearchClubSelector(self)
        
        # after closing of second window
        #self.mode = 1

        self.set_friendly_gui(t1, t2)

        
    def season_init(self, teams_selected: list):

        self.mode = 2

        self.rankteams.clear()
        self.calendar.clear()
        self.cur_day = 0
        self.cur_match = 0
        random_indexes = list(range(len(teams_selected)))
        random.shuffle(random_indexes)
        for i in range(len(teams_selected)):
            self.rankteams.append( CalendarizedTeam.CalendarizedTeam(teams_selected[i], random_indexes[i], 0,0,0,0,0,0,0))

        self.calendar = frapi.circle_method(len(self.rankteams))
        self.next_match = self.calendar[0][0]

        ghost = self.init_teams_for_match(self.next_match[0], self.next_match[1])

        if ghost:
            self.widgets_new["button_next"].configure(state='normal')
        else:
            self.widgets_new["button_next"].configure(state='disabled')
        return
    

    def random_season_handler(self):

        num = RandomSeasonSelector(self)
        
        teams = rtapi.get_random_teams(self.old_badges, self.selected_pot, self.select_nat_teams, num)

        #self.mode = 2
        self.season_init(teams)

        return
    
    def real_season_handler(self):
        try:
            comp_id = RealSeasonSelector(self)
            print(comp_id)
            teams_ids = rtapi.get_ids_from_competition(comp_id, 2023)
            teams_selected = rtapi.get_teams_from_ids(teams_ids, self.old_badges)
            
            self.season_init(teams_selected)
            
        except:
            print("error during real season handler..., gui level")
        
        return

    

    def season_handler(self):
        try:
            teams_selected = SeasonHandlerMain(self)

            self.season_init(teams_selected)
            print(self.calendar)

        except:
            pass

        return

    def about_page(self):
        AboutPage(self)
        return

    def extract_league_num(self, c_str: str) -> int:
        return int(c_str.split()[1])
        

    def clear_all_teams(self):
        self.mode = 0
        '''for w in self.widgets_new:
            w.place_forget()'''
        self.teams.clear()
        self.teams.append(None)
        self.teams.append(None)
        self.rankteams.clear()
        self.update_ranking()
        self.rankteams.append(None)
        self.rankteams.append(None)
        self.calendar.clear()
        self.cur_day=0
        self.cur_match=0
        self.widgets_new["label_info_match"].configure(text=self.intro_text)
        #self.widgets_new["label_info_match"].lift()
        widgets_to_forget = []
        widgets_to_forget.append(self.widgets_new["label_team1name"])
        widgets_to_forget.append(self.widgets_new["label_team2name"])
        widgets_to_forget.append(self.widgets_new["label_team1country"])
        widgets_to_forget.append(self.widgets_new["label_team2country"])
        widgets_to_forget.append(self.widgets_new["label_team1img"])
        widgets_to_forget.append(self.widgets_new["label_team2img"])
        widgets_to_forget.append(self.widgets_new["label_team1goals"])
        widgets_to_forget.append(self.widgets_new["label_team2goals"])
        widgets_to_forget.append(self.widgets_new["label_goal_separator"])
        widgets_to_forget.append(self.widgets_new["label_matchstadium"])

        for w in widgets_to_forget:
            w.place_forget()

        # disabling button for match start and next
        self.widgets_new["button_start"].configure(state="disabled")
        self.widgets_new["button_next"].configure(state="disabled")

    def invert_teams(self):
        #self.teams[0], self.teams[1] = self.teams[1], self.teams[0]
        #self.rankteams[0], self.rankteams[1] = self.rankteams[1], self.rankteams[0]
        self.next_match = (1-self.next_match[0], 1-self.next_match[1])
        self.init_teams_for_match(self.next_match[0], self.next_match[1])

    def random_friendly(self):
        #self.mode = 1
        t1 = rtapi.get_random_team(self.old_badges, self.selected_pot, self.select_nat_teams)
        t2 = rtapi.get_random_team(self.old_badges, self.selected_pot, self.select_nat_teams)

        self.set_friendly_gui(t1,t2)

        return
    
    def prefs_page(self):

        options = PreferencesPage(self)

        self.old_badges = options[0]
        self.selected_pot = options[1]
        self.home_adv = options[2]
        self.select_nat_teams = options[3]

        print(options)

        return


def PreferencesPage(root: RootWindow):
    win_pref = tk.Toplevel()
    #win_pref.geometry("300x600+250+200")
    win_pref.title("About")
    #win_pref.resizable(False, False)
    win_pref.grab_set()

    ret_vals = [root.old_badges, root.selected_pot, root.home_adv, root.select_nat_teams]

    def save_changes(destroyer:bool):
        ret_vals[0] = select_badges.get()
        ret_vals[1] = select_pot.get()
        ret_vals[2] = select_home.get()
        ret_vals[3] = False
        if ret_vals[1] not in [0,1,2]:
            ret_vals[3] = select_nat_teams.get()
        if destroyer:
            win_pref.destroy()

    tk.Label(win_pref, text="PREFERENCES MENU", anchor=tk.NW, justify=tk.LEFT, font=(root.fonts["main"], 11, 'bold')).pack(padx=10, pady=10)

    tk.Label(win_pref, text="Team badges displayed in match", anchor=tk.NW, justify=tk.LEFT, font=(root.fonts["main"], 9, 'bold')).pack(anchor=tk.NW, padx=10, pady=10)
    select_badges = tk.IntVar(value=root.old_badges)
    tk.Radiobutton(win_pref, variable=select_badges, anchor=tk.W, height=1, width=35, value=0, font=(root.fonts["main"], 9), text="Current").pack(anchor=tk.NW, padx=10)
    tk.Radiobutton(win_pref, variable=select_badges, anchor=tk.W, height=1, width=35, value=1, font=(root.fonts["main"], 9), text="Oldest (not always correct)").pack(anchor=tk.NW, padx=10)
    tk.Radiobutton(win_pref, variable=select_badges, anchor=tk.W, height=1, width=35, value=2, font=(root.fonts["main"], 9), text="Random").pack(anchor=tk.NW, padx=10)
    tk.Radiobutton(win_pref, variable=select_badges, anchor=tk.W, height=1, width=35, value=-1, font=(root.fonts["main"], 9), text="Second-last").pack(anchor=tk.NW, padx=10)

    # -----

    tk.Label(win_pref, text="Team Randomizer Pots", anchor=tk.NW, justify=tk.LEFT, font=(root.fonts["main"], 9, 'bold')).pack(anchor=tk.NW, padx=10, pady=10)
    cb_pots = []
    select_pot = tk.IntVar(value=root.selected_pot)
    labels_pots = ["Top 25", "Top 100", "Top 1000"] + [f"Pot {i}" for i in range(1,5)] + ["Enhanced All For All", "Lowest ranking"]
    i=0
    for l in labels_pots:
        cb_pots.append( tk.Radiobutton(win_pref, anchor=tk.W, variable=select_pot, value=i, height=1, width=35, font=(root.fonts["main"], 9), text=l) )
        cb_pots[-1].pack(anchor=tk.NW, padx=10)
        i+=1

    # -----
        
    tk.Label(win_pref, text="Include National Teams in random selection", anchor=tk.NW, justify=tk.LEFT, font=(root.fonts["main"], 9, 'bold')).pack(anchor=tk.NW, padx=10, pady=10)
    select_nat_teams = tk.BooleanVar(value=root.select_nat_teams)
    tk.Radiobutton(win_pref, anchor=tk.W, variable=select_nat_teams, value=True, height=1, width=35, font=(root.fonts["main"], 9), text="No").pack(anchor=tk.NW, padx=10)
    tk.Radiobutton(win_pref, anchor=tk.W, variable=select_nat_teams, value=False, height=1, width=35, font=(root.fonts["main"], 9), text="Yes").pack(anchor=tk.NW, padx=10)

    # -----

    tk.Label(win_pref, text="Location of matches", anchor=tk.NW, justify=tk.LEFT, font=(root.fonts["main"], 9, 'bold')).pack(anchor=tk.NW, padx=10, pady=10)
    select_home = tk.IntVar(value=root.home_adv)
    tk.Radiobutton(win_pref, variable=select_home, anchor=tk.W, height=1, width=35, value=1, font=(root.fonts["main"], 9), text="Matches in home team stadium").pack(anchor=tk.NW, padx=10)
    tk.Radiobutton(win_pref, variable=select_home, anchor=tk.W, height=1, width=35, value=0, font=(root.fonts["main"], 9), text="Matches in neutral locations").pack(anchor=tk.NW, padx=10)

    # ----- save buttons

    tk.Button(win_pref, text="SAVE", width=10, font=(root.fonts["main"], 10, 'bold'), command=lambda:save_changes(False)).pack(side=tk.LEFT, padx = 10)
    tk.Button(win_pref, text="SAVE & CLOSE", width=20, fg='Red', font=(root.fonts["main"], 10, 'bold'), command=lambda:save_changes(True)).pack(side=tk.LEFT, padx = 10)


    win_pref.wait_window()
    return ret_vals



def AboutPage(root):
    window_about = tk.Toplevel()
    window_about.geometry("300x175+250+200")
    window_about.title("About")
    window_about.resizable(False, False)
    window_about.grab_set()

    colors = ['#E50000', '#FF8D00', '#FFEE00', '#028121', '#004CFF', '#770088']
    color_index=0

    canvas = tk.Canvas(window_about, width=100, height=100, highlightthickness=0)
    img = Image.open('img/about_emblem.png')
    img.thumbnail((90,90))
    imgtk = itk.PhotoImage(img)
    canvas.create_image(0,0,anchor=tk.NW,image=imgtk)
    canvas.imagelist = []
    canvas.imagelist.append(imgtk)
    canvas.place(x=150, y=30, anchor=tk.N)

    l_text = f'Football Randomizer v{VER} by Diroto, July 2023\nGitHub: td2002\nDiscord: @diroto'
    label = tk.Label(window_about, text=l_text, anchor=tk.CENTER, fg=colors[color_index], font=(root.fonts["main"], 8, 'bold'))
    label.place(x=150, y=145, anchor=tk.S)

    def change_color(colors, color_index):
        color_index = (color_index+1) % len(colors)
        label.config(fg = colors[color_index])
        window_about.after(1000, lambda : change_color(colors, color_index))
    
    window_about.after(1000, lambda : change_color(colors, color_index))


def RandomSeasonSelector(root) -> int:

    win_r_season = tk.Toplevel()
    win_r_season.geometry("300x200+250+200")
    win_r_season.title("Season Selector")
    win_r_season.resizable(False, False)
    win_r_season.grab_set()

    global amount
    amount = -1

    def save_amount():
        global amount
        try:
            amount = int(entry.get())
            win_r_season.destroy()
        except:
            label.config(text="Amount not valid! Please insert a valid one")

    label = tk.Label(win_r_season, text="Select the amount of teams in the new season")
    label.pack()

    entry = tk.Entry(win_r_season)
    entry.pack()

    btn = tk.Button(win_r_season, text="SAVE & CLOSE", command=save_amount)
    btn.pack()

    win_r_season.wait_window()
    return amount


def RealSeasonSelector(root):
    win_rss = tk.Toplevel()
    win_rss.geometry("300x300+250+200")
    win_rss.title("Real Season Selector")
    win_rss.resizable(False, False)
    win_rss.grab_set()
    
    country_num = 0
    comp_num = 0
    ret_comp_id:str
    
    with open("files/comps_final.txt", "r") as file_comps:
        data = file_comps.readlines()
    comps = []
    comps.append([])

    tmp = [str.strip(x) for x in data[0].split("§§§")]
    comps[0].append( tmp )

    for s in data:
        tmp = [str.strip(x) for x in s.split("§§§")]
        if comps[-1][0][0] == tmp[0]:
            comps[-1].append( tmp )
        else:
            comps.append([])
            comps[-1].append(tmp)
            
    #print(comps)
    ret_comp_id = None
    
    def change_country_left():
        nonlocal country_num
        nonlocal comp_num
        comp_num = 0
        country_num = (country_num-1) % len(comps)
        l_country.config(text = comps[country_num][0][0])
        l_comp_name.config(text = comps[country_num][comp_num][2])
        l_comp_tier.config(text = comps[country_num][comp_num][1])
        return
    def change_country_right():
        nonlocal country_num
        nonlocal comp_num
        comp_num = 0
        country_num = (country_num+1) % len(comps)
        l_country.config(text = comps[country_num][0][0])
        l_comp_name.config(text = comps[country_num][comp_num][2])
        l_comp_tier.config(text = comps[country_num][comp_num][1])
        return
    def change_comp_left():
        nonlocal comp_num
        nonlocal country_num
        comp_num = (comp_num-1) % len(comps[country_num])
        l_comp_name.config(text = comps[country_num][comp_num][2])
        l_comp_tier.config(text = comps[country_num][comp_num][1])
        return
    def change_comp_right():
        nonlocal comp_num
        nonlocal country_num
        comp_num = (comp_num+1) % len(comps[country_num])
        l_comp_name.config(text = comps[country_num][comp_num][2])
        l_comp_tier.config(text = comps[country_num][comp_num][1])
        return
    
    def select_comp():
        nonlocal ret_comp_id
        nonlocal country_num
        nonlocal comp_num
        ret_comp_id = comps[country_num][comp_num][4]
        win_rss.destroy()
        
    #print(comps)
    l_intro = tk.Label(win_rss, text="Select a real competition")
    l_intro.pack(expand=True)

    frame_1 = tk.Frame(win_rss)
    frame_1.pack(expand=True)
    
    btn_country_left = tk.Button(frame_1, text="<", command=change_country_left)
    btn_country_left.pack(side=tk.LEFT, expand=False)

    tk.Label(frame_1, text="Country").pack(side=tk.LEFT, expand=True, fill=tk.X)
    
    l_country = tk.Label(win_rss, text=comps[country_num][0][0], font=(root.fonts["main"], 9, "bold"))
    l_country.pack(fill=tk.X)
    
    btn_country_right = tk.Button(frame_1, text=">", command=change_country_right)
    btn_country_right.pack(side=tk.LEFT, expand=False)

    frame_2 = tk.Frame(win_rss)
    frame_2.pack(expand=True)
    
    btn_comp_left = tk.Button(frame_2, text="<", command=change_comp_left)
    btn_comp_left.pack(side=tk.LEFT)
    
    tk.Label(frame_2, text="Competition").pack(side=tk.LEFT, expand=True, fill=tk.X)

    l_comp_name = tk.Label(win_rss, text=comps[country_num][comp_num][2], font=(root.fonts["main"], 10, "bold"))
    l_comp_name.pack()
    
    btn_comp_right = tk.Button(frame_2, text=">", command=change_comp_right)
    btn_comp_right.pack(side=tk.LEFT)
    
    l_comp_tier = tk.Label(win_rss, text=comps[country_num][comp_num][1])
    l_comp_tier.pack()
    
    btn_ok = tk.Button(win_rss, text="LOAD COMPETITION", command=select_comp)
    btn_ok.pack(expand=True)

    win_rss.update()
    win_rss.minsize(win_rss.winfo_width(), win_rss.winfo_height())
    
    win_rss.wait_window()
    return ret_comp_id


def SeasonHandlerMain(root) -> list[Team.Team]:
    win_season_handler = tk.Toplevel()
    win_season_handler.geometry("700x650+100+100")
    win_season_handler.title("Select the teams in the tournament")
    win_season_handler.resizable(False, False)
    win_season_handler.grab_set()

    teams_current = []
    rb = []
    img_rb = []
    basics_got = []
    img_list = []
    imgs_cur = [None] * 10
    label_list = []

    def search_team_by_name_enter_bind(event):
        search_team_by_name()

    def search_team_by_name():

        name = "not working"
        try:
            name = in_text.get()
        except:
            pass
        
        basics_got.clear()
        for i in range(10):
            rb[i].place_forget()
            img_rb[i].place_forget()
        basics = rtapi.get_basics_from_search_name(name, 10)
        i=0
        for t in basics:
            if len(t) > 1:
                basics_got.append( t[0] )
                name = t[1]
                country = t[2]
                rb[i].configure(value=i)
                tmp = name + "\n(" + country + ")"
                rb[i].configure(text=tmp)
                rb[i].place(x=55, y=130+(45*i), anchor=tk.W)
                file_like=io.BytesIO(t[3])
                img = Image.open(file_like)
                img.thumbnail((30,30))
                imgtk = itk.PhotoImage(img)
                imgs_cur[i] = img
                img_rb[i].create_image(15,15,anchor=tk.CENTER,image=imgtk)
                img_rb[i].image = imgtk
                img_rb[i].place(x=20, y=130+(45*i), anchor=tk.W)
                i+=1
            else:
                break

        btn_add.config(state='normal')

    def add_selected_team():
        ind = select1.get()
        team = rtapi.get_team_from_id(basics_got[ind], root.old_badges)
        if team.get_name() not in [teams_current[i].get_name() for i in range(len(teams_current))]:
            teams_current.append(team)
            frame_list.config(height=10+len(teams_current)*40)
        
            img_list.append( tk.Canvas(frame_list, width=30, height=30, highlightthickness=0) )
            #imgtk = copy.deepcopy(img_rb[ind].imagelist)
            imgtk = itk.PhotoImage(imgs_cur[ind])
            img_list[-1].create_image(15,15,anchor=tk.CENTER, image=imgtk)
            img_list[-1].imagelist = []
            img_list[-1].imagelist.append(imgtk)
            img_list[-1].place(x=10, y=25+(len(teams_current)-1)*40, anchor=tk.W)

            tmp = team.get_name() + "\n(" + team.get_country() + ")"
            label_list.append( tk.Label(frame_list, anchor=tk.W, justify=tk.LEFT, text=tmp) )
            label_list[-1].place(x=50, y=25+(len(teams_current)-1)*40, anchor=tk.W)

            #frame_list.config(height=len(label_list)*40)
            list_teams.config(scrollregion=list_teams.bbox(tk.ALL))

        update_after_num_change()

    def remove_last_team():
        img_list[-1].place_forget()
        label_list[-1].place_forget()
        teams_current.pop()
        update_after_num_change()
        return
    
    def update_after_num_change():
        num = len(teams_current)
        if num < 1:
            btn_undo.config(state='disabled', bg='lightgrey')
        elif num >= 1:
            btn_undo.config(state='normal', bg='red')
        if num >= 2:
            btn_ok.config(state='normal', fg='white', bg='darkgreen')
            intro_label.config(text=f'READY TO START WITH THESE {len(teams_current)} TEAMS!')
        elif num < 2:
            btn_ok.config(state='disabled', fg='lightgrey', bg='grey94')
            intro_label.config(text="NOT ENOUGH TEAMS TO START A SEASON")
        

    in_text = tk.Entry(win_season_handler, width=26, font=(root.fonts["main"], 11), borderwidth=8)
    in_text.bind('<Return>', search_team_by_name_enter_bind)
    in_text.place(x=20, y=20)
    btn1 = tk.Button(win_season_handler, height=1, width=20, command=search_team_by_name, text="SEARCH TEAMS", borderwidth=6)
    btn1.place(x=20, y=60)


    select1 = tk.IntVar()
    for i in range(10):
        rb.append( tk.Radiobutton(win_season_handler, variable=select1, anchor=tk.W, justify=tk.LEFT, height=2, width=35, font=(root.fonts["main"], 9)) ) 
        img_rb.append( tk.Canvas(win_season_handler, width=30, height=30, highlightthickness=0) )

    btn_add = tk.Button(win_season_handler, command=add_selected_team, text="ADD SELECTED TEAM", width=20, font=(root.fonts["main"], 10, 'bold'), state='disabled')
    btn_add.place(x=20, y=630, anchor=tk.SW)

    

    list_teams = tk.Canvas(win_season_handler, width=350, height=500, highlightthickness=2, highlightbackground='Black')
    list_teams.place(x=320, y=320, anchor=tk.W)

    frame_list = tk.Frame(list_teams, width=350, height=10)
    list_teams.create_window(0,0, window=frame_list, anchor=tk.CENTER)

    intro_label = tk.Label(win_season_handler, text="NOT ENOUGH TEAMS TO START A SEASON", font=(root.fonts["main"], 10, 'bold'))
    intro_label.place(x=495, y=30, anchor=tk.N)

    btn_ok = tk.Button(win_season_handler, command=win_season_handler.destroy, text="START SEASON", width=20, font=(root.fonts["main"], 11, 'bold'), state='disabled')
    btn_ok.place(x=420, y=630, anchor=tk.SW)

    btn_undo = tk.Button(win_season_handler, command=remove_last_team, text="UNDO", width=6, font=(root.fonts["main"], 10, 'bold'), bg='lightgrey', state='disabled')
    btn_undo.place(x=240, y=630, anchor=tk.SW)

    list_teams.config(scrollregion=list_teams.bbox(tk.ALL))

    ############### Scroll Using Mouse Wheel ###############
    def scroll(event, widget):
        widget.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def final_scroll(event, widget, func):
        widget.bind_all("<MouseWheel>", func)

    def stop_scroll(event, widget):
        widget.unbind_all("<MouseWheel>")

    list_teams.bind("<Enter>", lambda event: final_scroll(event, list_teams, lambda event: scroll(event, list_teams)))
    list_teams.bind("<Leave>", lambda event: stop_scroll(event, list_teams))
    ################### code for scrolling bottom right box #####################

    win_season_handler.wait_window()
    return teams_current
    


def SearchClubSelector(root):

    win_searcher = tk.Toplevel()
    win_searcher.geometry("700x570+100+100")
    win_searcher.title("Select two teams for a friendly match")
    win_searcher.resizable(False, False)
    win_searcher.grab_set()

    in_text = []
    rb = []
    img_rb = []
    rb.append([])
    rb.append([])
    img_rb.append([])
    img_rb.append([])
    teams_got = []
    teams_got.append([])
    teams_got.append([])

    team1, team2 = None, None

    flags_start = [False, False]

    def search_team_by_name_enter1(event):
        search_team_by_name(0)
    def search_team_by_name_enter2(event):
        search_team_by_name(1)

    in_text.append( tk.Entry(win_searcher, width=26, font=(root.fonts["main"], 11), borderwidth=8) )
    in_text[0].bind('<Return>', search_team_by_name_enter1)
    in_text[0].place(x=20, y=20)
    btn1 = tk.Button(win_searcher, height=1, width=20, command=(lambda : search_team_by_name(0)), text="SEARCH TEAM 1", borderwidth=6)
    btn1.place(x=20, y=60)


    select1 = tk.IntVar()
    for i in range(10):
        rb[0].append( tk.Radiobutton(win_searcher, variable=select1, anchor=tk.W, height=2, width=34, font=(root.fonts["main"], 9), justify=tk.LEFT) ) 
        img_rb[0].append( tk.Canvas(win_searcher, width=30, height=30, highlightthickness=0) )

    select2 = tk.IntVar()
    for i in range(10):
        rb[1].append( tk.Radiobutton(win_searcher, variable=select2, anchor=tk.W, height=2, width=34, font=(root.fonts["main"], 9), justify=tk.LEFT) ) 
        img_rb[1].append( tk.Canvas(win_searcher, width=30, height=30, highlightthickness=0) )
    
    
    in_text.append( tk.Entry(win_searcher, width=24, font=(root.fonts["main"], 11), borderwidth=8) )
    in_text[1].bind('<Return>', search_team_by_name_enter2)
    in_text[1].place(x=680, y=20, anchor=tk.NE)
    btn2 = tk.Button(win_searcher, height=1, width=20, command=(lambda : search_team_by_name(1)), text="SEARCH TEAM 2", borderwidth=6)
    btn2.place(x=680, y=60, anchor=tk.NE)

    def save_and_return_teams():
        nonlocal team1
        nonlocal team2
        team1 = rtapi.get_team_from_id(teams_got[0][select1.get()], root.old_badges)
        team2 = rtapi.get_team_from_id(teams_got[1][select2.get()], root.old_badges)
        win_searcher.destroy()

    btn_ok = tk.Button(win_searcher, command=save_and_return_teams, text="START FRIENDLY", width=14, font=(root.fonts["main"], 10, 'bold'), state='disabled')
    btn_ok.place(x=350, y=40, anchor=tk.N)

    
    def set_loading_img():
        '''img_load = Image.open('img/loading.gif')
        img_load = img_load.resize((30,30))
        imgtk_load = itk.PhotoImage(img_load)
        img_rb[0][0].create_image(0,0,anchor=tk.NW,image=imgtk_load)
        img_rb[0][0].imagelist = []
        img_rb[0][0].imagelist.append(imgtk_load)'''
        print("ciao")

    def search_team_by_name(which: int):

        thr = threading.Thread(target=set_loading_img)
        thr.start()

        name = "not working"
        try:
            name = in_text[which].get()
        except:
            pass

        teams_got[which].clear()
        for i in range(10):
            rb[which][i].place_forget()
            img_rb[which][i].place_forget()
        basics = rtapi.get_basics_from_search_name(name, 10)

        thr.join()

        i=0
        for t in basics:
            if len(t) > 1:
                teams_got[which].append( t[0] )
                name = t[1]
                country = t[2]
                rb[which][i].configure(value=i)
                '''tmp = name + " (" + country + ")"
                if (len(tmp) > 32):'''
                tmp = name + "\n(" + country + ")"
                rb[which][i].configure(text=tmp)
                rb[which][i].place(x=55+(400*which), y=130+(45*i), anchor=tk.W)
                file_like=io.BytesIO(t[3])
                img = Image.open(file_like)
                img.thumbnail((30,30))
                imgtk = itk.PhotoImage(img)
                img_rb[which][i].create_image(15,15,anchor=tk.CENTER,image=imgtk)
                img_rb[which][i].imagelist = []
                img_rb[which][i].imagelist.append(imgtk)
                img_rb[which][i].place(x=20+(400*which), y=130+(45*i), anchor=tk.W)

                flags_start[which] = True
                if flags_start[0] and flags_start[1]:
                    btn_ok.config(state='normal')

                i+=1
            else:
                break


    win_searcher.wait_window()
    if (team1 is not None and team2 is not None):
        return team1, team2
    return





def main(): 
        
    root = tk.Tk()
    root.title('Football Randomizer')
    #root.resizable(False, False)
    #root.geometry("1100x700+50+50")
    root.minsize(1100,700)
    #root.iconbitmap(default='img/icon.ico')
    app = RootWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()
