from os import sep
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkinter.scrolledtext import ScrolledText

# Game takes vanillas based on their index in this list, so no touchy
VANILLAS = [
        "Empty",
        "Timer",
        "Wires",
        "BigButton",
        "Keypad",
        "Simon",
        "WhosOnFirst",
        "Memory",
        "Morse",
        "Venn",
        "WireSequence",
        "Maze",
        "Password",
        "NeedyVentGas",
        "NeedyCapacitor",
        "NeedyKnob"]
    
class AssetFile:

    # default settings/variable init
    def __init__(self):

        self.iden = "mission"
        self.name = "Mission"
        self.desciption = "a mission"
        self.time_limit = "300"
        self.strikes = "3"
        self.needy_activation_time = "90"
        self.front_only = 0
        self.widgets = "5"
        self.modules = ""
        self.separator = "\n"
        self.pacing = 1


    # ran when pressing the create button, returns true or false based on sanity()
    def enter(self, iden, name, description, time_limit, strikes, needy_activation_time, front_only, widgets, modules, separator, pacing):

        # takes all of the inputted info and puts it into AssetFile's variables if they weren't left blank
        self.iden = iden.strip() if iden.strip() != "" else self.iden
        self.name = name.strip() if name.strip() != "" else self.name
        self.desciption = description.strip() if "\'{}\'".format(description.strip()) != "" else self.desciption
        self.time_limit = time_limit.strip() if time_limit.strip() != "" else self.time_limit
        self.strikes = strikes.strip() if strikes.strip() != "" else self.strikes
        self.needy_activation_time = needy_activation_time.strip() if needy_activation_time.strip() != "" else self.needy_activation_time
        self.front_only = front_only
        self.widgets = widgets.strip() if widgets.strip() != "" else self.widgets
        self.modules = modules.strip() if modules.strip() != "" else self.modules
        switcher = {"newlines": "\n", "spaces": " ", "tabs": "\t"}
        self.separator = switcher.get(separator, "\n")
        self.pacing = pacing
        # stops the process if any of the variables don't pass the sanity check
        if not self.sanity():
            return False
        # string of pain, the whole asset file before the modlist is written here
        retstring = "%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!114 &11400000\nMonoBehaviour:\n  m_ObjectHideFlags: 0\n  m_PrefabParentObject: {{fileID: 0}}\n  m_PrefabInternal: {{fileID: 0}}\n  m_GameObject: {{fileID: 0}}\n  m_Enabled: 1\n  m_EditorHideFlags: 0\n  m_Script: {{fileID: -548183353, guid: 45b809be76fd7a3468b6f517bced6f28, type: 3}}\n  m_Name: {}\n  m_EditorClassIdentifier: {}\n  DisplayName: {}\n  Description: {}\n  GeneratorSetting:\n    TimeLimit: {}\n    NumStrikes: {}\n    TimeBeforeNeedyActivation: {}\n    FrontFaceOnly: {}\n    OptionalWidgetCount: {}\n    ComponentPools:".format(self.iden, self.iden, self.name, self.desciption, self.time_limit, self.strikes, self.needy_activation_time, str(self.front_only), self.widgets)
        modlist = self.modules.split(self.separator)
        for i in range(len(modlist)):
            count = 1   # how many of current module there is 
            vann = 1    # whether current module is vanilla, 1 is vanilla, 0 is modded
            component = ""  # vanilla modules are put in ComponentTypes rather than ModTypes, so seperate string to go under ComponentTypes
            modstring = " []"   # this goes under ModTypes, default without mods is here
            # this counts modules if more than one
            # example 2*module would set count to 2 and then continue with everything after 2*
            if "*" in modlist[i]:
                count = modlist[i][0]
                modlist[i] = modlist[i][2:]
            # this removes the formatting of [] around pools
            if "[" in modlist[i]:
                modlist[i] = modlist[i][1:-1]
            # even non-pooled modules are treated like a pool with one module, since they are formatted the same
            pooled = modlist[i].split(",")
            for module in pooled:
                # vanilla formatting: add 0{}000000 to ComponentTypes, where {} is the hex index in the earlier VANILLAS string
                if module in VANILLAS:
                    temp = str(hex(VANILLAS.index(module)))[2:]
                    component += "0{}000000".format(temp)
                else:
                    vann = 0    # set to zero because if there are mods, the default of " []" is wrong
                    modstring += "\n      - {}".format(module)
            # removes default " []"
            if vann == 0:
                modstring = modstring[3:]
            # finally adds the count, compenent, and modstring to what goes in the file below the string of pain
            retstring += "\n    - Count: {}\n      AllowedSources: 2\n      ComponentTypes: {}\n      SpecialComponentType: 0\n      ModTypes:{}".format(count, component, modstring)
        retstring += "\n  PacingEventsEnabled: {}".format(str(self.pacing)) # pacing goes below the mods for some reason
        retstring += "\n  # Mission Utility v0.2 by BlvdBroken" # version number for debugging
        # creates a .asset file with the name of the ID, since thats what Unity does as well
        f = open("{}.asset".format(self.iden), "w")
        f.write(retstring)
        f.close()
        #print(retstring)
        return True # returns True to show it passes the sanity check, important for createMission() in the Gui class


    # makes sure Unity nor your OS gets mad at you for your asset file, runs within enter()
    def sanity(self):

        # these first two are illegal characters in Win/Mac files as well as reserved filenames in Win
        illegalFileNameChars = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*", " ", "."]
        illegalFileNames = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"]
        if (self.iden.upper() in illegalFileNames):
            showinfo(title="Error", message="Illegal file name.")
            return False
        for chara in illegalFileNameChars:
            if chara in self.iden:
                showinfo(title="Error", message="Illegal character in mission ID.")
                return False
        # next four yell at you for having non-numerics in numbered inputs: time limit, strikes, needy activation time, and widgets
        if not self.time_limit.isnumeric():
            showinfo(title="Error", message="Illegal character in Time Limit.")
            return False
        if not self.strikes.isnumeric():
            showinfo(title="Error", message="Illegal character in Strikes.")
            return False
        if not self.needy_activation_time.isnumeric():
            showinfo(title="Error", message="Illegal character in Needy Activation Time.")
            return False
        if not self.widgets.isnumeric():
            showinfo(title="Error", message="Illegal character in Widgets.")
            return False
        # TODO figure out what characters cause the descriptions to throw a fit, or what I can include to make them acceptable
        # currently most special characters in the description break the file according to Unity, even though it's the exact same format if you enter it through Unity
        return True



