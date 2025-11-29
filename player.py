from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, Input
from textual.containers import Container, Grid
from textual.screen import Screen
from textual import events
import subprocess
import yt_dlp  

class QuitScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Static("Are you sure you want to quit?", id="question"),
            Button("Yes", variant="error", id="yes"),
            Button("No", variant="primary", id="no"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.app.exit()
        else:
            self.app.pop_screen()
            
    def on_key(self, event: events.Key) -> None:
        if event.key.lower() in ("y", "q", "escape"):
            self.app.exit()
        elif event.key.lower() == "n":
            self.app.pop_screen()


class YouTubePlayerScreen(Screen):
    BINDINGS = [
        ("q", "request_quit", "Quit"),
        ("d", "toggle_dark", "Dark Mode"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        
        with Container(id="main-container"):
            
            yield Static(
                "[red]" + "[center]" +
                """
                                    ⠀⠀⢀⣀⣠⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣄⣀⡀⠀⠀
                                    ⠀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠀
                                    ⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀
                                    ⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆
                                    ⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠈⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
                                    ⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⢈⣹⣿⣿⣿⣿⣿⣿⣿⡇
                                    ⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⢀⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
                                    ⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇
                                    ⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀
                                    ⠀⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠀
                                    ⠀⠀⠈⠉⠙⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠋⠉⠁⠀⠀
                """ +
                "[/center]" + "[/red]",
                id="logo",
            )
                    
            yield Static(
                f"[bold white on blue]YouTube Audio Player TUI[/bold white on blue]\n\n"
                f"Enter a YouTube link below and press ENTER to start playback.\n\n"
                f"Press ESC to stop MPV playback.", 
                id="display-box-static"
            )

            yield Input(
                placeholder="Paste the YouTube link here...", 
                id="input-link"
            )
    
    def action_request_quit(self) -> None:
        self.app.push_screen(QuitScreen())
    
    def action_toggle_dark(self) -> None:
        self.app.dark = not self.app.dark


    def play_video(self, url: str, display_box: Static) -> None:
        
        display_box.update(f"[yellow]Status:[/yellow] Extracting stream URL with yt-dlp...\n[i]Link: {url}[/i]")
        
        try:
            ydl_opts = {
                'format': 'bestaudio/best', 
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                stream_url = info.get('url')
                title = info.get('title', 'Unknown Video')
            
            if not stream_url:
                raise ValueError("Stream URL could not be extracted.")
            
        except Exception as e:
            display_box.update(
                f"[bold red]Extraction ERROR:[/bold red] Failed to retrieve audio stream URL.\n"
                f"Details: {type(e).__name__}: {str(e)}\n"
                f"[i]Ensure the video is public and the link is valid.[/i]"
            )
            return

        
        display_box.update(
            f"[bold green]Status: Playing![/bold green]\n"
            f"Title: [bold white]{title}[/bold white]\n"
            f"[i]Playback is now running in the background. Press ESC to stop the player.[/i]"
        )

        with self.app.suspend():
            try:
                process = subprocess.run(["mpv", "--vo=tct", url])
                
                if process.returncode == 0:
                    display_box.update(
                        f"[bold green]Playback Complete![/bold green]\n"
                        f"Status: Finished successfully.\n\n"
                        f"[i]Enter a new link or press Q to quit.[/i]"
                    )
                else:
                     error_output = (process.stderr.strip() or process.stdout.strip() or 'No detailed error reported.')
                     
                     if process.returncode == 2:
                        status_message = "[bold yellow]Playback Stopped[/bold yellow]\nStatus: User interrupted playback (Code 2).\n"
                     else:
                        status_message = f"[bold red]Playback Error[/bold red]\nStatus: Player exit with non-zero code ({process.returncode}).\nError Details: {error_output}\n"

                     display_box.update(
                        f"{status_message}\n"
                        f"[i]Enter a new link or press Q to quit.[/i]"
                    )


            except FileNotFoundError:
                display_box.update(
                    f"[bold red]FATAL ERROR: MPV Player not found![/bold red]\n"
                    f"Ensure that 'mpv' is installed and available in your system PATH."
                )
            except Exception as e:
                display_box.update(
                    f"[bold red]Unknown ERROR:[/bold red] {type(e).__name__}: {e!r}\n"
                )


    def on_input_submitted(self, message: Input.Submitted) -> None:
        link = message.value.strip()
        input_widget = self.query_one("#input-link", Input)
        display_box = self.query_one("#display-box-static", Static)
        
        if not link:
            display_box.update("[bold red]ERROR:[/bold red] The link field cannot be empty.")
            return

        input_widget.value = "" 
        
        self.play_video(link, display_box)


class YouTubePlayerApp(App):
    
    CSS_PATH = "player.css"
    TITLE = "Textual YouTube Audio Player"
    BINDINGS = [
        ("q", "request_quit", "Quit"),
        ("d", "toggle_dark", "Dark Mode"),
    ]

    def on_mount(self) -> None:
        try:
            self.push_screen(YouTubePlayerScreen())
        except Exception as e:
            print(f"Error initializing app: {e}")
        
    def action_request_quit(self) -> None:
        self.push_screen(QuitScreen())
        
    def action_toggle_dark(self) -> None:
        self.dark = not self.dark


if __name__ == "__main__":
    app = YouTubePlayerApp()
    app.run()