import flet as ft
import random
def main(page: ft.Page):
    page.title = "Rock Paper Scissors"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 500
    page.window_height = 700
    page.padding = 20
    page.bgcolor = ft.Colors.WHITE
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    player_score = 0
    computer_score = 0
    ties = 0
    choices = ["rock", "paper", "scissors"]

    # Header
    title = ft.Text("Rock Paper Scissors", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
    subtitle = ft.Text("Choose your move:", size=16)

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

    # Function to handle game logic
    def play_game(player_choice):
        nonlocal player_score, computer_score, ties
        
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
        if player_choice == computer_choice:
            result_text.value = "It's a tie!"
            result_text.color = ft.Colors.BLUE_500
            ties += 1
        elif ((player_choice == "rock" and computer_choice == "scissors") or
              (player_choice == "paper" and computer_choice == "rock") or
              (player_choice == "scissors" and computer_choice == "paper")):
            result_text.value = "You win!"
            result_text.color = ft.Colors.GREEN_500
            player_score += 1
        else:
            result_text.value = "Computer wins!"
            result_text.color = ft.Colors.RED_500
            computer_score += 1
        
        # Update score
        score_text.value = f"Player: {player_score} - Computer: {computer_score} - Ties: {ties}"
        
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

    # Add all components to the page
    page.add(
        ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        title,
                        ft.Divider(),
                        score_text,
                        ft.Divider(),
                        subtitle,
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
                border_radius=10
            ),
            elevation=5
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
