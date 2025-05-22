import flet as ft
import random
import os
import datetime
import polars as pl
import matplotlib
# Set matplotlib to use non-GUI backend to prevent thread warnings
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Create data directory if it doesn't exist
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(data_dir, exist_ok=True)
data_file = os.path.join(data_dir, "game_data.csv")

# Initialize or load game data with better error handling
try:
    if os.path.exists(data_file):
        try:
            # Load CSV with explicit schema to ensure consistent data types
            df = pl.read_csv(data_file, dtypes={
                "timestamp": pl.Utf8,
                "player_choice": pl.Utf8,
                "computer_choice": pl.Utf8,
                "result": pl.Utf8,
                "session_id": pl.Utf8
            })
            
            # Verify required columns exist
            required_cols = ["timestamp", "player_choice", "computer_choice", "result", "session_id"]
            if not all(col in df.columns for col in required_cols):
                raise ValueError("CSV file is missing required columns")
        except Exception as e:
            print(f"Error loading game data: {e}")
            df = pl.DataFrame({
                "timestamp": [],
                "player_choice": [],
                "computer_choice": [],
                "result": [],
                "session_id": []
            }, schema={
                "timestamp": pl.Utf8,
                "player_choice": pl.Utf8,
                "computer_choice": pl.Utf8,
                "result": pl.Utf8,
                "session_id": pl.Utf8
            })
    else:
        df = pl.DataFrame({
            "timestamp": [],
            "player_choice": [],
            "computer_choice": [],
            "result": [],
            "session_id": []
        }, schema={
            "timestamp": pl.Utf8,
            "player_choice": pl.Utf8,
            "computer_choice": pl.Utf8,
            "result": pl.Utf8,
            "session_id": pl.Utf8
        })
except Exception as e:
    print(f"Error initializing data: {e}")
    df = pl.DataFrame({
        "timestamp": [],
        "player_choice": [],
        "computer_choice": [],
        "result": [],
        "session_id": []
    }, schema={
        "timestamp": pl.Utf8,
        "player_choice": pl.Utf8,
        "computer_choice": pl.Utf8,
        "result": pl.Utf8,
        "session_id": pl.Utf8
    })

