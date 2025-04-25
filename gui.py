import customtkinter as ctk
import threading
import f1_analysis 
from PIL import Image
from f1_analysis import TEAM_COLORS

# Load session from inputs
def on_load_session():
    
    def load_and_plot():
        mode = mode_var.get()
        year = year_var.get()
        grand_prix = gp_var.get()
        session_type = session_var.get()
        driver1 = driver1_var.get()
        driver2 = driver2_var.get()
        
        if not driver1 or not driver2:
            ctk.CTkMessagebox(title="Error", message="Please enter both driver names.", icon="cancel")
            return

        session = f1_analysis.load_session(mode, year, grand_prix, session_type)

        if session:
            if session_type == "Qualifying":
                f1_analysis.plot_best_laps(session)
                f1_analysis.plot_lap_comparison(session, driver1, driver2)
                f1_analysis.plot_track_dominance(session, driver1, driver2)
                f1_analysis.plot_max_speeds(session)
            elif session_type == "Race":
                f1_analysis.plot_stint_comparison(session, [driver1, driver2], TEAM_COLORS)
                f1_analysis.plot_lap_time_distribution(session, TEAM_COLORS)
            elif session_type in ["FP1", "FP2", "FP3"]:
                f1_analysis.plot_best_laps(session)
                f1_analysis.plot_lap_time_distribution(session, TEAM_COLORS)
                f1_analysis.plot_lap_comparison(session, driver1, driver2)
                f1_analysis.plot_max_speeds(session)    

    load_and_plot()

# Start GUI
def run_gui():
    global root, mode_var, year_var, gp_var, session_var, driver1_var, driver2_var

    ctk.set_appearance_mode("light")  
    ctk.set_default_color_theme("blue")  

    root = ctk.CTk()
    root.title("F1 Telemetry Analyzer")
    root.geometry("800x600") 
    root.configure(fg_color="white")

    # Load background image
    image = Image.open("F1-Logo.png")
    bg_image = ctk.CTkImage(light_image=image, dark_image=image, size=(300, 150))  # Background image

    # Frame for layout
    frame = ctk.CTkFrame(root, fg_color="white", corner_radius=20, border_color='black', border_width=3, width=900, height=600)  
    frame.place(relx=0.5, rely=0.5, anchor="center")

    # Ensure columns expand evenly
    for i in range(3):
        frame.grid_columnconfigure(i, weight=1)

    # Title Label
    title_label = ctk.CTkLabel(frame, text="F1 ANALYSIS", font=("Segoe UI", 36, "italic", "bold"), fg_color="white", text_color="black")
    title_label.grid(row=0, column=0, columnspan=3, pady=20)

    # Mode Selection
    mode_label = ctk.CTkLabel(frame, text="Select Mode:", font=("Segoe UI", 18, "bold"), fg_color="white", text_color="black")
    mode_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    mode_var = ctk.StringVar(value="Grand Prix")
    mode_menu = ctk.CTkComboBox(frame, variable=mode_var, values=["Grand Prix"], font=("Segoe UI", 16,"bold"), width=130, justify="center")
    mode_menu.grid(row=1, column=1, columnspan=2, padx=10, pady=10)

    # Year, Grand Prix, Session
    year_var = ctk.StringVar(value="Select Year")
    year_menu = ctk.CTkComboBox(frame, variable=year_var, values=["2025","2024", "2023","2022","2021","2020","2019","2018"], font=("Segoe UI", 16,"bold"), width=130, justify="center")
    year_menu.grid(row=2, column=0, padx=10, pady=10)

    gp_var = ctk.StringVar(value="Select GP")
    gp_menu = ctk.CTkComboBox(frame, variable=gp_var, values=["Bahrain", "Saudi Arabia", "Australia", "Japan", "China", "Miami", "Emilia Romagna", "Monaco", "Canada", "Spain", "Austria", "Silverstone", "Hungary", "Belgium", "Netherlands", "Italy", "Azerbaijan", "Singapore", "Austin", "Mexico", "Brazil", "Las Vegas", "Qatar", "Abu Dhabi"], font=("Segoe UI", 16,"bold"), width=120, justify="center")
    gp_menu.grid(row=2, column=1, padx=10, pady=10)

    session_var = ctk.StringVar(value="Select Session")
    session_menu = ctk.CTkComboBox(frame, variable=session_var, values=["FP1", "FP2", "FP3", "Qualifying", "Race"], font=("Segoe UI", 16,"bold"), width=142, justify="center")
    session_menu.grid(row=2, column=2, padx=10, pady=10)

    # Image in the middle
    bg_label = ctk.CTkLabel(frame, image=bg_image, text="")
    bg_label.grid(row=3, column=0, columnspan=3)

    # Driver 1
    driver1_var = ctk.StringVar(value='Insert Driver 1')
    driver1_entry = ctk.CTkEntry(frame, textvariable=driver1_var, placeholder_text="Driver 1", width=120, font=("Segoe UI", 16,"bold"), justify="center")
    driver1_entry.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    # Driver 2
    driver2_var = ctk.StringVar(value='Insert Driver 2')
    driver2_entry = ctk.CTkEntry(frame, textvariable=driver2_var, placeholder_text="Driver 2", width=120, font=("Segoe UI", 16,"bold"), justify="center")
    driver2_entry.grid(row=4, column=1, columnspan=2, pady=20)

    # Load Session Button
    load_button = ctk.CTkButton(frame, text="Load Session", command=on_load_session, font=("Segoe UI", 18, "bold"), fg_color="#FF0000", text_color="white", corner_radius=20, width=200, height=50)
    load_button.grid(row=5, column=0, columnspan=3, pady=20)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
