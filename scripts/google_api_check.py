import os
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Load environment variables from the project root .env
load_dotenv()

console = Console()


def check_google_api():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        console.print(
            "[bold red]❌ Error:[/bold red] GEMINI_API_KEY not found in .env file."
        )
        return

    console.print(
        Panel(
            "[bold cyan]G777 Google API Health Checker[/bold cyan]\n"
            "[dim]Mission O-01 | CNS Squad Constitution Adherent[/dim]",
            border_style="blue",
        ),
        justify="center",
    )

    # API Definitions and Health Check Endpoints
    # We test endpoints that give clear indicators of key validity and service enablement
    apis = [
        {
            "name": "Generative Language API",
            "endpoint": f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
            "method": "GET",
            "critical": True,
        },
        {
            "name": "Places API (New)",
            "endpoint": f"https://places.googleapis.com/v1/places:searchNearby?key={api_key}",
            "method": "POST",
            "headers": {
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": "places.displayName",
            },
            "json": {
                "locationRestriction": {
                    "circle": {
                        "center": {"latitude": 37.7937, "longitude": -122.3965},
                        "radius": 500.0,
                    }
                }
            },
            "critical": True,
        },
        {
            "name": "Custom Search API",
            "endpoint": f"https://www.googleapis.com/customsearch/v1?key={api_key}&q=test&cx=test",
            "method": "GET",
            "critical": True,
        },
        {
            "name": "YouTube Data API v3",
            "endpoint": f"https://www.googleapis.com/youtube/v3/videos?part=id&id=Ks-_Mh1QhMc&key={api_key}",
            "method": "GET",
            "critical": False,
        },
        {
            "name": "Workflows API",
            "endpoint": f"https://workflowexecutions.googleapis.com/v1/projects/health-check/locations/us-central1/workflows?key={api_key}",
            "method": "GET",
            "critical": False,
        },
        {
            "name": "Cloud Storage API",
            "endpoint": f"https://storage.googleapis.com/storage/v1/b?project=health-check&key={api_key}",
            "method": "GET",
            "critical": False,
        },
    ]

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Service Name", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Details", style="dim")

    for api in apis:
        try:
            if api["method"] == "GET":
                response = requests.get(api["endpoint"], timeout=10)
            else:
                response = requests.post(
                    api["endpoint"],
                    json=api.get("json", {}),
                    headers=api.get("headers", {}),
                    timeout=10,
                )

            status_code = response.status_code
            try:
                data = response.json()
                error_reason = data.get("error", {}).get("status", "")
                message = data.get("error", {}).get("message", "")
            except Exception:
                data = {}
                error_reason = "NON_JSON_RESPONSE"
                message = response.text[:100]

            # Logic to determine health based on typical Google API responses
            if status_code == 200:
                status = "[bold green]✅ Active[/bold green]"
                details = "Functional"
            elif status_code == 403:
                if (
                    "PERMISSION_DENIED" in error_reason
                    or "restricted" in message.lower()
                ):
                    status = "[bold yellow]⚠️ Restricted[/bold yellow]"
                    details = f"Restriction Error: {message[:40]}"
                elif (
                    "API_KEY_SERVICE_BLOCKED" in error_reason
                    or "not enabled" in message.lower()
                ):
                    status = "[bold red]🚫 Disabled[/bold red]"
                    details = "API not enabled in Google Cloud Console."
                else:
                    status = "[bold red]❌ Denied[/bold red]"
                    details = message[:60]
            elif status_code == 400:
                # Custom Search might return 400 if CX is invalid, but 200/403 tells us about the key
                if "API key not valid" in message:
                    status = "[bold red]❌ Invalid Key[/bold red]"
                    details = "The API key is incorrect."
                else:
                    # If we get a 400 but it's about params (like invalid project ID),
                    # it usually means the Key itself was accepted and the API is enabled.
                    status = "[bold green]✅ Active[/bold green]"
                    details = "Functional (Parameter mismatch expected)"
            elif status_code == 404:
                status = "[bold green]✅ Active[/bold green]"
                details = "Endpoint reached (Resource not found)"
            else:
                status = f"[bold red]❓ Error {status_code}[/bold red]"
                details = message[:60]

            table.add_row(api["name"], status, details)

        except Exception as e:
            table.add_row(api["name"], "[bold red]💥 Failed[/bold red]", str(e)[:60])

    console.print(table)
    console.print("\n[bold cyan]Audit Checklist Verification:[/bold cyan]")
    console.print(
        "1. [dim]Generative Language API[/dim] -> [bold red]Required[/bold red]"
    )
    console.print(
        "2. [dim]Places API (New)[/dim]       -> [bold red]Required[/bold red]"
    )
    console.print(
        "3. [dim]Custom Search API[/dim]     -> [bold red]Required[/bold red]"
    )
    console.print(
        "\n[italic yellow]Tip: Ensure all Required services show 'Active' for production stability.[/italic yellow]"
    )


if __name__ == "__main__":
    check_google_api()