def main(page: ft.Page):
    page.title = "Rock Paper Scissors Dashboard"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1000
    page.window_height = 800
    page.padding = 10
    page.bgcolor = ft.Colors.WHITE
    page.scroll = ft.ScrollMode.AUTO

    # Create a unique session ID
    session_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # Game variables
    player_score = 0
    computer_score = 0
    ties = 0
    choices = ["rock", "paper", "scissors"]
    
    # Header
    header = ft.Container(
        content=ft.Column([
            ft.Text("Rock Paper Scissors Dashboard", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
            ft.Text("Play, track your progress, and analyze your performance", size=16, italic=True)
        ]),
        padding=10,
        margin=ft.margin.only(bottom=20),
    )
    
    # Initialize tabs
    tab_bar = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Play Game"),
            ft.Tab(text="Statistics"),
            ft.Tab(text="History")
        ],
        expand=True,
    )

    # Game Tab Content
    # Score display
    score_text = ft.Text(f"Player: {player_score} - Computer: {computer_score} - Ties: {ties}", 
                         size=18, weight=ft.FontWeight.BOLD)

    # Result display
    result_text = ft.Text("", size=22, color=ft.Colors.PRIMARY)

    # Choice icons
    rock_icon = ft.Icon(ft.Icons.SPORTS_HANDBALL, size=60)
    paper_icon = ft.Icon(ft.Icons.INSERT_DRIVE_FILE, size=60)
    scissors_icon = ft.Icon(ft.Icons.CONTENT_CUT, size=60)

    player_choice_display = ft.Container(
        content=ft.Column([
            ft.Text("You chose:", color=ft.Colors.BLUE_700),
            ft.Container(width=80, height=80, border_radius=40, bgcolor=ft.Colors.BLUE_50, 
                        content=ft.Icon(ft.Icons.QUESTION_MARK, size=40), alignment=ft.alignment.center)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        visible=False
    )
    
    computer_choice_display = ft.Container(
        content=ft.Column([
            ft.Text("Computer chose:", color=ft.Colors.RED_700),
            ft.Container(width=80, height=80, border_radius=40, bgcolor=ft.Colors.RED_50, 
                        content=ft.Icon(ft.Icons.QUESTION_MARK, size=40), alignment=ft.alignment.center)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        visible=False
    )

    # Stats containers
    stats_container = ft.Container(
        content=None,
        padding=20,
        expand=True
    )
    
    history_container = ft.Container(
        content=None,
        padding=20,
        expand=True
    )

    # Fixed visualization functions with error handling
    def generate_pie_chart():
        try:
            # Calculate win statistics
            if not os.path.exists(data_file) or df.shape[0] == 0:
                return ft.Text("No game data available yet. Play some games first!")
                
            results_count = df.group_by("result").agg(pl.count().alias("count"))
            
            # Create pie chart using non-interactive backend
            plt.figure(figsize=(8, 6))
            labels = results_count['result'].to_list()
            values = results_count['count'].to_list()
            colors = ['#4CAF50', '#F44336', '#2196F3']  # Green, Red, Blue for wins, losses, ties
            
            plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.axis('equal')
            plt.title('Game Results Distribution')
            
            # Save to BytesIO
            buf = BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            
            # Convert to base64 for embedding in flet
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            
            return ft.Image(
                src_base64=img_base64,
                width=400,
                height=300,
                fit=ft.ImageFit.CONTAIN
            )
        except Exception as e:
            print(f"Error generating pie chart: {e}")
            return ft.Text("Could not generate chart. Error occurred.")

    def generate_bar_chart():
        try:
            if not os.path.exists(data_file) or df.shape[0] == 0:
                return ft.Text("No game data available yet. Play some games first!")
            
            # Count choices
            player_choices = df.group_by("player_choice").agg(pl.count().alias("count"))
            
            # Create bar chart
            plt.figure(figsize=(8, 6))
            choices = player_choices['player_choice'].to_list()
            counts = player_choices['count'].to_list()
            
            bars = plt.bar(choices, counts, color=['#2196F3', '#4CAF50', '#F44336'])
            
            plt.xlabel('Choice')
            plt.ylabel('Frequency')
            plt.title('Your Choice Distribution')
            
            # Save to BytesIO
            buf = BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            
            # Convert to base64 for embedding in flet
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            
            return ft.Image(
                src_base64=img_base64,
                width=400,
                height=300,
                fit=ft.ImageFit.CONTAIN
            )
        except Exception as e:
            print(f"Error generating bar chart: {e}")
            return ft.Text("Could not generate chart. Error occurred.")

    def calculate_win_ratio():
        if not os.path.exists(data_file) or df.shape[0] == 0:
            return None, None, None
        
        total_games = df.shape[0]
        wins = df.filter(pl.col("result") == "Win").shape[0]
        losses = df.filter(pl.col("result") == "Loss").shape[0]
        ties = df.filter(pl.col("result") == "Tie").shape[0]
        
        win_ratio = wins / total_games if total_games > 0 else 0
        loss_ratio = losses / total_games if total_games > 0 else 0
        tie_ratio = ties / total_games if total_games > 0 else 0
        
        return win_ratio, loss_ratio, tie_ratio

    def update_stats_view():
        win_ratio, loss_ratio, tie_ratio = calculate_win_ratio()
        
        if win_ratio is None:
            stats_container.content = ft.Column([
                ft.Text("No game data available yet. Play some games first!", size=18)
            ])
            return
        
        pie_chart = generate_pie_chart()
        bar_chart = generate_bar_chart()
        
        # Create stats view
        stats_container.content = ft.Column([
            ft.Text("Game Statistics", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
            ft.Divider(),
            
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("Win Ratio", size=18, weight=ft.FontWeight.BOLD),
                        ft.ProgressBar(value=win_ratio, width=200, color=ft.Colors.GREEN_500),
                        ft.Text(f"{win_ratio:.1%}", size=16)
                    ]),
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.Colors.GREEN_50
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Loss Ratio", size=18, weight=ft.FontWeight.BOLD),
                        ft.ProgressBar(value=loss_ratio, width=200, color=ft.Colors.RED_500),
                        ft.Text(f"{loss_ratio:.1%}", size=16)
                    ]),
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.Colors.RED_50
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Tie Ratio", size=18, weight=ft.FontWeight.BOLD),
                        ft.ProgressBar(value=tie_ratio, width=200, color=ft.Colors.BLUE_500),
                        ft.Text(f"{tie_ratio:.1%}", size=16)
                    ]),
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.Colors.BLUE_50
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
            
            ft.Divider(),
            
            ft.Text("Results Distribution", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([pie_chart], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Divider(),
            
            ft.Text("Your Choice Patterns", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([bar_chart], alignment=ft.MainAxisAlignment.CENTER),
            
            # Additional stats
            ft.Divider(),
            
            ft.Text("Total Games Played", size=20, weight=ft.FontWeight.BOLD),
            ft.Text(f"{df.shape[0]}", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
        
        page.update()

    def update_history_view():
        if not os.path.exists(data_file) or df.shape[0] == 0:
            history_container.content = ft.Column([
                ft.Text("No game history available yet. Play some games first!", size=18)
            ])
            page.update()
            return
        
        # Create DataTable for history
        history_data = []
        
        # Sort by timestamp descending
        sorted_df = df.sort("timestamp", descending=True)
        
        # Get the last 30 games or all if less than 30
        recent_games = sorted_df.head(30)
        
        # Create table rows
        for row in recent_games.iter_rows(named=True):
            history_data.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(row["timestamp"])),
                        ft.DataCell(ft.Text(row["player_choice"].capitalize())),
                        ft.DataCell(ft.Text(row["computer_choice"].capitalize())),
                        ft.DataCell(
                            ft.Text(
                                row["result"], 
                                color=ft.Colors.GREEN_700 if row["result"] == "Win" else 
                                      ft.Colors.RED_700 if row["result"] == "Loss" else 
                                      ft.Colors.BLUE_700
                            )
                        ),
                    ]
                )
            )
        
        history_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Time")),
                ft.DataColumn(ft.Text("Your Choice")),
                ft.DataColumn(ft.Text("Computer's Choice")),
                ft.DataColumn(ft.Text("Result")),
            ],
            rows=history_data,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
            sort_column_index=0,
            sort_ascending=False,
        )
        
        # Create export button
        def export_to_excel(e):
            export_path = os.path.join(data_dir, "game_history.xlsx")
            df.write_excel(export_path)
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Exported to {export_path}"),
                action="OK"
            )
            page.snack_bar.open = True
            page.update()
        
        export_button = ft.ElevatedButton(
            "Export to Excel",
            icon=ft.Icons.DOWNLOAD,
            on_click=export_to_excel,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
            )
        )
        
        # Fix the Row with padding error by using Container instead
        history_container.content = ft.Column([
            ft.Text("Game History", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
            ft.Text("Recent Games (Last 30)", size=16, italic=True),
            history_table,
            ft.Container(
                content=ft.Row(
                    [export_button], 
                    alignment=ft.MainAxisAlignment.END
                ),
                padding=20
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
        
        page.update()

    # Function to handle game logic
    def play_game(player_choice):
        try:
            nonlocal player_score, computer_score, ties
            global df
            
            # Computer makes a random choice
            computer_choice = random.choice(choices)
            
            # Update icons
            choice_to_icon = {
                "rock": ft.Icons.SPORTS_HANDBALL,
                "paper": ft.Icons.INSERT_DRIVE_FILE,
                "scissors": ft.Icons.CONTENT_CUT
            }
            
            player_choice_display.visible = True
            player_choice_display.content.controls[1].content = ft.Icon(choice_to_icon[player_choice], size=40, color=ft.Colors.BLUE_700)
            
            computer_choice_display.visible = True
            computer_choice_display.content.controls[1].content = ft.Icon(choice_to_icon[computer_choice], size=40, color=ft.Colors.RED_700)
            
            # Determine the winner
            result = ""
            if player_choice == computer_choice:
                result_text.value = "It's a tie!"
                result_text.color = ft.Colors.BLUE_500
                ties += 1
                result = "Tie"
            elif ((player_choice == "rock" and computer_choice == "scissors") or
                  (player_choice == "paper" and computer_choice == "rock") or
                  (player_choice == "scissors" and computer_choice == "paper")):
                result_text.value = "You win!"
                result_text.color = ft.Colors.GREEN_500
                player_score += 1
                result = "Win"
            else:
                result_text.value = "Computer wins!"
                result_text.color = ft.Colors.RED_500
                computer_score += 1
                result = "Loss"
            
            # Update score
            score_text.value = f"Player: {player_score} - Computer: {computer_score} - Ties: {ties}"
            
            # Record the game data
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = pl.DataFrame({
                "timestamp": [timestamp],
                "player_choice": [player_choice],
                "computer_choice": [computer_choice],
                "result": [result],
                "session_id": [session_id]
            }, schema={
                "timestamp": pl.Utf8,
                "player_choice": pl.Utf8,
                "computer_choice": pl.Utf8,
                "result": pl.Utf8,
                "session_id": pl.Utf8
            })
            
            # Append to the dataframe
            df = pl.concat([df, new_row])
            
            # Save to CSV
            try:
                df.write_csv(data_file)
            except Exception as e:
                print(f"Error saving game data: {e}")
                # Show error message to user
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Failed to save game data"),
                    action="OK"
                )
                page.snack_bar.open = True
            
            # Update the stats views (but don't refresh them yet)
            if tab_bar.selected_index != 0:
                if tab_bar.selected_index == 1:
                    update_stats_view()
                elif tab_bar.selected_index == 2:
                    update_history_view()
        
            page.update()
        except Exception as e:
            print(f"Error in play_game: {e}")
            # Show error message to user
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Game error: {str(e)}"),
                action="OK"
            )
            page.snack_bar.open = True
            page.update()

    # Button click handlers
    def image_click(choice):
        def handle_click(e):
            play_game(choice)
        return handle_click

    def reset_click(e):
        nonlocal player_score, computer_score, ties
        player_score = 0
        computer_score = 0
        ties = 0
        result_text.value = ""
        score_text.value = f"Player: {player_score} - Computer: {computer_score} - Ties: {ties}"
        player_choice_display.visible = False
        computer_choice_display.visible = False
        page.update()

    # Choice buttons with icons
    rock_btn = ft.Container(
        content=ft.Column([
            rock_icon,
            ft.Text("Rock")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        on_click=image_click("rock"),
        ink=True,
        padding=20,
        margin=10,
        border_radius=10,
        bgcolor=ft.Colors.BLUE_50,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=8,
            color=ft.Colors.BLUE_GREY_100,
            offset=ft.Offset(2, 2),
        )
    )
    
    paper_btn = ft.Container(
        content=ft.Column([
            paper_icon,
            ft.Text("Paper")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        on_click=image_click("paper"),
        ink=True,
        padding=20,
        margin=10,
        border_radius=10,
        bgcolor=ft.Colors.GREEN_50,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=8,
            color=ft.Colors.BLUE_GREY_100,
            offset=ft.Offset(2, 2),
        )
    )
    
    scissors_btn = ft.Container(
        content=ft.Column([
            scissors_icon,
            ft.Text("Scissors")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        on_click=image_click("scissors"),
        ink=True,
        padding=20,
        margin=10,
        border_radius=10,
        bgcolor=ft.Colors.ORANGE_50,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=8,
            color=ft.Colors.BLUE_GREY_100,
            offset=ft.Offset(2, 2),
        )
    )
    
    choice_row = ft.Row(
        [rock_btn, paper_btn, scissors_btn],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY
    )
    
    # Results display
    result_display = ft.Column(
        [
            ft.Row([player_choice_display, computer_choice_display], 
                  alignment=ft.MainAxisAlignment.SPACE_EVENLY),
            result_text
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20
    )
    
    # Reset button
    reset_btn = ft.ElevatedButton(
        "Reset Game", 
        on_click=reset_click, 
        icon=ft.Icons.REFRESH,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
            padding=15
        )
    )

    # Game tab content
    game_content = ft.Container(
        content=ft.Column(
            [
                ft.Text("Let's play!", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                ft.Divider(),
                score_text,
                ft.Divider(),
                ft.Text("Choose your move:", size=16),
                choice_row,
                ft.Divider(),
                result_display,
                ft.Divider(),
                reset_btn
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        ),
        padding=30,
        border_radius=10,
        expand=True,
    )

    # Tab change handler
    def on_tab_change(e):
        try:
            selected_index = e.control.selected_index
            
            # Update visibility
            game_content.visible = selected_index == 0
            stats_container.visible = selected_index == 1
            history_container.visible = selected_index == 2
            
            # Load content for the selected tab
            if selected_index == 1:  # Stats tab
                update_stats_view()
            elif selected_index == 2:  # History tab
                update_history_view()
                
            page.update()
        except Exception as e:
            print(f"Error changing tabs: {e}")

    tab_bar.on_change = on_tab_change

    # Set up tab content
    tab_content = ft.Container(
        content=ft.Stack([
            game_content,       # Tab 0
            stats_container,    # Tab 1
            history_container,  # Tab 2
        ]),
        expand=True,
        padding=10,
    )

    # Update visibility based on selected tab
    def update_tab_visibility():
        selected_index = tab_bar.selected_index
        game_content.visible = selected_index == 0
        stats_container.visible = selected_index == 1
        history_container.visible = selected_index == 2
        page.update()

    tab_bar.on_change = lambda e: (on_tab_change(e), update_tab_visibility())

    # Initialize tab visibility explicitly
    game_content.visible = True
    stats_container.visible = False
    history_container.visible = False

    # Add debug button to help identify issues
    def debug_info(e):
        info = f"""
        Tab index: {tab_bar.selected_index}
        Game content visible: {game_content.visible}
        Stats visible: {stats_container.visible}
        History visible: {history_container.visible}
        Data rows: {df.shape[0]}
        """
        # Create a function to close the dialog
        def close_dialog(e):
            page.dialog.open = False
            page.update()
            
        page.dialog = ft.AlertDialog(
            title=ft.Text("Debug Info"),
            content=ft.Text(info),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ]
        )
        page.dialog.open = True
        page.update()

    debug_btn = ft.ElevatedButton(
        "Debug",
        on_click=debug_info,
        icon=ft.Icons.BUG_REPORT,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREY_700,
        )
    )

    # Add all components to the page
    page.add(
        header,
        ft.Card(
            content=ft.Column([
                tab_bar,
                tab_content,
                ft.Row([debug_btn], alignment=ft.MainAxisAlignment.END)
            ]),
            elevation=5,
            expand=True,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
