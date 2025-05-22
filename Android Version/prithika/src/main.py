import flet as ft
import random
import os
import pandas as pd
import polars as pl
import plotly.express as px
import io
import base64
from datetime import datetime

def main(page: ft.Page):
    # Page setup
    page.title = "Rock Paper Scissors Game"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.BLUE_GREY_50
    
    # Excel file path
    excel_file = os.path.join(os.path.dirname(__file__), "rps_data.xlsx")
    
    # Game state variables
    user_score = 0
    computer_score = 0
    choices = ["rock", "paper", "scissors"]
    current_view = "dashboard"  # Changed default view to dashboard
    username = "Prithika"  # Add username
    
    # Create references properly
    score_text_ref = ft.Ref[ft.Text]()
    status_message_ref = ft.Ref[ft.Text]()
    user_choice_text_ref = ft.Ref[ft.Text]()
    computer_choice_text_ref = ft.Ref[ft.Text]()
    stats_content_ref = ft.Ref[ft.Column]()
    history_table_ref = ft.Ref[ft.DataTable]()
    content_area_ref = ft.Ref[ft.Container]()
    dashboard_content_ref = ft.Ref[ft.Column]()  # Add new reference for dashboard content
    
    # Create logo for sidebar - Added this definition
    logo_container = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Icon(
                    ft.Icons.SPORTS_ESPORTS,
                    size=50,
                    color=ft.Colors.BLUE_700,
                ),
                padding=10,
                border_radius=50,
                bgcolor=ft.Colors.BLUE_50,
            ),
            ft.Text("RPS Game", size=18, weight=ft.FontWeight.BOLD),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
        margin=ft.margin.only(bottom=30, top=20),
    )
    
    # Initialize Excel file if it doesn't exist
    def init_excel_file():
        if not os.path.exists(excel_file):
            # Create game history sheet
            history_df = pd.DataFrame(columns=["timestamp", "user_choice", "computer_choice", "result"])
            # Create game stats sheet
            stats_df = pd.DataFrame({
                "metric": ["user_wins", "computer_wins", "ties", "total_games"],
                "value": [0, 0, 0, 0]
            })
            
            # Save to Excel with multiple sheets
            with pd.ExcelWriter(excel_file) as writer:
                history_df.to_excel(writer, sheet_name="history", index=False)
                stats_df.to_excel(writer, sheet_name="stats", index=False)

    # Game logic functions
    def determine_winner(user_pick, computer_pick):
        nonlocal user_score, computer_score
        
        if user_pick == computer_pick:
            return "It's a tie!"
        
        if (user_pick == "rock" and computer_pick == "scissors") or \
           (user_pick == "paper" and computer_pick == "rock") or \
           (user_pick == "scissors" and computer_pick == "paper"):
            user_score += 1
            return "You win!"
        else:
            computer_score += 1
            return "Computer wins!"
    
    # Save game result to Excel
    def save_game_result(user_choice, computer_choice, result):
        # Read existing data
        try:
            history_df = pd.read_excel(excel_file, sheet_name="history")
            stats_df = pd.read_excel(excel_file, sheet_name="stats")
        except:
            init_excel_file()
            history_df = pd.DataFrame(columns=["timestamp", "user_choice", "computer_choice", "result"])
            stats_df = pd.DataFrame({
                "metric": ["user_wins", "computer_wins", "ties", "total_games"],
                "value": [0, 0, 0, 0]
            })
        
        # Add new game to history
        new_game = pd.DataFrame({
            "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "user_choice": [user_choice],
            "computer_choice": [computer_choice],
            "result": [result]
        })
        history_df = pd.concat([history_df, new_game], ignore_index=True)
        
        # Update stats
        stats_df.loc[stats_df["metric"] == "total_games", "value"] += 1
        
        if result == "You win!":
            stats_df.loc[stats_df["metric"] == "user_wins", "value"] += 1
        elif result == "Computer wins!":
            stats_df.loc[stats_df["metric"] == "computer_wins", "value"] += 1
        else:  # Tie
            stats_df.loc[stats_df["metric"] == "ties", "value"] += 1
        
        # Save updated data
        with pd.ExcelWriter(excel_file) as writer:
            history_df.to_excel(writer, sheet_name="history", index=False)
            stats_df.to_excel(writer, sheet_name="stats", index=False)
            
        # Update stats page if it's currently displayed
        if current_view == "stats":
            update_stats_view()

    # Button click handler
    def handle_choice(e, choice):
        # Get computer's choice
        computer_choice = random.choice(choices)
        
        # Update choice displays
        user_choice_text_ref.current.value = f"Your choice: {choice.capitalize()}"
        computer_choice_text_ref.current.value = f"Computer's choice: {computer_choice.capitalize()}"
        
        # Determine winner and update score
        result = determine_winner(choice, computer_choice)
        status_message_ref.current.value = result
        score_text_ref.current.value = f"You: {user_score}  |  Computer: {computer_score}"
        
        # Save to Excel
        save_game_result(choice, computer_choice, result)
        
        # Update UI
        page.update()
    
    # Reset game function
    def reset_game(e):
        nonlocal user_score, computer_score
        user_score = computer_score = 0
        
        score_text_ref.current.value = f"You: {user_score}  |  Computer: {computer_score}"
        status_message_ref.current.value = "Choose your move!"
        user_choice_text_ref.current.value = "Your choice: "
        computer_choice_text_ref.current.value = "Computer's choice: "
        page.update()
    
    # Update stats view function
    def update_stats_view():
        try:
            # Get reference to stats content
            stats_content = stats_content_ref.current
            stats_content.controls.clear()
            
            # Read stats from Excel using polars
            # Check if file exists first
            if not os.path.exists(excel_file):
                init_excel_file()
                
            stats_df = pl.read_excel(excel_file, sheet_name="stats")
            history_df = pl.read_excel(excel_file, sheet_name="history")
            
            # Extract metrics
            metrics = stats_df.to_dict(as_series=False)
            total_games = metrics["value"][metrics["metric"].index("total_games")]
            user_wins = metrics["value"][metrics["metric"].index("user_wins")]
            computer_wins = metrics["value"][metrics["metric"].index("computer_wins")]
            ties = metrics["value"][metrics["metric"].index("ties")]
            
            # Add summary text
            stats_content.controls.append(
                ft.Text(f"Total Games: {total_games}", size=24, weight=ft.FontWeight.BOLD)
            )
            stats_content.controls.append(
                ft.Text(f"Your Wins: {user_wins} ({user_wins/total_games*100:.1f}% win rate)" if total_games > 0 else "Your Wins: 0", 
                       size=20, color=ft.Colors.GREEN)
            )
            stats_content.controls.append(
                ft.Text(f"Computer Wins: {computer_wins} ({computer_wins/total_games*100:.1f}% win rate)" if total_games > 0 else "Computer Wins: 0", 
                       size=20, color=ft.Colors.RED)
            )
            stats_content.controls.append(
                ft.Text(f"Ties: {ties} ({ties/total_games*100:.1f}% tie rate)" if total_games > 0 else "Ties: 0", 
                       size=20, color=ft.Colors.BLUE)
            )
            
            # Only create visualizations if there's data
            if total_games > 0:
                # Create pie chart data for win distribution
                pie_data = {"Category": ["You", "Computer", "Ties"], 
                           "Count": [user_wins, computer_wins, ties]}
                pie_df = pd.DataFrame(pie_data)
                
                # Add win distribution chart
                stats_content.controls.append(
                    ft.Text("Win Distribution", size=22, weight=ft.FontWeight.W_500, 
                           text_align=ft.TextAlign.CENTER)
                )
                
                # Add pie chart container
                win_chart = ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(f"You: {user_wins}", color=ft.Colors.GREEN, size=16),
                            padding=10,
                            bgcolor=ft.Colors.GREEN_50,
                            border_radius=5,
                            width=120,
                        ),
                        ft.Container(
                            content=ft.Text(f"Computer: {computer_wins}", color=ft.Colors.RED, size=16),
                            padding=10,
                            bgcolor=ft.Colors.RED_50,
                            border_radius=5,
                            width=120,
                        ),
                        ft.Container(
                            content=ft.Text(f"Ties: {ties}", color=ft.Colors.BLUE, size=16),
                            padding=10,
                            bgcolor=ft.Colors.BLUE_50,
                            border_radius=5,
                            width=120,
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                    margin=ft.margin.only(top=10, bottom=20),
                )
                stats_content.controls.append(win_chart)
                
                # Create win percentage by choice chart if enough data
                if total_games >= 5 and len(history_df) > 0:
                    # Add choice analysis header
                    stats_content.controls.append(
                        ft.Text("Performance by Choice", size=22, weight=ft.FontWeight.W_500,
                               text_align=ft.TextAlign.CENTER)
                    )
                    
                    # Process data for each choice
                    choice_stats = {}
                    for choice in choices:
                        # Filter games with this choice
                        choice_games = history_df.filter(pl.col("user_choice") == choice)
                        if len(choice_games) > 0:
                            # Calculate wins
                            choice_wins = choice_games.filter(pl.col("result") == "You win!").height
                            win_rate = (choice_wins / len(choice_games)) * 100
                            choice_stats[choice] = {
                                "total": len(choice_games),
                                "wins": choice_wins,
                                "win_rate": win_rate
                            }
                    
                    # Create choice performance chart
                    choice_chart = ft.Row(
                        [
                            ft.Container(
                                content=ft.Column([
                                    ft.Icon(ft.Icons.CIRCLE, size=40, color=ft.Colors.BLUE_700),
                                    ft.Text("Rock", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{choice_stats.get('rock', {}).get('total', 0)} games", size=14),
                                    ft.Text(f"{choice_stats.get('rock', {}).get('win_rate', 0):.1f}% wins", 
                                           size=16, 
                                           color=ft.Colors.GREEN if choice_stats.get('rock', {}).get('win_rate', 0) > 50 else ft.Colors.RED),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                                padding=15,
                                bgcolor=ft.Colors.BLUE_GREY_50,
                                border_radius=10,
                                width=150,
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Icon(ft.Icons.SQUARE_OUTLINED, size=40, color=ft.Colors.TEAL_700),
                                    ft.Text("Paper", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{choice_stats.get('paper', {}).get('total', 0)} games", size=14),
                                    ft.Text(f"{choice_stats.get('paper', {}).get('win_rate', 0):.1f}% wins", 
                                           size=16, 
                                           color=ft.Colors.GREEN if choice_stats.get('paper', {}).get('win_rate', 0) > 50 else ft.Colors.RED),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                                padding=15,
                                bgcolor=ft.Colors.BLUE_GREY_50,
                                border_radius=10,
                                width=150,
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Icon(ft.Icons.CONTENT_CUT, size=40, color=ft.Colors.PURPLE_700),
                                    ft.Text("Scissors", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{choice_stats.get('scissors', {}).get('total', 0)} games", size=14),
                                    ft.Text(f"{choice_stats.get('scissors', {}).get('win_rate', 0):.1f}% wins", 
                                           size=16, 
                                           color=ft.Colors.GREEN if choice_stats.get('scissors', {}).get('win_rate', 0) > 50 else ft.Colors.RED),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                                padding=15,
                                bgcolor=ft.Colors.BLUE_GREY_50,
                                border_radius=10,
                                width=150,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=15,
                    )
                    stats_content.controls.append(choice_chart)
            
            page.update()
        except Exception as e:
            print(f"Error updating stats: {e}")
            stats_content_ref.current.controls.clear()
            stats_content_ref.current.controls.append(ft.Text(f"Error loading statistics: {str(e)}"))
            page.update()
    
    # Update history view function
    def update_history_view():
        try:
            # Get reference to history table
            history_table = history_table_ref.current
            history_table.rows.clear()
            
            # Read history from Excel
            if os.path.exists(excel_file):
                history_df = pd.read_excel(excel_file, sheet_name="history")
                
                # Add rows to table (most recent first)
                for idx, row in history_df.iloc[::-1].iterrows():
                    history_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(row["timestamp"])),
                                ft.DataCell(ft.Text(row["user_choice"].capitalize())),
                                ft.DataCell(ft.Text(row["computer_choice"].capitalize())),
                                ft.DataCell(ft.Text(row["result"]))
                            ]
                        )
                    )
            
            page.update()
        except Exception as e:
            print(f"Error updating history: {e}")
            history_table_ref.current.rows.append(
                ft.DataRow(
                    cells=[ft.DataCell(ft.Text(f"Error loading history: {str(e)}"))]
                )
            )
            page.update()
    
    # Tab navigation function
    def change_tab(e):
        nonlocal current_view
        selected_tab = e.control.selected_index
        
        if selected_tab == 0:  # Dashboard tab
            current_view = "dashboard"
            content_area_ref.current.content = dashboard_view
            update_dashboard_view()
        elif selected_tab == 1:  # Game tab
            current_view = "game"
            content_area_ref.current.content = game_view
        elif selected_tab == 2:  # Stats tab
            current_view = "stats"
            content_area_ref.current.content = stats_view
            update_stats_view()
        elif selected_tab == 3:  # History tab
            current_view = "history"
            content_area_ref.current.content = history_view
            update_history_view()
        
        page.update()
    
    # Get time-based greeting
    def get_greeting():
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            return "Good morning"
        elif 12 <= current_hour < 17:
            return "Good afternoon"
        elif 17 <= current_hour < 21:
            return "Good evening"
        else:
            return "Good night"
    
    # Update dashboard view function
    def update_dashboard_view():
        try:
            # Get reference to dashboard content
            dashboard_content = dashboard_content_ref.current
            dashboard_content.controls.clear()
            
            # Update greeting based on time
            greeting = get_greeting()
            
            # Add welcome card
            welcome_card = ft.Card(
                content=ft.Container(
                    width=1600,expand=True,
                    content=ft.Column([
                        ft.Text(f"{greeting}, {username}!", 
                               size=28, 
                               weight=ft.FontWeight.BOLD,
                               color=ft.Colors.BLUE_700),
                        ft.Text(f"Welcome to your Rock Paper Scissors dashboard",
                               size=16,
                               color=ft.Colors.BLUE_GREY_800),
                        ft.Text(f"Today: {datetime.now().strftime('%A, %B %d, %Y')}",
                               size=14,
                               color=ft.Colors.BLUE_GREY_600),
                    ]),
                    padding=20,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                        colors=[ft.Colors.BLUE_50, ft.Colors.INDIGO_50],
                    ),
                ),
                elevation=4,
                margin=ft.margin.only(bottom=25, top=10),
            )
            dashboard_content.controls.append(welcome_card)
            
            # Check if we have game data to show
            if not os.path.exists(excel_file):
                init_excel_file()
                
            stats_df = pl.read_excel(excel_file, sheet_name="stats")
            history_df = pl.read_excel(excel_file, sheet_name="history")
            
            # Extract metrics more safely
            metrics = stats_df.to_dict(as_series=False)
            
            # Handle case when DataFrame might be empty
            if "metric" not in metrics or "value" not in metrics or len(metrics["metric"]) == 0:
                total_games = 0
                user_wins = 0
                computer_wins = 0
                ties = 0
            else:
                # Find indices safely with default values
                total_games_idx = metrics["metric"].index("total_games") if "total_games" in metrics["metric"] else 0
                user_wins_idx = metrics["metric"].index("user_wins") if "user_wins" in metrics["metric"] else 0
                computer_wins_idx = metrics["metric"].index("computer_wins") if "computer_wins" in metrics["metric"] else 0
                ties_idx = metrics["metric"].index("ties") if "ties" in metrics["metric"] else 0
                
                total_games = metrics["value"][total_games_idx]
                user_wins = metrics["value"][user_wins_idx]
                computer_wins = metrics["value"][computer_wins_idx]
                ties = metrics["value"][ties_idx]
            
            # Add quick stats cards
            dashboard_content.controls.append(
                ft.Text("Game Overview", size=20, weight=ft.FontWeight.W_600)
            )
            
            # Stats cards row
            stats_row = ft.Row(
                controls=[
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("Total Games", size=16, color=ft.Colors.BLUE_GREY_700),
                                ft.Text(f"{total_games}", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=15,
                            width=150,
                            height=120,
                        ),
                        elevation=3,
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("Win Rate", size=16, color=ft.Colors.BLUE_GREY_700),
                                ft.Text(f"{(user_wins/total_games*100):.1f}%" if total_games > 0 else "0%", 
                                      size=32, 
                                      weight=ft.FontWeight.BOLD, 
                                      color=ft.Colors.GREEN),
                            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=15,
                            width=150,
                            height=120,
                        ),
                        elevation=3,
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("Best Choice", size=16, color=ft.Colors.BLUE_GREY_700),
                                ft.Text(get_best_choice(history_df) if total_games > 5 else "Play more!",
                                      size=22 if total_games > 5 else 18, 
                                      weight=ft.FontWeight.BOLD, 
                                      color=ft.Colors.BLUE_700),
                            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=15,
                            width=150,
                            height=120,
                        ),
                        elevation=3,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            )
            dashboard_content.controls.append(stats_row)
            
            # Add recent games section if there are games
            if total_games > 0:
                dashboard_content.controls.append(
                    ft.Container(height=30)  # Spacer
                )
                dashboard_content.controls.append(
                    ft.Text("Recent Activity", size=20, weight=ft.FontWeight.W_600)
                )
                
                # Recent games list
                recent_games = ft.ListView(
                    height=180,
                    spacing=2,
                    padding=10,
                    divider_thickness=1,
                )
                
                # Get the most recent 5 games - use a safer approach
                recent_history = history_df.head(min(5, len(history_df)))
                
                for row in recent_history.iter_rows(named=True):
                    # Process each row safely
                    user_choice = row.get("user_choice", "unknown")
                    computer_choice = row.get("computer_choice", "unknown")
                    result = row.get("result", "unknown")
                    
                    # Determine icon based on user choice
                    if user_choice == "rock":
                        icon = ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.BLUE_700, size=20)
                    elif user_choice == "paper":
                        icon = ft.Icon(ft.Icons.SQUARE_OUTLINED, color=ft.Colors.TEAL_700, size=20)
                    else:  # scissors or unknown
                        icon = ft.Icon(ft.Icons.CONTENT_CUT, color=ft.Colors.PURPLE_700, size=20)
                    
                    # Determine result color
                    if result == "You win!":
                        result_color = ft.Colors.GREEN
                    elif result == "Computer wins!":
                        result_color = ft.Colors.RED
                    else:
                        result_color = ft.Colors.BLUE
                    
                    # Add to recent games list
                    recent_games.controls.append(
                        ft.Container(
                            content=ft.Row([
                                icon,
                                ft.Text(f"{user_choice.capitalize()} vs {computer_choice.capitalize()}", 
                                      expand=True),
                                ft.Text(result, color=result_color),
                            ]),
                            padding=ft.padding.symmetric(vertical=8, horizontal=15),
                            border_radius=5,
                            bgcolor=ft.Colors.WHITE,
                        )
                    )
                
                dashboard_content.controls.append(
                    ft.Container(
                        content=recent_games,
                        border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
                        border_radius=10,
                        padding=ft.padding.only(top=10, bottom=10),
                        margin=ft.margin.only(bottom=20),
                    )
                )
                
                # Add trend analysis if enough games
                if total_games >= 10:
                    dashboard_content.controls.append(
                        ft.Text("Performance Trend", size=20, weight=ft.FontWeight.W_600)
                    )
                    
                    # Create a visual trend indicator
                    trend_container = create_trend_visualization(history_df)
                    dashboard_content.controls.append(trend_container)
            
            page.update()
        except Exception as e:
            print(f"Error updating dashboard: {e}")
            import traceback
            traceback.print_exc()  # Add detailed error logging
            dashboard_content_ref.current.controls.clear()
            dashboard_content_ref.current.controls.append(
                ft.Text(f"Error loading dashboard: {str(e)}")
            )
            page.update()
    
    # Helper function to get the best choice based on win rate
    def get_best_choice(history_df):
        if len(history_df) == 0:
            return "N/A"
        
        choice_stats = {}
        for choice in choices:
            choice_games = history_df.filter(pl.col("user_choice") == choice)
            if len(choice_games) > 0:
                wins = choice_games.filter(pl.col("result") == "You win!").height
                win_rate = (wins / len(choice_games)) * 100
                choice_stats[choice] = win_rate
        
        if not choice_stats:
            return "Play more!"
            
        # Get the choice with highest win rate
        best_choice = max(choice_stats.items(), key=lambda x: x[1])
        return f"{best_choice[0].capitalize()}"
    
    # Helper function to create trend visualization
    def create_trend_visualization(history_df):
        # Transform data to get cumulative win rate over time
        wins = []
        current_wins = 0
        total = 0
        win_rates = []
        
        # Process each game and calculate running win rate
        for idx, row in history_df.iter_rows(named=True):
            total += 1
            if row["result"] == "You win!":
                current_wins += 1
            win_rate = (current_wins / total) * 100
            win_rates.append(win_rate)
        
        # Create a simplified trend visualization
        trend_container = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                bgcolor=ft.Colors.BLUE_200 if i < len(win_rates) else ft.Colors.GREY_300,
                                height=max(5, min(70, win_rates[i] if i < len(win_rates) else 0)),
                                width=10,
                                border_radius=ft.border_radius.only(top_left=5, top_right=5),
                                tooltip=f"{win_rates[i]:.1f}%" if i < len(win_rates) else "No data",
                            ) for i in range(min(15, total))
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                        padding=10,
                    ),
                    ft.Text("Game History Trend (Win Rate %)", size=14, color=ft.Colors.BLUE_GREY_600),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ], alignment=ft.MainAxisAlignment.CENTER),
            margin=ft.margin.only(bottom=20, top=10),
        )
        
        return trend_container
    
    # Create a function to create header with user icon for all tabs
    def create_tab_header(title):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        title,
                        size=32, 
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_700,
                    ),
                    ft.Container(width=20),  # Spacer
                    ft.Container(
                        content=ft.PopupMenuButton(
                            icon=ft.Icons.ACCOUNT_CIRCLE,
                            icon_size=36,
                            icon_color=ft.Colors.BLUE_700,
                            tooltip="User Options",
                            items=[
                                ft.PopupMenuItem(
                                    text="My Profile",
                                    icon=ft.Icons.PERSON,
                                    on_click=lambda _: show_profile_dialog(page)
                                ),
                                ft.PopupMenuItem(
                                    text="Logout",
                                    icon=ft.Icons.LOGOUT,
                                    on_click=lambda _: show_logout_snackbar(page)
                                ),
                            ],
                        ),
                        alignment=ft.alignment.center_right,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(left=15, right=15, top=15, bottom=5),
            border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
            bgcolor=ft.Colors.BLUE_50,
            width=float("inf"),
            border=ft.border.only(bottom=ft.BorderSide(3, ft.Colors.BLUE_200)),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                offset=ft.Offset(0, 3),
            )
        )
    
    # Add functions to handle menu item clicks
    def show_profile_dialog(page):
        # Create profile dialog
        profile_dialog = ft.AlertDialog(
            title=ft.Text("User Profile", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Container(
                    content=ft.CircleAvatar(
                        content=ft.Icon(ft.Icons.PERSON, size=40),
                        radius=40,
                        bgcolor=ft.Colors.BLUE_100,
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=20),
                ),
                ft.Text("Username: Player1", size=16),
                ft.Text("Games Played: Coming soon", size=16),
                ft.Text("Win Rate: Coming soon", size=16),
            ], tight=True, spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("Close", on_click=lambda _: close_dialog(page))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Show the dialog
        page.dialog = profile_dialog
        profile_dialog.open = True
        page.update()
        
    def close_dialog(page):
        # Close the dialog
        page.dialog.open = False
        page.update()
    
    def show_logout_snackbar(page):
        # Display logout message
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Logout feature coming soon!"),
            action="OK",
        )
        page.snack_bar.open = True
        page.update()
    
    # Dashboard view
    dashboard_view = ft.Container(
        content=ft.Column(
            [
                # Add header with user icon
                create_tab_header("DASHBOARD"),
                
                # Content container
                ft.Container(
                    content=ft.Column([], ref=dashboard_content_ref),
                    padding=ft.padding.all(20),
                    expand=True,
                )
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=0,
        expand=True
    )
    
    # Stats view
    stats_view = ft.Container(
        content=ft.Column(
            [
                # Add header with user icon
                create_tab_header("GAME STATISTICS"),
                
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                content=ft.Column([], ref=stats_content_ref),
                                expand=True
                            )
                        ],
                        spacing=20,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=ft.padding.all(20),
                    expand=True
                )
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=0,
        expand=True
    )
    
    # History view
    history_view = ft.Container(
        content=ft.Column(
            [
                # Add header with user icon
                create_tab_header("GAME HISTORY"),
                
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                content=ft.DataTable(
                                    ref=history_table_ref,
                                    columns=[
                                        ft.DataColumn(ft.Text("Time")),
                                        ft.DataColumn(ft.Text("Your Choice")),
                                        ft.DataColumn(ft.Text("Computer's Choice")),
                                        ft.DataColumn(ft.Text("Result"))
                                    ],
                                    rows=[]
                                ),
                                expand=True
                            )
                        ],
                        spacing=20,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=ft.padding.all(20),
                    expand=True
                )
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=0,
        expand=True
    )
    
    # Game content area
    game_view = ft.Container(
        content=ft.Column(
            [
                # Add header with user icon
                create_tab_header("ROCK PAPER SCISSORS"),
                
                # Content container
                ft.Container(
                    content=ft.Column(
                        [
                            # Score display
                            ft.Container(
                                content=ft.Text(f"You: {user_score}  |  Computer: {computer_score}", 
                                            size=24, 
                                            weight=ft.FontWeight.W_500,
                                            color=ft.Colors.BLUE_800,
                                            ref=score_text_ref),
                                alignment=ft.alignment.center,
                                margin=ft.margin.only(bottom=30, top=20)
                            ),
                            
                            # Game status message
                            ft.Container(
                                content=ft.Text("Choose your move!",
                                            size=20, 
                                            color=ft.Colors.BLACK87,
                                            text_align=ft.TextAlign.CENTER,
                                            ref=status_message_ref),
                                alignment=ft.alignment.center,
                                margin=ft.margin.symmetric(vertical=15),
                                height=50
                            ),
                            
                            # Choice display
                            ft.Row(
                                controls=[
                                    ft.Column(
                                        [ft.Text("Your choice: ", size=18, ref=user_choice_text_ref)],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        expand=True
                                    ),
                                    ft.Column(
                                        [ft.Text("Computer's choice: ", size=18, ref=computer_choice_text_ref)],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        expand=True
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.CENTER
                            ),
                            
                            ft.Container(height=30),  # Spacer
                            
                            # Button row
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.CIRCLE),
                                            ft.Text("Rock", size=16)
                                        ], alignment=ft.MainAxisAlignment.CENTER),
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=10),
                                            padding=15
                                        ),
                                        on_click=lambda e: handle_choice(e, "rock"),
                                        width=150,
                                        height=60
                                    ),
                                    ft.ElevatedButton(
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.SQUARE_OUTLINED),
                                            ft.Text("Paper", size=16)
                                        ], alignment=ft.MainAxisAlignment.CENTER),
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=10),
                                            padding=15
                                        ),
                                        on_click=lambda e: handle_choice(e, "paper"),
                                        width=150,
                                        height=60
                                    ),
                                    ft.ElevatedButton(
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.CONTENT_CUT),
                                            ft.Text("Scissors", size=16)
                                        ], alignment=ft.MainAxisAlignment.CENTER),
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=10),
                                            padding=15
                                        ),
                                        on_click=lambda e: handle_choice(e, "scissors"),
                                        width=150,
                                        height=60
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=20
                            ),
                            
                            ft.Container(height=30),  # Spacer
                            
                            # Reset button
                            ft.Row(
                                [
                                    ft.OutlinedButton(
                                        "Reset Game",
                                        icon=ft.Icons.REFRESH,
                                        on_click=reset_game
                                    )
                                ], 
                                alignment=ft.MainAxisAlignment.CENTER
                            )
                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(20),
                    expand=True,
                )
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=0,
        expand=True
    )
    
    # Define the content area container properly
    content_area = ft.Container(
        content=dashboard_view,  # Default to dashboard view
        expand=True,
        ref=content_area_ref
    )
    
    # Fix the sidebar definition to include all necessary properties
    sidebar = ft.NavigationRail(
        selected_index=0,  # Default to Dashboard tab
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=150,
        min_extended_width=250,
        group_alignment=-0.9,
        leading=logo_container,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD,
                selected_icon=ft.Icons.DASHBOARD,
                label="Dashboard",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SPORTS_ESPORTS,
                selected_icon=ft.Icons.SPORTS_ESPORTS,
                label="Game",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.BAR_CHART,
                selected_icon=ft.Icons.BAR_CHART,
                label="Stats",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.HISTORY,
                selected_icon=ft.Icons.HISTORY,
                label="History",
            ),
        ],
        on_change=change_tab,
    )
    
    # Initialize the dashboard view first
    update_dashboard_view()
    
    # Main layout with sidebar and content
    page.add(
        ft.Row(
            [
                sidebar,
                ft.VerticalDivider(width=1),
                content_area,
            ],
            expand=True,
        )
    )

ft.app(target=main)