class Gui(tk.Tk):

    # currently everything except createMission() runs in init, while not the best practice it makes the most sense for a GUI
    def __init__(self):

        super().__init__()

        self.title("Mission Asset Utility")
        self.geometry('900x750')

        iden = tk.StringVar()
        name = tk.StringVar()
        description = tk.StringVar()
        time_limit = tk.StringVar()
        strikes = tk.StringVar()
        needy_activation_time = tk.StringVar()
        front_only = tk.StringVar(value=0)
        widgets = tk.StringVar()
        #modules = tk.StringVar()
        separator = tk.StringVar()
        pacing = tk.StringVar(value=0)

        # using tk's grid functionality as it's very nice compared to other options
        # column 0 is for names while 1 is for inputs
        # row 8 is where module list goes
        self.columnconfigure(0, weight = 0)
        self.columnconfigure(1, weight = 20)
        self.rowconfigure(8, weight = 5)

        # sticky="WE" means it fills it's whole grid location left to right (west to east)
        iden_label = ttk.Label(self, text="Mission ID:")
        iden_label.grid(column=0, row=0, padx=10, pady=5)
        iden_box = ttk.Entry(self, textvariable=iden)
        iden_box.grid(column=1, row=0, sticky="WE", padx=10, pady=5)

        name_label = ttk.Label(self, text="Name:")
        name_label.grid(column=0, row=1, padx=10, pady=5)
        name_box = ttk.Entry(self, textvariable=name)
        name_box.grid(column=1, row=1, sticky="WE", padx=10, pady=5)

        description_label = ttk.Label(self, text="Description:")
        description_label.grid(column=0, row=2, padx=10, pady=5)
        description_box = ttk.Entry(self, textvariable=description)
        description_box.grid(column=1, row=2, sticky="WE", padx=10, pady=5)

        time_limit_label = ttk.Label(self, text="Time Limit:")
        time_limit_label.grid(column=0, row=3, padx=10, pady=5)
        time_limit_box = ttk.Entry(self, textvariable=time_limit)
        time_limit_box.grid(column=1, row=3, sticky="WE", padx=10, pady=5)

        strikes_label = ttk.Label(self, text="Strikes:")
        strikes_label.grid(column=0, row=4, padx=10, pady=5)
        strikes_box = ttk.Entry(self, textvariable=strikes)
        strikes_box.grid(column=1, row=4, sticky="WE", padx=10, pady=5)

        needy_activation_time_label = ttk.Label(self, text="Needy Activation Time:")
        needy_activation_time_label.grid(column=0, row=5, padx=10, pady=5)
        needy_activation_time_box = ttk.Entry(self, textvariable=needy_activation_time)
        needy_activation_time_box.grid(column=1, row=5, sticky="WE", padx=10, pady=5)

        widgets_label = ttk.Label(self, text="Widget Amount:")
        widgets_label.grid(column=0, row=6, padx=10, pady=5)
        widgets_box = ttk.Entry(self, textvariable=widgets)
        widgets_box.grid(column=1, row=6, sticky="WE", padx=10, pady=5)

        # TODO fix spaghetti code that was made in an attempt to make these look nice, don't ask what I was going for
        front_only_check = ttk.Checkbutton(self, text="Front Only", variable=front_only, onvalue=1, offvalue=0).grid(column=1, row=7, padx=10, pady=10)
        pacing_check = ttk.Checkbutton(self, text="Pacing Events", variable=pacing, onvalue=1, offvalue=0).grid(column=1, row=7, sticky="E", padx=10, pady=10, ipadx=100)

        # ScrolledText comes with a scrollbar, but it's only for up and down, so I add a Scrollbar to go left and right in case you are using spaces/tabs to separate
        modules_label = ttk.Label(self, text="Module List:")
        modules_label.grid(column=0, row=8, padx=10, pady=5)
        modules_box = ScrolledText(self, width=10, height=10, wrap=tk.NONE)
        modules_box.grid(column=1, row=8, sticky="NSEW", padx=10, pady=0)
        modules_scrollbar = ttk.Scrollbar(self, orient='horizontal', command=modules_box.xview)
        modules_scrollbar.grid(column=1, row=9, sticky="EW", padx=10)
        modules_box["xscrollcommand"] = modules_scrollbar.set

        # TODO make the sheet usable *before* you select this, no idea why this happens
        separator_label = ttk.Label(self, text="Separator:")
        separator_label.grid(column=0, row=10, padx=10, pady=5)
        separator_box = ttk.Combobox(self, textvariable=separator)
        separator_box['values'] = ["newlines", "spaces", "tabs"]
        separator_box['state'] = 'readonly'
        separator_box.grid(column=1, row=10, sticky="W", padx=10, pady=5)

        # runs createMission() with all of the info in the other boxes when pressed
        enter_button = ttk.Button(self, text="Create Asset File", command=lambda: self.createMission(iden.get(), name.get(), description.get(), time_limit.get(), strikes.get(), needy_activation_time.get(), front_only.get(), widgets.get(), modules_box.get("1.0", "end"), separator.get(), pacing.get())).grid(column=1, row=11, padx=10, pady=5)

        # shows you the defaults and some important notes before you start
        showinfo(title="Info", message="Defaults:\n  ID: mission\n  Name: Mission\n  Description: a mission\n  Time Limit: 300\n  Strikes: 3\n  Needy Activation Time: 90\n  Widgets: 5\n\nNote: All times are in seconds.\n\nThe module list should use the module ID's, which can be found at ktane.timwi.de")

        # this is important for the tk gui, I imagine it just runs a constant update
        self.mainloop()


    # ran when enter button is pressed, creates a new AssetFile and then tells you it worked if it passes the sanity check
    def createMission(self, iden, name, desciption, time_limit, strikes, needy_activation_time, front_only, widgets, modules, separator, pacing):

        created_mission = AssetFile()
        if created_mission.enter(iden, name, desciption, time_limit, strikes, needy_activation_time, front_only, widgets, modules, separator, pacing):
            showinfo(title="You did it!", message="Mission file created and downloaded.")


def main():
    Gui()

if __name__ == "__main__":
    main()